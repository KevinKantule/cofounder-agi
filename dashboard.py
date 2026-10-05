import sys
import streamlit as st
from web_tools import search_web, search_github_repos
from sub_agents import run_sub_agent, collaborative_code_generation

st.set_page_config(page_title="Cofounder AGI", page_icon="🤖", layout="wide")

# --- CLASE PARA INTERCEPTAR LA CONSOLA (MAGIA AGI) ---
class StreamlitConsole:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        # Dibuja la terminal en tiempo real en la barra lateral
        self.placeholder.code(self.buffer, language="bash")

    def flush(self):
        pass

# --- 1. GESTIÓN DEL ESTADO ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Soy tu Cofundador AGI. Ingresa una idea de negocio o requerimiento técnico."}]
if "fase" not in st.session_state:
    st.session_state.fase = "IDEACION"
if "idea_actual" not in st.session_state:
    st.session_state.idea_actual = ""
if "tech_report" not in st.session_state:
    st.session_state.tech_report = ""

# --- 2. BARRA LATERAL (MONITOR DE PENSAMIENTO EN VIVO) ---
with st.sidebar:
    st.title("🧠 Monitor del Cerebro")
    st.info(f"Fase Actual: **{st.session_state.fase}**")
    if st.button("🔄 Reiniciar Proyecto"):
        st.session_state.clear()
        st.rerun()
        
    st.markdown("---")
    st.subheader("🖥️ Terminal Autónoma")
    # Contenedor vacío donde inyectaremos los logs en tiempo real
    consola_placeholder = st.empty()

# --- ÁREA PRINCIPAL ---
st.title("🚀 Panel de Ideación y Desarrollo")

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 3. LÓGICA DE FASES ---

# FASE A: IDEACIÓN
if st.session_state.fase == "IDEACION":
    if prompt := st.chat_input("Ej: Sistema IoT para huertos, o SaaS de facturación..."):
        st.session_state.idea_actual = prompt
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.session_state.fase = "VALIDACION"
        st.rerun()

# FASE B: VALIDACIÓN
if st.session_state.fase == "VALIDACION":
    with st.chat_message("assistant"):
        st.markdown(f"🔍 **Analizando viabilidad para:** '{st.session_state.idea_actual}'")
        
        # Redirigir consola para ver las búsquedas si tuvieran prints
        sys.stdout = StreamlitConsole(consola_placeholder)
        
        with st.spinner("Investigando mercado y código abierto..."):
            market_data = search_web(f"competidores viabilidad: {st.session_state.idea_actual}")
            github_data = search_github_repos(f"open source {st.session_state.idea_actual}")
            
        with st.spinner("El Abogado del Diablo está analizando..."):
            business_report = run_sub_agent("business_strategist", f"IDEA:\n{st.session_state.idea_actual}\n\nMERCADO:\n{market_data}")
            
        with st.spinner("El Explorador está integrando..."):
            tech_report = run_sub_agent("open_source_explorer", f"IDEA:\n{st.session_state.idea_actual}\n\nGITHUB:\n{github_data}")
            st.session_state.tech_report = tech_report
            
        # Restaurar consola
        sys.stdout = sys.__stdout__
            
        reporte_final = f"### 🧐 Análisis Anti-Complacencia\n{business_report}\n\n### 🏗️ Propuesta Técnica\n{tech_report}"
        st.markdown(reporte_final)
        
        st.session_state.mensajes.append({"role": "assistant", "content": reporte_final})
        st.session_state.fase = "DECISION_HITL"
        st.rerun()

# FASE C: HITL
if st.session_state.fase == "DECISION_HITL":
    st.warning("⚠️ Acción Requerida: ¿Aprobamos la arquitectura para generar el código?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Aprobar e Iniciar Ingeniería", use_container_width=True):
            st.session_state.fase = "CODING"
            st.rerun()
    with col2:
        if st.button("❌ Descartar Idea", use_container_width=True):
            st.session_state.mensajes.append({"role": "assistant", "content": "Idea descartada. Ingresa un nuevo concepto."})
            st.session_state.fase = "IDEACION"
            st.rerun()

# FASE D: INGENIERÍA (Bucle ReAct)
if st.session_state.fase == "CODING":
    with st.chat_message("assistant"):
        st.markdown("👨‍💻 **Ingeniería activada. Observa la terminal en la barra lateral...**")
        
        # Redirigir la consola para ver al Coder y Reviewer debatiendo y al cli_runner fallando/acertando
        sys.stdout = StreamlitConsole(consola_placeholder)
        
        prompt_tecnico = f"Implementa un MVP para: {st.session_state.idea_actual}. Tecnologías base: {st.session_state.tech_report}"
        
        codigo_generado = collaborative_code_generation(
            task_description=prompt_tecnico,
            filename="mvp_core_module.py",
            max_intentos=3
        )
        
        # Restaurar consola original al terminar
        sys.stdout = sys.__stdout__
        
        mensaje_exito = f"✅ **¡Módulo completado y guardado!**\n\n```python\n{codigo_generado}\n```"
        st.markdown(mensaje_exito)
        st.session_state.mensajes.append({"role": "assistant", "content": mensaje_exito})
        
        st.session_state.fase = "IDEACION"
        st.button("Iniciar nuevo ciclo")