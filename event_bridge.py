"""Contrato de telemetría entre el motor Python y Agent Valley.

El bridge es deliberadamente local y sin red: Streamlit lee los eventos de la
sesión actual y los entrega al componente React como una lista JSON.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Literal, TypedDict
from uuid import uuid4

AgentStatus = Literal["idle", "walking", "working", "success", "error", "awaiting_approval"]


class AgentEvent(TypedDict):
    event_id: str
    timestamp: str
    agent_id: str
    status: AgentStatus
    destination: str
    message: str
    metadata: dict[str, Any]


class EventBridge:
    """Buffer circular, seguro para hilos, de eventos serializables."""

    def __init__(self, max_events: int = 200) -> None:
        self._events: deque[AgentEvent] = deque(maxlen=max_events)
        self._lock = Lock()

    def emit(
        self,
        agent_id: str,
        status: AgentStatus,
        destination: str,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AgentEvent:
        event: AgentEvent = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "status": status,
            "destination": destination,
            "message": message,
            "metadata": metadata or {},
        }
        with self._lock:
            self._events.append(event)
        return event

    def snapshot(self) -> list[AgentEvent]:
        with self._lock:
            return list(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


bridge = EventBridge()


def emit_event(
    agent_id: str,
    status: AgentStatus,
    destination: str,
    message: str = "",
    **metadata: Any,
) -> AgentEvent:
    """API única que deben utilizar los módulos del backend."""
    return bridge.emit(agent_id, status, destination, message, metadata)
