import os
import re
from llm_chain import query_cofounder_brain
from mcp_tools import safe_write_file
from memory_rag import AgentMemory
from cli_runner import run_python_script

AGENT_SPECIALIZATIONS = {
    "coder": {
        "prompt": (
            "Eres el Agente Coder de Elite. Escribe código Python eficiente, modular y perfecto, "
            "respetando el contexto del proyecto. Tu respuesta DEBE estar contenida dentro de un bloque ```python ... ```."
        ),
        "preferred_model": "openrouter/qwen/qwen3.8-max"
    },
    "reviewer": {
        "prompt": (
            "Eres el Agente Auditor de Calidad. Revisa el código del Coder con rigor extremo. "
            "Si todo es correcto, inicia tu respuesta EXACTAMENTE con la palabra 'APROBADO'. "
            "Si hay fallos lógicos o de seguridad, inicia con 'RECHAZADO' y explica por qué."
        ),
        "preferred_model": "gemini/gemini-3.1-pro-preview"
    }
}

def extract_python_code(raw_text: str) -> str:
    text = raw_text.strip()
    match = re.search(r"```(?:python)?\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip() + "\n"
    text = re.sub(r"^```(?:python)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip() + "\n"

def run_sub_agent(role: str, prompt: str) -> str:
    spec = AGENT_SPECIALIZATIONS.get(role, {
        "prompt": "Eres un asistente de ingeniería.",
        "preferred_model": None
    })
    messages = [
        {"role": "system", "content": spec["prompt"]},
        {"role": "user", "content": prompt}
    ]
    return query_cofounder_brain(messages, preferred_model=spec["preferred_model"])

def collaborative_code_generation(task_description: str, filename: str = None, max_intentos: int = 5):
    print(f"🎯 [Orquestador] Tarea asignada: {task_description}\n")
    
    memory = AgentMemory()
    relevant_memories = memory.query_rag(task_description, top_k=2)
    memory_context = ""
    
    if relevant_memories:
        print("🧠 [RAG] Contexto histórico recuperado:")
        for mem_item in relevant_memories:
            print(f"  • {mem_item}")
            memory_context += f"- {mem_item}\n"
        print()

    feedback = ""
    proposed_code = ""

    for intento in range(1, max_intentos + 1):
        print(f"🔄 --- Ciclo Agéntico {intento} de {max_intentos} ---")
        
        prompt_coder = f"Tarea: {task_description}"
        if memory_context:
            prompt_coder += f"\n\n🧠 REGLAS HISTÓRICAS:\n{memory_context}"
        if feedback:
            prompt_coder += f"\n\n⚠️ CORRECCIÓN REQUERIDA:\n{feedback}\nArregla el código para solucionar esto."
        
        print("👨‍💻 [Coder] Escribiendo/Refactorizando solución...")
        proposed_code = run_sub_agent("coder", prompt_coder)
        codigo_limpio = extract_python_code(proposed_code)
        
        print("🔍 [Reviewer] Auditando código estáticamente...")
        review_dictamen = run_sub_agent("reviewer", f"Audita este código:\n{codigo_limpio}")
        dictamen_limpio = review_dictamen.strip().replace("*", "").upper()

        # FASE DE AUDITORÍA Y EJECUCIÓN AUTÓNOMA
        if dictamen_limpio.startswith("APROBADO"):
            print("✅ [Reviewer] Análisis estático APROBADO. Pasando a prueba de terminal...")
            
            # 1. Crear archivo temporal para pruebas
            temp_file = "_temp_exec.py"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(codigo_limpio)
                
            # 2. Ejecutar el código de forma aislada
            print(f"▶️ [CLI Runner] Ejecutando código en segundo plano...")
            resultado = run_python_script(temp_file)
            
            # 3. Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            # 4. Evaluar el resultado real
            if resultado["success"]:
                print(f"✅ [CLI Runner] Ejecución IMPECABLE. Salida:\n{resultado['output']}\n")
                
                # Memoria y Guardado
                memory.remember(
                    f"Hito: {task_description} guardado exitosamente.",
                    {"tag": "desarrollo", "archivo": filename}
                )

                if filename:
                    # NUEVA VERSIÓN AUTO-GUARDADO PARA LA WEB
                    if filename:
                         res = safe_write_file(filename, codigo_limpio)
                         print(f"💾 Guardado por el agente: {res}")
                    #print(f"⚠️ SOLICITUD HITL: ¿Deseas guardar el código aprobado y probado en '{filename}'?")
                    #confirmacion = input("Autorizar escritura (s/n): ").strip().lower()
                    #if confirmacion == 's':
                        #res = safe_write_file(filename, codigo_limpio)
                        #print(res)
                return proposed_code
            else:
                # 5. Atrapar el Traceback y forzar autocorrección
                error_traceback = resultado["output"]
                print(f"❌ [CLI Runner] La ejecución falló. Traceback:\n{error_traceback}")
                feedback = (
                    f"El código fue aprobado por el Reviewer, pero al ejecutarse en consola arrojó "
                    f"este error (Traceback):\n{error_traceback}\n"
                    f"Por favor, analiza el error y corrige el código para que se ejecute correctamente."
                )
                print("⚠️ [Orquestador] Devolviendo el error de terminal al Coder para auto-reparación...\n")
        else:
            feedback = review_dictamen
            print("⚠️ [Reviewer] El código requiere correcciones estáticas. Devolviendo al Coder...\n")

    print("❌ Límite de intentos alcanzado sin lograr una ejecución exitosa.")
    return proposed_code

if __name__ == "__main__":
    # Prueba del flujo de auto-corrección forzando un error intencional.
    tarea = "Escribe un script que divida 10 entre 0, atrape el error e imprima un mensaje. Asegúrate de incluir un print('Inicio') al principio."
    collaborative_code_generation(tarea, filename="prueba_ejecucion.py")