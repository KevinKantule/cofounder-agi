import subprocess
import os

def run_python_script(filepath: str, timeout: int = 10) -> dict:
    """
    Ejecuta un script de Python en un subproceso y captura su salida.
    Retorna un diccionario con el estado de éxito y los logs o errores.
    """
    if not os.path.exists(filepath):
        return {"success": False, "output": f"Error: El archivo '{filepath}' no existe."}

    try:
        # Ejecuta el script invocando el intérprete de Python
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # returncode 0 significa que la ejecución fue impecable
        if result.returncode == 0:
            return {
                "success": True, 
                "output": result.stdout.strip() or "[Ejecución exitosa, sin salida en consola]"
            }
        else:
            # Capturamos el Traceback (Error) para pasárselo al Coder
            return {
                "success": False, 
                "output": result.stderr.strip() or result.stdout.strip()
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "output": f"TIMEOUT: El script se quedó colgado (límite de {timeout}s)."}
    except Exception as e:
        return {"success": False, "output": f"Error crítico de sistema al ejecutar: {str(e)}"}

if __name__ == "__main__":
    # Prueba rápida: Creamos un script temporal con un error a propósito
    test_file = "test_error.py"
    with open(test_file, "w") as f:
        f.write("print('Hola Mundo')\n1 / 0  # ZeroDivisionError intencional")
        
    print("▶️ Ejecutando script de prueba...")
    resultado = run_python_script(test_file)
    
    print("\n¿Fue exitoso?:", resultado["success"])
    print("Salida de la terminal:\n", resultado["output"])
    
    # Limpieza
    os.remove(test_file)