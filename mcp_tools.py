import os
from security_guard import analyze_python_code

# Carpeta raíz restringida (Sandbox)
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def safe_write_file(filepath: str, content: str) -> str:
    """Escribe o actualiza un archivo tras validar sintaxis si es código Python."""
    abs_path = os.path.abspath(os.path.join(WORKSPACE_DIR, filepath))
    
    # Bloqueo de Directory Traversal (ej. ../../windows/system32)
    if not abs_path.startswith(WORKSPACE_DIR):
        return "⛔ ACCESO DENEGADO: Intento de modificación fuera del espacio de trabajo."

    # Si es Python, pasa primero por el guardarraíl AST
    if filepath.endswith(".py"):
        valid, msg = analyze_python_code(content)
        if not valid:
            return f"⛔ BLOQUEADO POR GUARDARRAÍL AST: {msg}"

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ Archivo '{filepath}' guardado exitosamente."

def safe_read_file(filepath: str) -> str:
    """Lee el contenido de un archivo dentro del proyecto."""
    abs_path = os.path.abspath(os.path.join(WORKSPACE_DIR, filepath))
    if not abs_path.startswith(WORKSPACE_DIR):
        return "⛔ ACCESO DENEGADO: Lectura fuera del espacio de trabajo no permitida."
    if not os.path.exists(abs_path):
        return f"❌ El archivo '{filepath}' no existe."
    
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

def list_workspace_files() -> list:
    """Explora la estructura actual del proyecto ignorando carpetas del sistema."""
    files_list = []
    for root, _, files in os.walk(WORKSPACE_DIR):
        if any(ignored in root for ignored in ["venv", ".git", "__pycache__"]):
            continue
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), WORKSPACE_DIR)
            files_list.append(rel_path)
    return files_list

if __name__ == "__main__":
    print("📁 Estructura actual del espacio de trabajo:")
    for f in list_workspace_files():
        print(f"  • {f}")

    print("\n🧪 Prueba de escritura segura:")
    prueba = safe_write_file("test_modulo.py", "print('Hola desde el conector MCP')\n")
    print(prueba)