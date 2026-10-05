import os
import requests
from dotenv import load_dotenv
from llm_chain import query_cofounder_brain

load_dotenv()

def fetch_all_active_models() -> dict:
    inventory = {"gemini": [], "groq": [], "openrouter": []}

    # Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and "tu_clave" not in gemini_key:
        try:
            res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}")
            if res.status_code == 200:
                inventory["gemini"] = [
                    f"gemini/{m['name'].replace('models/', '')}"
                    for m in res.json().get("models", []) 
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                    and not any(x in m["name"] for x in ["tts", "image", "clip", "robotics", "computer-use"])
                ]
        except Exception:
            pass

    # Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and "tu_clave" not in groq_key:
        try:
            res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {groq_key}"})
            if res.status_code == 200:
                inventory["groq"] = [
                    f"groq/{m['id']}" 
                    for m in res.json().get("data", [])
                    if not any(x in m["id"] for x in ["whisper", "guard", "orpheus"])
                ]
        except Exception:
            pass

    # OpenRouter
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key and "tu_clave" not in openrouter_key:
        try:
            res = requests.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {openrouter_key}"})
            if res.status_code == 200:
                models = [m["id"] for m in res.json().get("data", [])]
                inventory["openrouter"] = [
                    f"openrouter/{m}" 
                    for m in models 
                    if any(k in m for k in ["llama", "gemini", "qwen", "deepseek"])
                ]
        except Exception:
            pass

    return inventory

def audit_and_optimize_chain():
    inventory = fetch_all_active_models()
    
    prompt_auditoria = f"""
    ANALIZA ESTE INVENTARIO REAL Y EXCLUSIVO DE MODELOS ACTIVOS EN NUESTRAS CUENTAS:
    
    {inventory}
    
    INSTRUCCIONES STRICTAS:
    1. Elige ÚNICAMENTE modelos que estén explícitamente escritos en el objeto JSON de arriba.
    2. Identifica el MEJOR modelo de razonamiento/desarrollo para CADA PROVEEDOR individualmente:
       - El campeón de Gemini:
       - El campeón de OpenRouter:
       - El campeón de Groq:
    3. Con esos campeones, arma la cadena de prioridad del #1 al #4 para `MODEL_PRIORITY_CHAIN` asegurando diversidad de proveedores.
    4. Explica brevemente por qué el modelo elegido para Groq es el más adecuado dentro de su catálogo disponible.
    """

    historial = [
        {"role": "system", "content": "Eres un auditor estricto de infraestructura de IA. Seleccionas el mejor modelo disponible por cada proveedor."},
        {"role": "user", "content": prompt_auditoria}
    ]

    print("🔍 Auditando el mejor modelo por cada proveedor (Gemini, OpenRouter, Groq)...\n")
    dictamen = query_cofounder_brain(historial)
    print("--- DICTAMEN DE CAMPEONES POR PROVEEDOR ---")
    print(dictamen)

if __name__ == "__main__":
    audit_and_optimize_chain()