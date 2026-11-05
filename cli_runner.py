import subprocess
import os
from event_bridge import emit_event

def run_static_analysis(filepath: str) -> tuple[bool, str]:
    """Escanea el código con Bandit (Seguridad) y MyPy (Tipado) antes de ejecutarlo."""
    try:
        # 1. Auditoría de Seguridad (Bandit)
        bandit_res = subprocess.run(
            ["bandit", "-r", filepath, "-ll", "-ii"], 
            capture_output=True, text=True
        )
        if bandit_res.returncode != 0:
            return False, f"🚨 VULNERABILIDAD DETECTADA POR BANDIT:\n{bandit_res.stdout.strip()}"

        # 2. Auditoría de Tipado (MyPy)
        mypy_res = subprocess.run(
            ["mypy", filepath, "--ignore-missing-imports"], 
            capture_output=True, text=True
        )
        if mypy_res.returncode != 0:
            return False, f"⚠️ ERROR DE TIPADO DETECTADO POR MYPY:\n{mypy_res.stdout.strip()}"

        return True, "✅ Análisis estático superado."
    except Exception as e:
        return False, f"Error en el sistema de linters: {str(e)}"


def run_python_script(filepath: str, timeout: int = 15) -> dict:
    """
    Ejecuta el script de forma segura: 
    Pasa por Linters y se ejecuta en un contenedor Docker efímero.
    """
    if not os.path.exists(filepath):
        emit_event("runner", "error", "camara_pruebas", "Archivo para ejecutar no existe")
        return {"success": False, "output": f"Error: El archivo '{filepath}' no existe."}

    # --- FASE 1: FILTRO HITL AUTÓNOMO (Linters) ---
    linter_ok, linter_msg = run_static_analysis(filepath)
    if not linter_ok:
        emit_event("runner", "error", "escudo", "El análisis estático bloqueó la ejecución")
        # Si falla el linter, devolvemos el error al Coder para que lo corrija
        return {"success": False, "output": linter_msg}

    # --- FASE 2: EJECUCIÓN AISLADA (Docker Sandbox) ---
    try:
        emit_event("runner", "working", "camara_pruebas", "Ejecutando sandbox Docker")
        abs_path = os.path.abspath(filepath)
        
        # Invocamos un contenedor Python ultraligero, montamos el archivo y lo ejecutamos.
        # Al terminar (o fallar), el contenedor se destruye automáticamente (--rm).
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{abs_path}:/app/script.py",
            "-w", "/app",
            "python:3.10-slim",
            "python", "script.py"
        ]

        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            emit_event("runner", "success", "camara_pruebas", "Sandbox completado")
            return {
                "success": True, 
                "output": result.stdout.strip() or "[Ejecución en Docker exitosa, sin salida en consola]"
            }
        else:
            emit_event("runner", "error", "camara_pruebas", "El sandbox devolvió un error")
            return {
                "success": False, 
                "output": f"❌ Error en Sandbox Docker:\n{result.stderr.strip() or result.stdout.strip()}"
            }
            
    except FileNotFoundError:
        emit_event("runner", "error", "camara_pruebas", "Docker no está disponible")
        return {"success": False, "output": "❌ Error Crítico: Docker no está instalado o no está en ejecución."}
    except subprocess.TimeoutExpired:
        emit_event("runner", "error", "camara_pruebas", "La ejecución excedió el tiempo límite")
        return {"success": False, "output": f"TIMEOUT: El script superó el límite de {timeout}s en el Sandbox."}
    except Exception as e:
        return {"success": False, "output": f"Error del sistema Docker: {str(e)}"}

# Alias de compatibilidad
run_python_code = run_python_script
