"""Orquestador multicloud con fallback local contextual."""
from __future__ import annotations

import os
from typing import Any, Literal
try:
    from dotenv import load_dotenv
except ImportError:
    # El dashboard puede operar con variables ya definidas por el sistema/VS Code.
    def load_dotenv() -> bool:
        return False
try:
    import litellm
    from litellm import completion
except ImportError:
    litellm = None
    completion = None
from event_bridge import emit_event

load_dotenv()
if litellm is not None:
    litellm.suppress_debug_info = True
    litellm.drop_params = True

DEFAULT_FALLBACK_CHAIN = [
    {"model": "gemini/gemini-3.1-pro-preview", "api_key_env": "GEMINI_API_KEY"},
    {"model": "openrouter/qwen/qwen3.8-max", "api_key_env": "OPENROUTER_API_KEY"},
    {"model": "groq/openai/gpt-oss-120b", "api_key_env": "GROQ_API_KEY"},
    {"model": "gemini/gemini-3.6-flash", "api_key_env": "GEMINI_API_KEY"},
]
CODE_ROLES = {"coder", "reviewer", "runner"}
CODE_KEYWORDS = ("código", "code", "python", "traceback", "error", "debug", "test", "script")
Workload = Literal["coder", "reviewer", "runner", "business_strategist", "open_source_explorer", "general"]


def select_local_model(messages: list[dict[str, str]], workload: str = "general") -> str:
    """Elige el modelo local según especialidad; ambos nombres son configurables en .env."""
    task = " ".join(str(message.get("content", "")) for message in messages).lower()
    if workload in CODE_ROLES or any(keyword in task for keyword in CODE_KEYWORDS):
        return os.getenv("OLLAMA_CODER_MODEL", "ollama/qwen2.5-coder:7b")
    return os.getenv("OLLAMA_GENERAL_MODEL", "ollama/gemma4:latest")


def _content(response: Any) -> str:
    content = response.choices[0].message.content
    if not content or not str(content).strip():
        raise ValueError("Respuesta vacía del modelo.")
    return str(content).strip()


def query_cofounder_brain(
    messages: list[dict[str, str]], response_format: dict[str, Any] | None = None,
    preferred_model: str | None = None, workload: Workload | str = "general",
) -> str:
    """Agota los proveedores cloud antes de usar Qwen Coder o Gemma local."""
    if completion is None:
        return "Error: LiteLLM no está instalado en el intérprete activo. Ejecuta `python -m pip install -r requirements.txt`."
    chain = list(DEFAULT_FALLBACK_CHAIN)
    if preferred_model:
        key = "OPENROUTER_API_KEY" if "openrouter" in preferred_model else "GROQ_API_KEY" if "groq" in preferred_model else "GEMINI_API_KEY"
        chain.insert(0, {"model": preferred_model, "api_key_env": key})
    cloud_errors: list[str] = []
    for item in chain:
        api_key = os.getenv(item["api_key_env"])
        if not api_key or "tu_clave" in api_key.lower():
            continue
        try:
            model = item["model"]
            print(f"🧠 Razonando con nube: {model}...")
            emit_event("brain", "working", "cerebro", f"Consultando {model}")
            kwargs: dict[str, Any] = {"model": model, "messages": messages, "api_key": api_key, "max_tokens": 4096}
            if response_format:
                kwargs["response_format"] = response_format
            answer = _content(completion(**kwargs))
            emit_event("brain", "success", "cerebro", f"Respuesta de {model}")
            return answer
        except Exception as exc:
            cloud_errors.append(f"{item['model']}: {exc}")
            print(f"⚠️ {item['model']} no disponible; probando siguiente proveedor.")
    local_model = select_local_model(messages, workload)
    try:
        print(f"🚨 Nube no disponible. Usando motor local: {local_model}.")
        emit_event("brain", "walking", "cerebro", f"Fallback local a {local_model}", workload=workload)
        kwargs = {"model": local_model, "api_base": os.getenv("OLLAMA_HOST", "http://localhost:11434"), "messages": messages, "max_tokens": 4096}
        if response_format:
            kwargs["response_format"] = response_format
        answer = _content(completion(**kwargs))
        emit_event("brain", "success", "cerebro", f"Respuesta local de {local_model}")
        return answer
    except Exception as exc:
        emit_event("brain", "error", "cerebro", "Falló el fallback local", error=str(exc))
        detail = "; ".join(cloud_errors[-2:]) or "No hay credenciales cloud configuradas"
        return f"Error: no se pudo generar una respuesta. Cloud: {detail}. Local: {exc}"
