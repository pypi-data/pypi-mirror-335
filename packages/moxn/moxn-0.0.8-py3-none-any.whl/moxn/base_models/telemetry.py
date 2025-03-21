from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional, Protocol, TypeAlias, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from moxn.base_models.content import Provider


# Core Domain Types
class SpanKind(str, Enum):
    LLM = "llm"
    TOOL = "tool"
    AGENT = "agent"


class SpanStatus(str, Enum):
    UNSET = "UNSET"
    OK = "OK"
    ERROR = "ERROR"


class SpanLogType(str, Enum):
    START = "span_start"
    END = "span_end"
    ERROR = "span_error"


class SpanEventLogType(str, Enum):
    EVENT = "span_event"
    ERROR = "span_event_error"


class BaseTelemetryLogRequest(BaseModel):
    id: UUID
    timestamp: datetime | None = None
    prompt_id: UUID
    prompt_version_id: UUID
    message: str | None = None
    log_metadata: dict[str, Any] = Field(default_factory=dict)
    attributes: dict[str, Any] = Field(default_factory=dict)


class SpanLogRequest(BaseTelemetryLogRequest):
    span_id: UUID
    root_span_id: UUID
    parent_span_id: UUID | None = None
    event_type: SpanLogType


class SpanEventLogRequest(BaseTelemetryLogRequest):
    span_id: UUID
    span_event_id: UUID
    event_type: SpanEventLogType


# Base Models
class BaseTelemetryEvent(BaseModel):
    """Base class for all telemetry events"""

    model_config = ConfigDict(
        json_encoders={
            UUID: str,  # Ensure UUIDs are serialized as strings
            datetime: lambda dt: dt.isoformat(),  # Ensure datetimes are ISO format
        }
    )

    id: UUID
    timestamp: datetime
    prompt_id: UUID
    prompt_version_id: UUID
    message: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class BaseSpanLog(BaseTelemetryEvent):
    """Base class for span logs"""

    span_id: UUID
    root_span_id: UUID
    parent_span_id: Optional[UUID] = None
    event_type: SpanLogType


class BaseSpanEventLog(BaseTelemetryEvent):
    """Base class for span event logs"""

    span_id: UUID
    span_event_id: UUID
    event_type: SpanEventLogType


class TelemetryLogResponse(BaseModel):
    """Response from telemetry log endpoint"""

    id: UUID
    timestamp: datetime
    status: str = "success"
    message: Optional[str] = None


# Transport Protocol
class TelemetryTransport(Protocol):
    """Protocol for sending telemetry data"""

    async def send_log(
        self, prompt: Union[SpanLogRequest, SpanEventLogRequest]
    ) -> TelemetryLogResponse: ...


class BaseSpan(BaseTelemetryEvent):
    """Base class for span-related events"""

    span_id: UUID
    name: str
    kind: SpanKind
    status: SpanStatus = SpanStatus.UNSET
    root_span_id: Optional[UUID] = None
    parent_span_id: Optional[UUID] = None


class BaseSpanEvent(BaseTelemetryEvent):
    """Base class for span event-related events"""

    span_id: UUID
    event_type: Literal["llm_response"]
    variables: Optional[dict[str, Any]] = None
    messages: Optional[list[dict[str, Any]]] = None
    llm_response_content: Optional[str] = None
    llm_response_tool_calls: Optional[list[dict[str, Any]]] = None


# Domain Events
class SpanCreated(BaseSpan):
    """Event emitted when a span is created"""

    pass


class SpanCompleted(BaseSpan):
    """Event emitted when a span is completed"""

    pass


class SpanFailed(BaseSpan):
    """Event emitted when a span fails"""

    error: str


class SpanResponse(BaseModel):
    span_id: UUID
    status: str = "success"
    message: Optional[str] = None


class SpanEventResponse(BaseModel):
    event_id: UUID
    span_id: UUID
    event_type: str
    status: str = "success"
    message: Optional[str] = None


class LLMSpanEvent(BaseSpanEvent):
    """Event emitted for LLM interactions"""

    provider: Provider
    raw_input: Optional[dict[str, Any]] = None
    rendered_input: Optional[dict[str, Any]] = None


class ToolCall(BaseModel):
    """Standardized tool call representation"""

    name: str
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    """Standardized LLM response"""

    content: str | None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    stop_reason: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMEvent(BaseModel):
    """Domain model for LLM interactions"""

    messages: list[dict[str, Any]]
    provider: Provider
    llm_response_content: Optional[str] = None
    llm_response_tool_calls: Optional[list[dict[str, Any]]] = None
    raw_input: Optional[dict[str, Any]] = None
    rendered_input: Optional[dict[str, Any]] = None
    attributes: Optional[dict[str, Any]] = None

    @classmethod
    def from_response(
        cls,
        messages: list[dict[str, Any]],
        response: LLMResponse,
        provider: Provider,
        raw_input: Optional[dict[str, Any]] = None,
        rendered_input: Optional[dict[str, Any]] = None,
        attributes: Optional[dict[str, Any]] = None,
    ) -> "LLMEvent":
        """Create an LLMEvent from a standardized response"""
        return cls(
            messages=messages,
            provider=provider,
            llm_response_content=response.content,
            llm_response_tool_calls=[
                tc.model_dump(by_alias=True) for tc in response.tool_calls
            ],
            raw_input=raw_input,
            rendered_input=rendered_input,
            attributes=attributes,
        )


class CreateSpanRequest(BaseSpan):
    """API prompt model for span creation"""

    pass


class CreateSpanEventRequest(BaseSpanEvent):
    """API prompt model for span event creation"""

    pass


class TelemetryResponse(BaseTelemetryEvent):
    """Base API response model"""

    status: str = "success"


class ErrorResponse(BaseTelemetryEvent):
    """API error response model"""

    status: str = "error"
    error_message: str


# --- Type Aliases ---
TelemetryLogRequest: TypeAlias = Union[SpanLogRequest, SpanEventLogRequest]
