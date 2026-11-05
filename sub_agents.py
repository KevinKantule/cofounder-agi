from llm_chain import query_cofounder_brain
# Importamos EXACTAMENTE la función que existe en tu cli_runner.py
from cli_runner import run_python_script
from memory_rag import LocalVectorMemory
from event_bridge import emit_event

# Instanciar el motor de memoria vectorial en disco con LanceDB
memory = LocalVectorMemory()

ROLES = {
    "coder": """Eres el Ingeniero de Software Principal de la Startup. 
Tu trabajo es escribir código Python impecable, tipado, modular y listo para producción. 
Cumple estrictamente con las reglas de arquitectura y seguridad provistas.""",

    "reviewer": """Eres el Revisor de Código Senior y Auditor de Seguridad.
Revisa el código propuesto. Si encuentras errores sintácticos, de lógica o vulnerabilidades, señala los fallos.
Si el código está listo y libre de errores, debes responder únicamente con la palabra 'APROBADO'.""",

    "business_strategist": """Eres el Abogado del Diablo y Estratega de Negocios.
Cuestiona premisas inviables, evalúa competidores y exige pragmatismo comercial.""",

    "open_source_explorer": """Eres el Arquitecto de Software Open Source.
Aprovecha repositorios y librerías existentes para acelerar el desarrollo del MVP."""
}

def build_rag_context(query: str) -> str:
    """Consulta LanceDB e inyecta reglas relevantes al contexto del prompt."""
    recuerdos = memory.query_memory(query, limit=3)
    if not recuerdos:
        return ""
    
    contexto = "\n--- 🧠 MEMORIA RAG Y REGLAS HISTÓRICAS (LanceDB) ---\n"
    for r in recuerdos:
        contexto += f"• [{r.get('category', 'general')}]: {r.get('text')}\n"
    contexto += "---------------------------------------------------\n"
    return contexto


def run_sub_agent(role: str, task_prompt: str) -> str:
    """Ejecuta un sub-agente inyectando memoria RAG desde LanceDB."""
    system_prompt = ROLES.get(role, "Eres un asistente virtual especializado.")
    
    # 1. Recuperar contexto histórico relevante desde LanceDB
    rag_context = build_rag_context(task_prompt)
    
    # 2. Unir prompt del usuario con las reglas recuperadas
    prompt_completo = f"{rag_context}\nTarea actual:\n{task_prompt}"
    
    print(f"🤖 Activando Agente: [{role.upper()}] (Consulta RAG integrada)...")
    destination = {"coder": "laboratorio", "reviewer": "escudo", "business_strategist": "mercado", "open_source_explorer": "cerebro"}.get(role, "cerebro")
    emit_event(role, "working", destination, f"{role} procesando tarea")
    
    # 3. Formatear el prompt como una lista estructurada para LiteLLM
    mensajes_estructurados = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_completo}
    ]
    
    # Enviar la lista directamente a la función de tu llm_chain
    response = query_cofounder_brain(mensajes_estructurados, workload=role)
    emit_event(role, "success", destination, f"{role} terminó su tarea")
    return response


def collaborative_code_generation(task_description: str, filename: str = "mvp_module.py", max_intentos: int = 3) -> str:
    """
    Bucle Coder <-> Reviewer <-> CLI Runner con memoria activa RAG en LanceDB.
    """
    rag_context = build_rag_context(task_description)
    feedback_reviewer = ""
    codigo_actual = ""

    for intento in range(1, max_intentos + 1):
        print(f"\n🔄 === BUCLE REACT (INTENTO {intento}/{max_intentos}) ===")
        emit_event("coder", "walking", "laboratorio", f"Intento ReAct {intento}/{max_intentos}")

        # A. Coder genera o corrige el código
        prompt_coder = (
            f"{rag_context}\n"
            f"REQUERIMIENTO TÉCNICO:\n{task_description}\n\n"
            f"FEEDBACK PREVIO / ERRORES A CORREGIR:\n{feedback_reviewer if feedback_reviewer else 'Ninguno. Genera la versión inicial.'}\n\n"
            f"Escribe solo el código Python funcional dentro de un bloque ```python ... ```."
        )
        
        codigo_bruto = run_sub_agent("coder", prompt_coder)

        # Extraer bloques de código Markdown
        if "```python" in codigo_bruto:
            codigo_actual = codigo_bruto.split("```python")[1].split("```")[0].strip()
        elif "```" in codigo_bruto:
            codigo_actual = codigo_bruto.split("```")[1].split("```")[0].strip()
        else:
            codigo_actual = codigo_bruto.strip()

        # B. Reviewer audita el código
        prompt_reviewer = f"Código a revisar:\n```python\n{codigo_actual}\n```\nRequerimiento: {task_description}"
        revision = run_sub_agent("reviewer", prompt_reviewer)

        print(f"🧐 Dictamen del Reviewer: {revision[:100]}...")

        # C. Si fue aprobado o estamos en el último intento, probar en CLI Runner
        if "APROBADO" in revision.upper() or intento == max_intentos:
            print("🚀 Ejecutando prueba de integración en CLI Runner...")
            emit_event("coder", "walking", "camara_pruebas", "Ejecutando prueba aislada")
            
            # GUARDAMOS EL CÓDIGO EN DISCO PARA QUE TU CLI_RUNNER PUEDA LEERLO
            with open(filename, "w", encoding="utf-8") as f:
                f.write(codigo_actual)
            
            # USAMOS TU FUNCIÓN 'run_python_script' PASANDO LA RUTA DEL ARCHIVO
            resultado = run_python_script(filename)
            exito = resultado["success"]
            output_cli = resultado["output"]

            if exito:
                print(f"✅ ¡Módulo '{filename}' ejecutado con éxito sin errores!")
                
                # D. GUARDAR APRENDIZAJE EN LANCEDB (Escritura RAG)
                regla_resumen = f"Módulo funcional '{filename}' completado para: {task_description[:80]}"
                memory.add_memory(
                    text=regla_resumen,
                    category="code_artifact",
                    metadata={"filename": filename}
                )
                emit_event("coder", "success", "camara_pruebas", "Prueba de integración superada")
                return codigo_actual
            else:
                feedback_reviewer = f"El código falló al ejecutarse en consola con este traceback:\n{output_cli}"
                print(f"❌ Error de ejecución en consola:\n{output_cli}")
                emit_event("coder", "error", "camara_pruebas", "La prueba falló", output=output_cli)
        else:
            feedback_reviewer = revision

    return codigo_actual
