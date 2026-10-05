import os
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

# 1. Cargar la configuración local
load_dotenv()

print("🔌 Conectando con Ollama local (qwen2.5-coder:7b)...")

# 2. Configurar el modelo local mediante LiteLLM
model_local = LiteLLMModel(
    model_id="ollama/qwen2.5-coder:7b",
    api_base=os.getenv("OLLAMA_HOST", "http://localhost:11434")
)

# 3. Crear el agente programador local
agente_programador = CodeAgent(
    tools=[],
    model=model_local,
    add_base_tools=True
)

# 4. Tarea de prueba para el agente
prompt_tarea = (
    "Escribe un script en Python que tome la lista [15, 3, 8, 22, 1, 4] "
    "y devuelva solo los números pares ordenados de menor a mayor. "
    "Ejecútalo y entrega el resultado final."
)

print("\n🚀 Ejecutando tarea con el agente programador local...\n")

try:
    resultado = agente_programador.run(prompt_tarea)
    print("\n✅ --- RESULTADO FINAL DEL AGENTE ---")
    print(resultado)
except Exception as e:
    print(f"\n❌ Error durante la ejecución: {e}")