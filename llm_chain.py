import os
import litellm
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

litellm.suppress_debug_info = True
litellm.drop_params = True

# Cadena de respaldo por defecto si el modelo preferido no responde
DEFAULT_FALLBACK_CHAIN = [
    {"model": "gemini/gemini-3.1-pro-preview", "api_key_env": "GEMINI_API_KEY"},
    {"model": "openrouter/qwen/qwen3.8-max", "api_key_env": "OPENROUTER_API_KEY"},
    {"model": "groq/openai/gpt-oss-120b", "api_key_env": "GROQ_API_KEY"},
    {"model": "gemini/gemini-3.6-flash", "api_key_env": "GEMINI_API_KEY"},
]

def query_cofounder_brain(messages: list, response_format: dict = None, preferred_model: str = None) -> str:
    # Si hay un modelo preferido, se intenta ejecutar de primero
    chain_to_use = list(DEFAULT_FALLBACK_CHAIN)
    
    if preferred_model:
        # Determina qué API key corresponde según el prefijo
        api_env = "GEMINI_API_KEY"
        if "openrouter" in preferred_model:
            api_env = "OPENROUTER_API_KEY"
        elif "groq" in preferred_model:
            api_env = "GROQ_API_KEY"

        # Inserta el modelo preferido al inicio de la cadena
        chain_to_use.insert(0, {"model": preferred_model, "api_key_env": api_env})

    for item in chain_to_use:
        model_id = item["model"]
        api_key = os.getenv(item["api_key_env"])

        if not api_key or "tu_clave" in api_key:
            continue

        try:
            print(f"🧠 Razonando con: {model_id}...")
            
            kwargs = {
                "model": model_id,
                "messages": messages,
                "api_key": api_key,
                "max_tokens": 4096
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = completion(**kwargs)
            content = response.choices[0].message.content
            
            if content and str(content).strip():
                return str(content).strip()
            else:
                raise ValueError("Respuesta vacía del modelo.")
                
        except Exception as e:
            print(f"⚠️ {model_id} indispuesto -> Conmutando al siguiente...\n")

    # Fallback local ininterrumpido en Ollama
    print("🚨 Nube no disponible. Usando Ollama local...")
    kwargs_local = {
        "model": "ollama/qwen2.5:7b",
        "api_base": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "messages": messages,
        "max_tokens": 4096
    }
    if response_format:
        kwargs_local["response_format"] = response_format

    response = completion(**kwargs_local)
    content = response.choices[0].message.content
    return str(content).strip() if content else "Error: Sin respuesta del modelo local."