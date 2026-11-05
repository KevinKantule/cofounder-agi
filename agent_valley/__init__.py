"""Componente Streamlit que muestra la telemetría de Agent Valley."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_build_dir = Path(__file__).parent / "frontend" / "dist"


def render_agent_valley(events: list[dict[str, Any]], height: int = 410) -> None:
    """Renderiza la build Vite si existe; mantiene una alternativa útil en desarrollo."""
    if _build_dir.exists():
        component = components.declare_component("agent_valley", path=str(_build_dir))
        component(events=events, default=None, key="agent-valley")
    else:
        components.html(
            "<div style='padding:1rem;border:1px dashed #4b5563;border-radius:8px;'>"
            "Agent Valley aún no está compilado. Ejecuta <code>npm run build</code> en "
            "<code>agent_valley/frontend</code>.</div>",
            height=height,
        )
