import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=== REVISIÓN OFICIAL DE MODELOS EN TUS CUENTAS ===")

# 1. Groq
groq_key = os.getenv("GROQ_API_KEY")
if groq_key and "tu_clave" not in groq_key:
    try:
        res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {groq_key}"})
        if res.status_code == 200:
            models = [m["id"] for m in res.json().get("data", [])]
            print("\n✅ Groq (Modelos de Razonamiento y Texto):")
            for m in models:
                if not any(x in m for x in ["whisper", "guard", "orpheus"]):
                    print(f"  • groq/{m}")
    except Exception as e:
        print(f"❌ Error en Groq: {e}")

# 2. Gemini
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key and "tu_clave" not in gemini_key:
    try:
        res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}")
        if res.status_code == 200:
            models = [
                m["name"].replace("models/", "") 
                for m in res.json().get("models", []) 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            print("\n✅ Gemini (Modelos de Razonamiento y Texto):")
            for m in models:
                if not any(x in m for x in ["tts", "image", "clip", "robotics", "computer-use"]):
                    print(f"  • gemini/{m}")
    except Exception as e:
        print(f"❌ Error en Gemini: {e}")

# 3. OpenRouter
openrouter_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_key and "tu_clave" not in openrouter_key:
    try:
        res = requests.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {openrouter_key}"})
        if res.status_code == 200:
            models = [m["id"] for m in res.json().get("data", [])]
            destacados = [m for m in models if any(k in m for k in ["llama-3.3", "gemini-2", "qwen-2.5", "deepseek"])]
            print("\n✅ OpenRouter (Modelos de Frontera Gratuitos/Destacados):")
            for m in destacados[:8]:
                print(f"  • openrouter/{m}")
    except Exception as e:
        print(f"❌ Error en OpenRouter: {e}")