import ast
import re

# Comandos de consola restringidos que requieren autorización humana (HITL)
DESTRUCTIVE_COMMANDS = [
    r"\brm\b", r"\brdir\b", r"\bdel\b", r"\bformat\b", 
    r"DROP TABLE", r"DELETE FROM", r"git reset --hard", r"rmdir /s"
]

def analyze_python_code(code_string: str) -> tuple[bool, str]:
    """Inspecciona la sintaxis de código Python usando AST y detalla la línea exacta del fallo."""
    try:
        ast.parse(code_string)
        return True, "Sintaxis Python válida."
    except SyntaxError as e:
        lines = code_string.splitlines()
        linea_afectada = lines[e.lineno - 1].strip() if e.lineno and 0 < e.lineno <= len(lines) else "Desconocida"
        
        diagnostico = (
            f"Error de sintaxis: '{e.msg}' en la línea {e.lineno}\n"
            f"   📌 Línea del problema: `{linea_afectada}`\n"
            f"   💡 Sospecha: Formato Markdown sin limpiar (ej. ```python), caracteres de escape inválidos o sintaxis incompleta."
        )
        return False, diagnostico

def is_command_safe(command: str) -> tuple[bool, str]:
    """Intercepta intenciones de borrado de archivos indicando el patrón sospechoso."""
    for pattern in DESTRUCTIVE_COMMANDS:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            diagnostico_cmd = (
                f"⛔ INTERCEPCIÓN HITL: Comando bloqueado por política de seguridad.\n"
                f"   📌 Patrón prohibido detectado: '{match.group()}'\n"
                f"   💡 Sospecha: El comando '{command}' intenta realizar una eliminación o modificación destructiva en el sistema."
            )
            return False, diagnostico_cmd
    return True, "Comando seguro para ejecutar."

if __name__ == "__main__":
    # Prueba AST
    codigo_malo = "```python\ndef suma(a, b):\n    return a + b"
    valido, msg = analyze_python_code(codigo_malo)
    print(f"Test AST:\n{msg}\n")

    # Prueba HITL
    cmd_malo = "rm -rf /archivos"
    seguro, msg_cmd = is_command_safe(cmd_malo)
    print(f"Test HITL:\n{msg_cmd}")