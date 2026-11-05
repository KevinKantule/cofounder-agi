import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"

# Filtro rápido para requerimientos técnicos explícitos (0 ms de latencia)
ENGINEERING_PATTERNS = [
    r"\bsaas\b", r"\bfastapi\b", r"\bpython\b", r"\bbot\b", r"\bapi\b", 
    r"\bapp\b", r"\bplataforma\b", r"\bsistema\b", r"\bcódigo\b", r"\bcode\b",
    r"\bcrea\b", r"\bdesarrolla\b", r"\bconstruye\b", r"\bscript\b", r"\biot\b",
    r"\barquitectura\b", r"\bbase de datos\b", r"\bbackend\b", r"\bfrontend\b"
]

ROUTER_PROMPT = """You are a JSON intent classifier for an AGI system.
Classify the user input into "CHAT" or "ENGINEERING".

Definitions:
- CHAT: Greetings, casual questions, asking what you do, general knowledge.
- ENGINEERING: Software development, building apps, SaaS concepts, scripts, bots, technical requests.

Respond strictly in JSON format matching this schema:
{"intent": "CHAT"} or {"intent": "ENGINEERING"}

User Input: """

def route_intent(user_prompt: str) -> str:
    """
    Clasifica la intención combinando filtro directo por patrones y llama3.2:1b con JSON.
    """
    prompt_lower = user_prompt.lower()
    
    # 1. Verificación instantánea por palabras clave
    for pattern in ENGINEERING_PATTERNS:
        if re.search(pattern, prompt_lower):
            return "ENGINEERING"

    # 2. Clasificación estructurada con LLM para casos ambiguos
    payload = {
        "model": "llama3.2:1b",
        "prompt": f"{ROUTER_PROMPT}\"{user_prompt}\"\nJSON:",
        "format": "json",
        "stream": False,
        "keep_alive": 0,  # Libera la RAM inmediatamente
        "options": {
            "temperature": 0.0,
            "num_predict": 15
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        if response.status_code == 200:
            res_json = json.loads(response.json().get("response", "{}"))
            intent = res_json.get("intent", "").upper()
            if intent in ["CHAT", "ENGINEERING"]:
                return intent
    except Exception as e:
        print(f"⚠️ Error en Router LLM: {e}")
        
    return "CHAT"

# --- PRUEBA DE EVALUACIÓN ---
if __name__ == "__main__":
    pruebas = [
        "Hola, ¿qué sabes hacer?",
        "SaaS para gestión de inventarios con FastAPI",
        "¿Cuál es la capital de Francia?",
        "Crea un bot que escanee vulnerabilidades en Python"
    ]
    
    print("🧪 Probando Router Predictivo Híbrido (Regex + JSON LLM)...\n")
    for p in pruebas:
        intencion = route_intent(p)
        print(f"Prompt: '{p}' --> Intención: [{intencion}]")