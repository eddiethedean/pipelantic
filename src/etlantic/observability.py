"""Observability and notification provider protocols (0.9)."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class ObservabilityEvent:
    name: str
    severity: str = "info"
    message: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "severity": self.severity,
            "message": self.message,
            "attributes": dict(self.attributes),
        }


@runtime_checkable
class ObservabilityProvider(Protocol):
    def emit(self, event: ObservabilityEvent) -> None: ...


@runtime_checkable
class NotificationProvider(Protocol):
    def notify(
        self, subject: str, message: str, *, dedupe_key: str | None = None
    ) -> None: ...


@dataclass
class JsonConsoleLogger:
    """Structured JSON logs to stdout (secret-free attributes only)."""

    stream: Any = field(default_factory=lambda: sys.stdout)
    _seen: set[str] = field(default_factory=set)

    def emit(self, event: ObservabilityEvent) -> None:
        payload = event.to_dict()
        self.stream.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
        self.stream.flush()

    def notify(
        self, subject: str, message: str, *, dedupe_key: str | None = None
    ) -> None:
        key = dedupe_key or f"{subject}:{message}"
        if key in self._seen:
            return
        self._seen.add(key)
        self.emit(
            ObservabilityEvent(
                name="notification",
                severity="info",
                message=message,
                attributes={"subject": subject},
            )
        )


@dataclass
class OpenTelemetryAdapter:
    """Optional OpenTelemetry bridge (requires ``etlantic[otel]``)."""

    service_name: str = "etlantic"

    def emit(self, event: ObservabilityEvent) -> None:
        try:
            from opentelemetry import trace  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "OpenTelemetry support requires installing etlantic[otel]"
            ) from exc
        tracer = trace.get_tracer(self.service_name)
        with tracer.start_as_current_span(event.name) as span:
            for key, value in event.attributes.items():
                span.set_attribute(str(key), str(value))
            if event.message:
                span.add_event(event.message)
        logging.getLogger("etlantic.otel").info(
            "%s %s", event.name, event.message or ""
        )
