"""
Módulo de validación segura de tokens o llaves de acceso.

Requisitos del proyecto:
- Python >=3.10
- Carga de variables de entorno desde un archivo .env (sin hardcodear credenciales)
- Validación del formato del token usando el árbol sintáctico (AST) para evitar
  inyección de código o valores inesperados.
"""

from __future__ import annotations

import os
import re
import ast
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Configuración de carga de .env
# --------------------------------------------------------------------------- #
_ENV_PATH: Final[Path] = Path(".") / ".env"


def _load_environment() -> None:
    """
    Carga el archivo .env una sola vez.
    La función es idempotente: si el archivo ya fue cargado, no hace nada.
    """
    if not os.getenv("PYTHON_DOTENV_LOADED"):
        load_dotenv(dotenv_path=_ENV_PATH, override=False)
        # Marcamos que ya cargamos para evitar recargas innecesarias
        os.environ["PYTHON_DOTENV_LOADED"] = "1"


# --------------------------------------------------------------------------- #
# Utilidades de validación de tokens
# --------------------------------------------------------------------------- #
_TOKEN_REGEX: Final[re.Pattern] = re.compile(
    r"^[A-Za-z0-9_\-]{20,}$"
)  # al menos 20 caracteres alfanuméricos, guiones y guiones bajos


def _is_valid_format(token: str) -> bool:
    """
    Verifica que el token cumpla con el patrón esperado.
    Se permite una longitud mínima de 20 caracteres y solo caracteres seguros.
    """
    return bool(_TOKEN_REGEX.fullmatch(token))


def _is_ast_safe(token: str) -> bool:
    """
    Usa el módulo `ast` para asegurarse de que el token no contenga estructuras
    que pudieran ser interpretadas como código Python.

    - Si el token se puede parsear como una expresión literal (por ej. una cadena
      simple), consideramos que es seguro.
    - Cualquier otro nodo del AST (por ej. llamadas, comprensiones, etc.) es
      rechazado.
    """
    try:
        # Parseamos como una expresión; si falla, no es una cadena literal.
        node = ast.parse(token, mode="eval")
    except SyntaxError:
        # No es una expresión válida → no es seguro.
        return False

    # Permitimos únicamente nodos de tipo Constant (cadenas, números, etc.).
    # Cualquier otro tipo (Call, BinOp, etc.) indica que el contenido es más que
    # una simple literal.
    return all(isinstance(child, ast.Constant) for child in ast.walk(node))


def _sanitize_token(token: str) -> str:
    """
    Elimina posibles espacios en blanco al inicio y al final.
    No modifica el contenido interno del token.
    """
    return token.strip()


# --------------------------------------------------------------------------- #
# API pública
# --------------------------------------------------------------------------- #
def get_token_from_env(var_name: str) -> str:
    """
    Obtiene la llave/token desde la variable de entorno indicada.

    Parámetros
    ----------
    var_name: str
        Nombre de la variable en .env que contiene la credencial.

    Retorna
    -------
    str
        Token limpio (sin espacios alrededor).

    Raises
    ------
    EnvironmentError
        Si la variable no está definida o está vacía.
    """
    _load_environment()
    raw = os.getenv(var_name)

    if raw is None or raw.strip() == "":
        raise EnvironmentError(
            f"La variable de entorno '{var_name}' no está definida o está vacía."
        )

    return _sanitize_token(raw)


def validate_token(var_name: str) -> bool:
    """
    Valida de forma segura una token/llave de acceso.

    Pasos de validación:
    1. Cargar la variable desde .env (sin hardcodear).
    2. Confirmar que el token tiene un formato aceptable mediante regex.
    3. Verificar que el token es una literal segura usando `ast`.
    4. (Opcional) Se pueden agregar más checks, como longitud exacta o prefijos.

    Parámetros
    ----------
    var_name: str
        Nombre de la variable de entorno que contiene el token.

    Retorna
    -------
    bool
        ``True`` si el token pasa todas las validaciones, ``False`` en caso contrario.
    """
    try:
        token = get_token_from_env(var_name)
    except EnvironmentError as exc:
        # Loggear de forma segura sin imprimir la credencial
        print(f"[VALIDATOR] Error al cargar token: {exc}")
        return False

    if not _is_valid_format(token):
        print("[VALIDATOR] Formato del token no válido.")
        return False

    if not _is_ast_safe(repr(token)):  # usamos repr para que sea una cadena literal válida
        print("[VALIDATOR] El token contiene patrones potencialmente peligrosos.")
        return False

    # Todas las comprobaciones pasaron
    return True


# --------------------------------------------------------------------------- #
# Ejemplo de uso (comentado para no ejecutar en producción)
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Supongamos que la variable .env se llama "MY_API_KEY"
    if validate_token("MY_API_KEY"):
        print("[INFO] Token validado correctamente.")
    else:
        print("[WARN] Token no es válido o no se pudo cargar.")
