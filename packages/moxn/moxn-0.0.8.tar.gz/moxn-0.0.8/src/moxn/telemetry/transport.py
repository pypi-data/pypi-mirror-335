from typing import Protocol

from moxn.base_models.telemetry import (
    SpanEventLogRequest,
    SpanLogRequest,
    TelemetryLogResponse,
)


class TelemetryTransportBackend(Protocol):
    """Protocol for the backend that handles actual sending of telemetry data"""

    async def create_telemetry_log(
        self, prompt: SpanLogRequest | SpanEventLogRequest
    ) -> TelemetryLogResponse: ...


class APITelemetryTransport:
    """Transport that sends telemetry data to the Moxn API"""

    def __init__(self, backend: TelemetryTransportBackend):
        self.backend = backend

    async def send_log(
        self, prompt: SpanLogRequest | SpanEventLogRequest
    ) -> TelemetryLogResponse:
        """Send telemetry log to the API"""
        return await self.backend.create_telemetry_log(prompt)
