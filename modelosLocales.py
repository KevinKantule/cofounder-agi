import requests

def listar_modelos_locales():
    """Consulta la API de Ollama para listar los modelos instalados."""
    try:
        respuesta = requests.get("http://localhost:11434/api/tags")
        if respuesta.status_code == 200:
            modelos = [modelo["name"] for modelo in respuesta.json().get("models", [])]
            print("Modelos locales disponibles:")
            for m in modelos:
                print(f" - {m}")
            return modelos
    except Exception as e:
        print(f"Error conectando a Ollama local: {e}")

listar_modelos_locales()