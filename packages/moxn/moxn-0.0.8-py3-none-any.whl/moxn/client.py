import json
from moxn.telemetry.client import TelemetryClient
from moxn.telemetry.transport import APITelemetryTransport, TelemetryTransportBackend
import logging
from functools import lru_cache
from pathlib import Path

import httpx
from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from moxn.exceptions import MoxnSchemaValidationError
from moxn.models.prompt import Prompt, PromptInstance
from moxn.models.schema import PromptSchemas, SchemaPromptType, CodegenResponse
from moxn.models.task import Task
from moxn.polling import PollingConfig, PollingManager
from moxn.storage.storage import InMemoryStorage
from moxn.base_models.telemetry import (
    SpanEventLogRequest,
    SpanLogRequest,
    TelemetryLogResponse,
    LLMEvent,
)
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Literal, Optional
from uuid import UUID

from moxn.telemetry.context import SpanContext

logger = logging.getLogger(__name__)


class MoxnSettings(BaseSettings):
    """Configuration settings for the Moxn client."""

    user_id: str
    org_id: str | None = None
    api_key: SecretStr
    base_api_route: HttpUrl = Field(default=HttpUrl("https://api.moxn.io/v1"))
    timeout: float = Field(default=60.0, description="Prompt timeout in seconds")

    model_config = SettingsConfigDict(
        frozen=True,
        extra="forbid",
        env_prefix="MOXN_",
        env_file="src/moxn/.env",
        env_file_encoding="utf-8",
    )


class MoxnClient(TelemetryTransportBackend):
    """
    Moxn API client for interacting with the Moxn platform.

    Example:
        ```python
        client = MoxnClient(
            user_id="user123",
            org_id="org456",  # Optional
            api_key="sk-...",
            base_api_route="https://api.moxn.com/v1"
        )
        ```
    Example:
        ```python
        config = PollingConfig(
            interval=3600.0,  # Poll every hour
            versions_to_track={
                "task_123": ["v1", "v2"],
                "task_456": ["v1"],
            }
        )

        async with MoxnClient() as client:
            await client.start_polling(config)
        ```
    """

    def __init__(self) -> None:
        self.settings = MoxnSettings()  # type: ignore
        self._client: httpx.AsyncClient | None = None
        self.storage = InMemoryStorage()
        self._polling_manager: PollingManager | None = None
        self._context_depth = 0  # Track nested context usage

        # Create telemetry components with self as the backend
        transport = APITelemetryTransport(backend=self)
        self.telemetry_client = TelemetryClient(transport=transport)

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, creating it if necessary."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> httpx.AsyncClient:
        """Creates an authenticated httpx client."""
        return httpx.AsyncClient(
            base_url=str(self.settings.base_api_route),
            timeout=self.settings.timeout,
            headers=self.get_headers(),
        )

    @lru_cache(maxsize=1)
    def get_headers(self, salt: bool = True) -> dict:
        """Returns the default headers for API prompts."""
        headers = {
            "x-api-key": self.settings.api_key.get_secret_value(),
            "x-requested-user-id": self.settings.user_id,
        }
        if self.settings.org_id:
            headers["x-requested-org-id"] = self.settings.org_id
        return headers

    async def __aenter__(self) -> "MoxnClient":
        self._context_depth += 1
        if self._client is None:
            self._client = self._create_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._context_depth -= 1
        if self._context_depth == 0:
            await self.stop_polling()
            await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Perform a GET prompt."""
        return await self.client.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """Perform a POST prompt."""
        return await self.client.post(path, **kwargs)

    async def put(self, path: str, **kwargs) -> httpx.Response:
        """Perform a PUT prompt."""
        return await self.client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """Perform a DELETE prompt."""
        return await self.client.delete(path, **kwargs)

    async def start_polling(self, config: PollingConfig) -> None:
        """Start polling for new versions of tasks and prompts."""
        if self._polling_manager is not None:
            await self._polling_manager.stop()

        self._polling_manager = PollingManager(
            config=config,
            fetch_task=self.fetch_task,
            fetch_prompt=self.fetch_prompt,
            store_task=self.storage.store_task,
            store_prompt=self.storage.store_prompt,
            get_last_polled=self.storage.get_last_polled,
            update_last_polled=self.storage.update_last_polled,
        )
        await self._polling_manager.start()

    async def stop_polling(self) -> None:
        """Stop polling for updates."""
        if self._polling_manager:
            await self._polling_manager.stop()
            self._polling_manager = None

    async def fetch_task(self, task_id: str, version_id: str | None = None) -> Task:
        """
        Fetch a task from the API.
        If version_id is None, fetches the latest version.
        """
        params = {}
        if version_id:
            params["version_id"] = version_id

        response = await self.get(f"/tasks/{task_id}", params=params)
        response.raise_for_status()

        return Task.model_validate(response.json())

    async def fetch_prompt(
        self, prompt_id: str, version_id: str | None = None
    ) -> Prompt:
        """
        Fetch a prompt from the API.
        If version_id is None, fetches the latest version.
        """
        params = {}
        if version_id:
            params["version_id"] = version_id

        response = await self.get(f"/prompts/{prompt_id}", params=params)
        response.raise_for_status()

        return Prompt.model_validate(response.json())

    async def get_prompt(self, prompt_id: str, prompt_version_id: str | None) -> Prompt:
        """
        Get a prompt version from storage, fetching from API if not found.
        """
        try:
            return await self.storage.get_prompt(prompt_id, prompt_version_id)
        except KeyError:
            # If not in storage, fetch from API and store
            prompt = await self.fetch_prompt(prompt_id, prompt_version_id)
            await self.storage.store_prompt(prompt)
            return prompt

    async def get_task(self, task_id: str, task_version_id: str | None) -> Task:
        """
        Get a task version from storage, fetching from API if not found.
        """
        try:
            return await self.storage.get_task(task_id, task_version_id)
        except KeyError:
            # If not in storage, fetch from API and store
            task = await self.fetch_task(task_id, task_version_id)
            await self.storage.store_task(task)
            return task

    async def fetch_prompt_schemas(
        self,
        prompt_id: str,
        version_id: str,
        schema_prompt_type: SchemaPromptType = SchemaPromptType.ALL,
    ) -> PromptSchemas:
        """
        Fetch schemas for a specific prompt version.
        Returns PromptSchemas containing SchemaWithMetadata objects.
        """
        params = {"version_id": version_id, "type": schema_prompt_type.value}

        response = await self.get(
            f"/prompts/{prompt_id}/schemas",
            params=params,
            headers=self.get_headers(),
        )

        if response.status_code == 404:
            raise KeyError(f"Prompt {prompt_id} or version {version_id} not found")

        response.raise_for_status()

        try:
            schemas = response.json()
            return PromptSchemas.model_validate(schemas)
        except Exception as e:
            logger.error(
                f"Error fetching prompt schemas for {prompt_id} version {version_id}: {e}",
                exc_info=True,
            )
            raise MoxnSchemaValidationError(
                prompt_id=prompt_id,
                version_id=version_id,
                schema=response.text,
                detail=str(e),
            )

    async def get_code_stubs(
        self,
        prompt_id: str,
        version_id: str,
        schema_prompt_type: SchemaPromptType = SchemaPromptType.ALL,
    ) -> CodegenResponse:
        try:
            params = {
                "version_id": version_id,
                "schema_type": schema_prompt_type.value,
            }

            response = await self.get(
                f"/prompts/{prompt_id}/codegen",
                params=params,
                headers=self.get_headers(),
                timeout=httpx.Timeout(30.0),
            )
            # Enhanced error handling
            if response.status_code != 200:
                logger.error(f"Codegen prompt failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")

                try:
                    error_detail = response.json()
                    error_message = error_detail.get("detail", {}).get(
                        "message", response.text
                    )
                except json.JSONDecodeError:
                    error_message = response.text or f"HTTP {response.status_code}"

                raise RuntimeError(f"Codegen prompt failed: {error_message}")

            # Parse and validate response
            codegen_response = CodegenResponse.model_validate(response.json())
            logger.info(f"Generated {len(codegen_response.files)} files")
            return codegen_response
        except httpx.TimeoutException as e:
            logger.error(f"Prompt timed out: {e}")
            raise RuntimeError("Code stub prompt timed out") from e
        except Exception as e:
            logger.error(f"Code stub prompt failed: {e}", exc_info=True)
            raise RuntimeError("Code stub prompt failed") from e

    async def generate_code_stubs(
        self,
        prompt_id: str,
        version_id: str,
        schema_prompt_type: SchemaPromptType = SchemaPromptType.ALL,
        output_dir: Path | str | None = "./moxn_types",
    ) -> CodegenResponse:
        """
        Generate Python type stubs from prompt schemas.

        Args:
            prompt_id: The prompt ID
            version_id: The version ID
            schema_prompt_type: Type of schemas to generate (input, output, or all)
            output_dir: Optional directory to write the generated code to

        Returns:
            CodegenResponse object containing the generated code files

        Raises:
            MoxnSchemaValidationError: If schema validation fails
            RuntimeError: If the codegen prompt fails
            IOError: If file operations fail
        """
        logger.info(
            f"Generating code stubs for prompt {prompt_id} version {version_id}"
        )

        try:
            # Parse and validate response
            codegen_response = await self.get_code_stubs(
                prompt_id=prompt_id,
                version_id=version_id,
                schema_prompt_type=schema_prompt_type,
            )
            logger.info(f"Generated {len(codegen_response.files)} files")

            # Validate generated files
            for filename, content in codegen_response.files.items():
                logger.debug(f"Validating generated file: {filename}")
                if not content.strip():
                    raise ValueError(f"Generated code for {filename} is empty")
                if "class" not in content:
                    raise ValueError(
                        f"Generated code for {filename} doesn't contain a class definition"
                    )

            # Save files if configured
            if output_dir is not None:
                output_path = (
                    Path(output_dir) if isinstance(output_dir, str) else output_dir
                )
                output_path.mkdir(parents=True, exist_ok=True)

                for filename, content in codegen_response.files.items():
                    file_path = output_path / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)
                    logger.info(f"Saved generated code to {file_path}")

            return codegen_response

        except httpx.TimeoutException as e:
            logger.error(f"Codegen prompt timed out: {e}")
            raise RuntimeError("Code generation timed out") from e
        except Exception as e:
            logger.error(f"Code generation failed: {e}", exc_info=True)
            raise

    async def create_telemetry_log(
        self,
        prompt: SpanLogRequest | SpanEventLogRequest,
    ) -> TelemetryLogResponse:
        """Send telemetry log to the API."""
        logger.debug(f"Sending telemetry log: {prompt}")

        try:
            # Ensure proper serialization of all fields
            json_data = prompt.model_dump(
                exclude_none=True,
                mode="json",
                by_alias=True,
            )

            response = await self.client.post(
                "/telemetry/log",
                json=json_data,
            )
            response.raise_for_status()

            return TelemetryLogResponse.model_validate(response.json())

        except httpx.TimeoutException as e:
            logger.error(f"Telemetry prompt timed out: {e}")
            raise RuntimeError("Telemetry prompt timed out") from e
        except Exception as e:
            logger.error(f"Telemetry prompt failed: {e}", exc_info=True)
            raise RuntimeError("Failed to send telemetry log") from e

    async def create_prompt_instance(
        self,
        prompt_id: str,
        version_id: str | None = None,
        message_names: list[str] | None = None,
        **variables,
    ) -> PromptInstance:
        """
        Create a new PromptInstance for managing LLM interactions.

        Args:
            prompt_id: The base prompt ID
            version_id: Optional specific version
            message_names: Optional list of message names to include
            **variables: Variables to use in message rendering
        """
        prompt = await self.get_prompt(prompt_id, version_id)
        return prompt.create_instance(message_names=message_names, **variables)

    @asynccontextmanager
    async def span(
        self,
        name: str,
        prompt_id: UUID,
        prompt_version_id: UUID,
        kind: Literal["llm", "tool", "agent"],
        attributes: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[SpanContext, None]:
        """
        Creates a new span context and sets it as the current span.

        Example:
            async with client.span("agent_task", prompt_id=req_id, prompt_version_id=ver_id, kind="agent"):
                # Do work within the span
                await client.log_event(llm_event)
        """
        async with self.telemetry_client.span(
            name=name,
            prompt_id=prompt_id,
            prompt_version_id=prompt_version_id,
            kind=kind,
            attributes=attributes,
        ) as span_context:
            yield span_context

    async def log_event(
        self,
        event: LLMEvent,
        span_id: Optional[UUID] = None,
    ) -> None:
        """
        Logs an LLM interaction event within the current span.

        Args:
            event: The LLM event to log
            span_id: Optional specific span ID to log to (uses current span if None)
        """
        await self.telemetry_client.log_event(event=event, span_id=span_id)
