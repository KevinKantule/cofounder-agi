"""Persistencia mínima y explícita del contexto de desarrollo del proyecto."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_PATH = Path(__file__).with_name("project_state.json")
STATE_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_state() -> dict[str, Any]:
    return {
        "version": STATE_VERSION,
        "updated_at": _now(),
        "phase": "IDEACION",
        "idea": "",
        "tech_report": "",
        "last_result": "",
    }


def load_project_state(path: Path = STATE_PATH) -> dict[str, Any]:
    """Devuelve un estado válido; un archivo corrupto no impide iniciar la UI."""
    if not path.exists():
        return default_state()
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("El estado debe ser un objeto JSON")
        return {**default_state(), **loaded}
    except (OSError, ValueError, json.JSONDecodeError):
        return default_state()


def save_project_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    """Guarda de forma atómica para evitar perder contexto en un cierre repentino."""
    payload = {**default_state(), **state, "version": STATE_VERSION, "updated_at": _now()}
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp_path, path)
