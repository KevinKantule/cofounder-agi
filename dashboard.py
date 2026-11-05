import sys
import streamlit as st
from web_tools import search_web, search_github_repos
from sub_agents import run_sub_agent, collaborative_code_generation
from router import route_intent
from agent_valley import render_agent_valley
from event_bridge import bridge, emit_event
from project_state import load_project_state, save_project_state

st.set_page_config(page_title="Cofounder AGI", page_icon="🤖", layout="wide")

# --- CLASE PARA INTERCEPTAR LA CONSOLA EN TIEMPO REAL ---
class StreamlitConsole:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        self.placeholder.code(self.buffer, language="bash")

    def flush(self):
        pass

# --- 1. GESTIÓN DEL ESTADO ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{
        "role": "assistant", 
        "content": "¡Hola! Soy tu Cofundador AGI. Ingresa una consulta general o describe una idea de negocio/software."
    }]
if "project_state_loaded" not in st.session_state:
    persisted = load_project_state()
    st.session_state.fase = persisted["phase"]
    st.session_state.idea_actual = persisted["idea"]
    st.session_state.tech_report = persisted["tech_report"]
    st.session_state.project_state_loaded = True
if "fase" not in st.session_state:
    st.session_state.fase = "IDEACION"
if "idea_actual" not in st.session_state:
    st.session_state.idea_actual = ""
if "tech_report" not in st.session_state:
    st.session_state.tech_report = ""

def persist_session() -> None:
    save_project_state({
        "phase": st.session_state.fase,
        "idea": st.session_state.idea_actual,
        "tech_report": st.session_state.tech_report,
        "last_result": st.session_state.mensajes[-1]["content"] if st.session_state.mensajes else "",
    })

# --- 2. BARRA LATERAL (MONITOR DE PENSAMIENTO EN VIVO) ---
with st.sidebar:
    st.title("🧠 Monitor del Cerebro")
    st.info(f"Fase Actual: **{st.session_state.fase}**")
    if st.button("🔄 Reiniciar Proyecto", use_container_width=True):
        bridge.clear()
        save_project_state({})
        st.session_state.clear()
        st.rerun()
        
    st.markdown("---")
    st.subheader("🖥️ Terminal Autónoma")
    consola_placeholder = st.empty()

    st.markdown("---")
    st.subheader("🌌 Agent Valley")
    render_agent_valley(bridge.snapshot(), height=410)

# --- ÁREA PRINCIPAL DE CHAT ---
st.title("🚀 Panel de Ideación y Desarrollo AGI")

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 3. LÓGICA DE FASES ---

# FASE A: IDEACIÓN & ROUTING
if st.session_state.fase == "IDEACION":
    if prompt := st.chat_input("Escribe una pregunta o una idea de negocio..."):
        # Registrar y mostrar mensaje del usuario de inmediato
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 1. Evaluar intención con el Router Predictivo Híbrido (0-100 ms)
        with st.spinner("🧠 Evaluando intención..."):
            intencion = route_intent(prompt)
        
        # 2. Ramificación según la clasificación
        if intencion == "CHAT":
            with st.chat_message("assistant"):
                respuesta_chat = (
                    "🤖 **Cofounder AGI (Modo Chat)**: ¡Entendido! "
                    "Estoy operativo y escuchando. Si en algún momento deseas validar "
                    "una idea de negocio, crear un software o generar arquitectura, "
                    "sólo descríbela y activaré el motor completo de ingeniería."
                )
                st.markdown(respuesta_chat)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_chat})
            emit_event("router", "success", "cerebro", "Consulta clasificada como conversación")
            persist_session()
            st.rerun()
            
        else:
            # Intención 'ENGINEERING': Avanzar al flujo pesado de validación
            st.session_state.idea_actual = prompt
            st.session_state.fase = "VALIDACION"
            emit_event("router", "walking", "mercado", "Solicitud de ingeniería recibida")
            persist_session()
            st.rerun()

# FASE B: VALIDACIÓN & ABOGADO DEL DIABLO
if st.session_state.fase == "VALIDACION":
    with st.chat_message("assistant"):
        st.markdown(f"🔍 **Analizando viabilidad para:** *'{st.session_state.idea_actual}'*")
        
        # Redirigir la consola a la barra lateral
        sys.stdout = StreamlitConsole(consola_placeholder)
        
        try:
            emit_event("business_strategist", "walking", "mercado", "Investigando mercado")
            with st.spinner("Investigando mercado y repositorios Open Source..."):
                market_data = search_web(f"competidores viabilidad: {st.session_state.idea_actual}")
                github_data = search_github_repos(f"open source {st.session_state.idea_actual}")
                
            emit_event("business_strategist", "working", "mercado", "Auditando la propuesta")
            with st.spinner("El Abogado del Diablo está auditando la propuesta..."):
                business_report = run_sub_agent(
                    "business_strategist", 
                    f"IDEA:\n{st.session_state.idea_actual}\n\nMERCADO:\n{market_data}"
                )
                
            emit_event("open_source_explorer", "working", "cerebro", "Analizando arquitectura open source")
            with st.spinner("El Explorador está integrando arquitectura Open Source..."):
                tech_report = run_sub_agent(
                    "open_source_explorer", 
                    f"IDEA:\n{st.session_state.idea_actual}\n\nGITHUB:\n{github_data}"
                )
                st.session_state.tech_report = tech_report
            emit_event("business_strategist", "success", "mercado", "Validación de negocio terminada")
            emit_event("open_source_explorer", "success", "cerebro", "Propuesta técnica lista")
        finally:
            # Restaurar consola siempre, incluso si hay una excepción
            sys.stdout = sys.__stdout__
            
        reporte_final = f"### 🧐 Análisis Anti-Complacencia\n{business_report}\n\n### 🏗️ Propuesta Técnica\n{tech_report}"
        st.markdown(reporte_final)
        
        st.session_state.mensajes.append({"role": "assistant", "content": reporte_final})
        st.session_state.fase = "DECISION_HITL"
        emit_event("hitl", "awaiting_approval", "escudo", "Esperando aprobación humana")
        persist_session()
        st.rerun()

# FASE C: CONTROL HUMANO EN EL BUCLE (HITL)
if st.session_state.fase == "DECISION_HITL":
    st.warning("⚠️ Acción Requerida: ¿Aprobamos la propuesta para generar y ejecutar el código?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Aprobar e Iniciar Ingeniería", use_container_width=True):
            st.session_state.fase = "CODING"
            emit_event("hitl", "success", "escudo", "Ingeniería aprobada por el usuario")
            persist_session()
            st.rerun()
    with col2:
        if st.button("❌ Descartar Idea", use_container_width=True):
            st.session_state.mensajes.append({"role": "assistant", "content": "Idea descartada. Puedes ingresar un nuevo concepto o pregunta."})
            st.session_state.fase = "IDEACION"
            emit_event("hitl", "idle", "escudo", "Propuesta descartada")
            persist_session()
            st.rerun()

# FASE D: INGENIERÍA (Bucle ReAct & Auto-Corrección)
if st.session_state.fase == "CODING":
    with st.chat_message("assistant"):
        st.markdown("👨‍💻 **Ingeniería activada. Observa los logs en vivo en la terminal lateral...**")
        
        # Redirigir consola para visualizar debates del Coder/Reviewer y pruebas en CLI
        sys.stdout = StreamlitConsole(consola_placeholder)
        
        try:
            emit_event("coder", "working", "laboratorio", "Generando y revisando código")
            prompt_tecnico = f"Implementa un MVP para: {st.session_state.idea_actual}. Tecnologías base: {st.session_state.tech_report}"
            
            codigo_generado = collaborative_code_generation(
                task_description=prompt_tecnico,
                filename="mvp_core_module.py",
                max_intentos=3
            )
        finally:
            sys.stdout = sys.__stdout__
        
        mensaje_exito = f"✅ **¡Módulo completado y ejecutado con éxito!**\n\n```python\n{codigo_generado}\n```"
        st.markdown(mensaje_exito)
        st.session_state.mensajes.append({"role": "assistant", "content": mensaje_exito})
        emit_event("coder", "success", "camara_pruebas", "Módulo generado")
        
        st.session_state.fase = "IDEACION"
        persist_session()
        if st.button("Iniciar nuevo ciclo"):
            st.rerun()
