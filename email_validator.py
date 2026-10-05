import re
import socket
from typing import Tuple, Type

# Intentar importar dnspython de forma segura al cargar el módulo
try:
    import dns.exception
    import dns.resolver

    _DNSPYTHON_AVAILABLE = True
    _DNS_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.Timeout,
        dns.exception.DNSException,
    )
except ImportError:
    _DNSPYTHON_AVAILABLE = False
    _DNS_EXCEPTIONS = ()

# Regex precompilado para mayor eficiencia en validaciones repetidas
_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+"  # Parte local
    r"@[a-zA-Z0-9-]+"  # Nombre del dominio principal
    r"(?:\.[a-zA-Z0-9-]+)*"  # Subdominios opcionales
    r"\.[a-zA-Z]{2,}$"  # TLD (mínimo 2 caracteres alfabéticos)
)


def is_valid_email(
    email: str, check_domain: bool = False, timeout: float = 3.0
) -> bool:
    """Valida una dirección de correo electrónico mediante sintaxis (regex)

    y opcionalmente comprueba la existencia del dominio mediante DNS.

    :param email: Dirección de correo electrónico a validar.
    :param check_domain: Si es True, realiza verificación DNS del dominio.
    :param timeout: Tiempo límite en segundos para la consulta DNS.
    :return: True si es válido sintácticamente (y el dominio existe si
        check_domain=True).
    """
    if not isinstance(email, str):
        return False

    # Validar formato sintáctico
    if not _EMAIL_REGEX.match(email):
        return False

    if not check_domain:
        return True

    domain = email.split("@")[-1]

    # 1. Estrategia con dnspython (si está disponible)
    if _DNSPYTHON_AVAILABLE:
        try:
            resolver = dns.resolver.Resolver()
            resolver.lifetime = timeout

            # Probar primero registros MX
            try:
                resolver.resolve(domain, "MX")
                return True
            except dns.resolver.NoAnswer:
                # Si no tiene registros MX, RFC 5321 permite fallback a registros A/AAAA
                try:
                    resolver.resolve(domain, "A")
                    return True
                except _DNS_EXCEPTIONS:
                    try:
                        resolver.resolve(domain, "AAAA")
                        return True
                    except _DNS_EXCEPTIONS:
                        return False
        except _DNS_EXCEPTIONS:
            return False

    # 2. Estrategia Fallback con librería estándar (socket)
    try:
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
            # Obtiene información de host (IPv4 / IPv6)
            socket.getaddrinfo(domain, None)
            return True
        finally:
            socket.setdefaulttimeout(original_timeout)
    except (socket.gaierror, UnicodeError, socket.timeout, OSError):
        return False


if __name__ == "__main__":
    # Casos de prueba exhaustivos
    test_cases = [
        ("test@example.com", True, "Correo válido estándar"),
        ("invalid-email.com", False, "Falta el símbolo '@'"),
        ("test@.com", False, "Nombre de dominio vacío"),
        ("test@example", False, "Falta el TLD"),
        ("test@example.c", False, "TLD de 1 sola letra (inválido)"),
        ("test@domain-with-hyphen.com", True, "Guion en el dominio (válido)"),
        ("test@sub.domain.com", True, "Subdominio presente (válido)"),
        ("test@domain.com.", False, "Punto al final del TLD (inválido)"),
        ("test@domain..com", False, "Doble punto consecutivo (inválido)"),
        (
            "user.name+tag@domain.co.uk",
            True,
            "Caracteres especiales permitidos en la parte local",
        ),
        (12345, False, "Entrada no es una cadena de texto"),
    ]

    print("=== Ejecutando pruebas de sintaxis ===")
    all_passed = True
    for email, expected, description in test_cases:
        result = is_valid_email(email, check_domain=False)
        status = "OK" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(
            f"[{status}] {str(email):<30} -> Obtenido: {result:<5} | Esperado: {expected:<5} ({description})"
        )

    print(
        f"\nEstado dnspython: {'Disponible' if _DNSPYTHON_AVAILABLE else 'No disponible (usando socket fallback)'}"
    )
    print(
        f"Resultado final: {'TODAS LAS PRUEBAS PASARON' if all_passed else 'ALGUNA PRUEBA FALLÓ'}"
    )
