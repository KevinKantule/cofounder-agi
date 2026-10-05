import json
import re
from llm_chain import query_cofounder_brain
from mcp_tools import safe_write_file, safe_read_file, list_workspace_files

def clean_code_content(raw_code: str) -> str:
    """Limpia bloques de código markdown de triple comilla si el LLM los incluye."""
    cleaned = raw_code.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip() + "\n"

def execute_agent_instruction(user_prompt: str):
    system_instruction = """
    Eres un Cofundador Técnico Autónomo. Si el usuario te pide crear o modificar código, 
    debes responder EXCLUSIVAMENTE en formato JSON estricto con esta estructura:
    {
        "pensamiento": "Explicación de la acción",
        "accion": "escribir_archivo" | "leer_archivo" | "listar_archivos",
        "ruta": "nombre_del_archivo.py",
        "contenido": "código python puro sin markdown ni comillas invertidas"
    }
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]

    print("🧠 El Cofundador está procesando la instrucción...")
    raw_response = query_cofounder_brain(messages, response_format={"type": "json_object"})
    
    try:
        plan = json.loads(raw_response)
        print(f"\n💡 Pensamiento del Agente: {plan.get('pensamiento')}")
        accion = plan.get("accion")
        ruta = plan.get("ruta", "")
        contenido = clean_code_content(plan.get("contenido", ""))

        if accion == "escribir_archivo":
            print(f"\n⚠️ SOLICITUD HITL: El agente quiere crear/modificar el archivo '{ruta}'.")
            confirmacion = input("¿Autorizas esta acción en tu disco duro? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                resultado = safe_write_file(ruta, contenido)
                print(f"RESULTADO: {resultado}")
            else:
                print("⛔ OPERACIÓN CANCELADA POR EL USUARIO.")

        elif accion == "leer_archivo":
            contenido_leido = safe_read_file(ruta)
            print(f"\n📖 Contenido de '{ruta}':\n{contenido_leido}")

        elif accion == "listar_archivos":
            archivos = list_workspace_files()
            print(f"\n📁 Archivos en el espacio de trabajo:\n{archivos}")

    except json.JSONDecodeError:
        print("\n❌ Error procesando la respuesta estructurada del LLM:")
        print(raw_response)

if __name__ == "__main__":
    prompt_prueba = "Crea un script llamado 'version_app.py' que defina una variable VERSION = '1.0.0' y ejecute un print con esa variable."
    execute_agent_instruction(prompt_prueba)