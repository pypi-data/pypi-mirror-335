from contextlib import asynccontextmanager
from contextvars import Token
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Literal, Optional
from uuid import UUID, uuid4

from moxn.base_models.telemetry import (
    LLMEvent,
    SpanLogRequest,
    SpanLogType,
    TelemetryLogResponse,
    SpanKind,
)

from .context import SpanContext, current_span
from moxn.base_models.telemetry import TelemetryTransport


class TelemetryClient:
    """
    Client for sending telemetry data to Moxn's observability system.

    Provides context-aware span management and event logging.
    Thread-safe across async boundaries using contextvars.
    """

    def __init__(
        self,
        transport: TelemetryTransport,
    ):
        self._transport = transport

    @asynccontextmanager
    async def span(
        self,
        name: str,
        prompt_id: UUID,
        prompt_version_id: UUID,
        kind: Literal["llm", "tool", "agent"] | SpanKind,
        attributes: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[SpanContext, None]:
        """
        Creates a new span context and sets it as the current span.

        Example:
            async with telemetry.span("agent_task", kind="agent"):
                # Current span is automatically available
                response = await llm.chat(...)
                await telemetry.log_event(...)
        """
        if isinstance(kind, str):
            kind = SpanKind(kind)
        parent_context = current_span.get()

        # Create new context
        context = (
            parent_context.create_child(name, kind, attributes)
            if parent_context
            else SpanContext.create_root(
                name=name,
                kind=kind,
                prompt_id=prompt_id,
                prompt_version_id=prompt_version_id,
                transport=self._transport,
                attributes=attributes,
            )
        )

        # Log span start
        await self._log_span_start(context)

        # Set as current context and get token for restoration
        token: Token = current_span.set(context)

        try:
            yield context
        except Exception as e:
            # Log error and re-raise
            await self._log_span_error(context, str(e))
            raise
        finally:
            # Restore previous context and log span end
            current_span.reset(token)
            await self._log_span_end(context)

    async def log_event(
        self,
        event: LLMEvent,
        span_id: Optional[UUID] = None,
    ) -> None:
        """Logs an LLM interaction event within the current span."""
        # Simplified span context lookup - just use current span if no span_id provided
        context = current_span.get() if span_id is None else None
        if context is None and span_id is not None:
            # If span_id was provided but we couldn't find the context, raise error
            raise RuntimeError(f"No span found with id {span_id}")
        if context is None:
            raise RuntimeError("No active span context found")

        await context.log_event(
            message="LLM response received",
            metadata={"event_type": "llm_response"},
            attributes=event.model_dump(mode="json", by_alias=True),
        )

    async def _log_span_start(self, context: SpanContext) -> TelemetryLogResponse:
        """Log the start of a span"""
        # Create a combined attributes dictionary that includes span metadata
        enhanced_attributes = {
            "span.name": context.name,
            "span.kind": context.kind.value,
            **context.attributes,
        }

        return await self._transport.send_log(
            SpanLogRequest(
                id=uuid4(),
                timestamp=context.start_time,
                span_id=context.span_id,
                root_span_id=context.root_span_id,
                parent_span_id=context.parent_span_id,
                event_type=SpanLogType.START,
                prompt_id=context.prompt_id,
                prompt_version_id=context.prompt_version_id,
                attributes=enhanced_attributes,
                message=f"Started span: {context.name}",
            )
        )

    async def _log_span_error(
        self, context: SpanContext, error_message: str
    ) -> TelemetryLogResponse:
        """Log an error event for the span"""
        return await self._transport.send_log(
            SpanLogRequest(
                id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                span_id=context.span_id,
                root_span_id=context.root_span_id,
                parent_span_id=context.parent_span_id,
                event_type=SpanLogType.ERROR,
                prompt_id=context.prompt_id,
                prompt_version_id=context.prompt_version_id,
                attributes=context.attributes,
                message=f"Error in span {context.name}: {error_message}",
            )
        )

    async def _log_span_end(self, context: SpanContext) -> TelemetryLogResponse:
        """Log the end of a span"""
        return await self._transport.send_log(
            SpanLogRequest(
                id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                span_id=context.span_id,
                root_span_id=context.root_span_id,
                parent_span_id=context.parent_span_id,
                event_type=SpanLogType.END,
                prompt_id=context.prompt_id,
                prompt_version_id=context.prompt_version_id,
                attributes=context.attributes,
                message=f"Completed span: {context.name}",
            )
        )
