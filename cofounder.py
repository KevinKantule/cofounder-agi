import time
from web_tools import search_web, search_github_repos
from sub_agents import run_sub_agent, collaborative_code_generation, AGENT_SPECIALIZATIONS
from memory_rag import AgentMemory

# Inyectamos los nuevos roles estratégicos al diccionario de especializaciones existente
AGENT_SPECIALIZATIONS["business_strategist"] = {
    "prompt": (
        "Eres el Cofundador Estratega y Abogado del Diablo. Tu rol es ANTI-COMPLACENCIA. "
        "Analiza los datos de mercado y competencia que se te proporcionan. "
        "Identifica por qué la idea podría fallar financieramente, técnica o logísticamente. "
        "Si hay hardware involucrado, cuestiona los costos (BOM) y la viabilidad de manufactura. "
        "Finalmente, propón un pivote o modelo de negocio más robusto."
    ),
    "preferred_model": "gemini/gemini-3.1-pro-preview" 
}

AGENT_SPECIALIZATIONS["open_source_explorer"] = {
    "prompt": (
        "Eres el Arquitecto de Integración. Revisa los proyectos Open-Source encontrados. "
        "Propón cómo usar estas herramientas (simuladores, frameworks, librerías) en lugar de "
        "programar desde cero. Destaca si las licencias suelen ser amigables para uso comercial."
    ),
    "preferred_model": "openrouter/qwen/qwen3.8-max"
}

def run_full_startup_cycle(idea: str):
    print("🚀 ========================================================")
    print("🌟 INICIANDO CICLO DE COFUNDADOR AGI: DE LA IDEA AL CÓDIGO")
    print("========================================================\n")
    
    print(f"💡 IDEA ORIGINAL: '{idea}'\n")
    
    # --- FASE 1: VALIDACIÓN DE NEGOCIO Y MERCADO ---
    print("🌐 [1/4] Investigando mercado y competidores en tiempo real...")
    market_data = search_web(f"competidores y viabilidad de: {idea}")
    time.sleep(2)
    
    print("🐙 [2/4] Buscando alternativas Open-Source en GitHub...")
    github_data = search_github_repos(f"open source {idea}")
    
    print("\n🧐 [3/4] Abogado del Diablo analizando viabilidad financiera...")
    prompt_strategist = f"IDEA:\n{idea}\n\nMERCADO:\n{market_data}"
    business_report = run_sub_agent("business_strategist", prompt_strategist)
    print(f"\n--- DICTAMEN DE NEGOCIO ---\n{business_report}\n")
    
    print("🏗️ [4/4] Explorador Open-Source proponiendo integraciones...")
    prompt_explorer = f"IDEA:\n{idea}\n\nGITHUB:\n{github_data}"
    tech_report = run_sub_agent("open_source_explorer", prompt_explorer)
    print(f"\n--- PROPUESTA TECNOLÓGICA ---\n{tech_report}\n")
    
    # --- PUNTO DE DECISIÓN HUMANA (HITL) ---
    print("⚠️ SOLICITUD HITL: Estrategia y validación completadas.")
    decision = input("¿Aprobamos la idea para pasar a desarrollo técnico? (s/n/pivotar): ").strip().lower()
    
    if decision == 'n':
        print("❌ Ciclo abortado. La idea fue descartada tras la validación.")
        return
    elif decision == 'pivotar':
        nuevo_enfoque = input("Escribe el nuevo enfoque o pivote: ")
        print(f"\n🔄 Reiniciando ciclo con el pivote: {nuevo_enfoque}")
        run_full_startup_cycle(nuevo_enfoque)
        return

    # --- FASE 2: DESARROLLO TÉCNICO Y RAG ---
    print("\n✅ IDEA APROBADA. Pasando a Ingeniería...")
    
    prompt_tecnico = (
        f"Implementa un MVP (Producto Mínimo Viable) en Python para esta idea: {idea}. "
        f"Toma en cuenta las sugerencias técnicas del explorador open-source: {tech_report} "
        f"Asegúrate de que el código sea modular, seguro y listo para producción."
    )
    
    file_name = "mvp_core_module.py"
    print(f"🧠 [Orquestador] Delegando tarea de código al equipo técnico...")
    
    codigo_final = collaborative_code_generation(
        task_description=prompt_tecnico,
        filename=file_name,
        max_intentos=5
    )
    
    # --- GUARDAR MEMORIA A LARGO PLAZO ---
    if codigo_final:
        mem = AgentMemory()
        mem.remember(
            f"Se validó y construyó el MVP para la idea: '{idea}'. El módulo base se guardó en {file_name}.",
            {"tag": "producto_lanzado"}
        )
        print("\n🏆 CICLO COMPLETADO: De la idea inicial al código en disco, con validación de mercado incluida.")

if __name__ == "__main__":
    # Prueba del flujo End-to-End
    idea_startup = (
        "Sistema IoT de bajo costo para automatizar el riego y monitoreo térmico en la germinación "
        "de cultivos caseros, con panel de control local."
    )
    run_full_startup_cycle(idea_startup)