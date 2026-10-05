import os
import streamlit as st
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

load_dotenv()

# Configuración de la página web
st.set_page_config(page_title="Cofounder & Developer AI Agent", page_icon="🤖")
st.title("🤖 Cofounder & Developer Agent Dashboard")
st.caption("Arquitectura agéntica local impulsada por Ollama y Qwen 2.5 Coder")

# Inicialización del modelo local
@st.cache_resource
def load_agent():
    model_local = LiteLLMModel(
        model_id="ollama/qwen2.5-coder:7b",
        api_base=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )
    return CodeAgent(tools=[], model=model_local, add_base_tools=False)

agent = load_agent()

# Interfaz de entrada del usuario
user_prompt = st.text_area(
    "Escribe el requerimiento o tarea para el agente:",
    placeholder="Ejemplo: Escribe un script para calcular el área de un círculo dado su radio."
)

if st.button("Ejecutar Agente", type="primary"):
    if user_prompt.strip():
        with st.spinner("El agente local está pensando y escribiendo código en CPU..."):
            try:
                result = agent.run(user_prompt)
                st.success("¡Tarea ejecutada con éxito!")
                st.subheader("Resultado del Agente:")
                st.code(result)
            except Exception as e:
                st.error(f"Error durante la ejecución: {e}")
    else:
        st.warning("Por favor ingresa una instrucción antes de ejecutar.")