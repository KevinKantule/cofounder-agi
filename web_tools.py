# web_tools.py
from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 4) -> str:
    """Busca información de mercado, competencia o viabilidad en la web."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return f"No se encontraron resultados en la web para: '{query}'"
            
        formatted_results = f"🔍 BÚSQUEDA WEB PARA '{query}':\n"
        for i, res in enumerate(results, 1):
            formatted_results += f"[{i}] {res.get('title', '')}\n"
            formatted_results += f"    Resumen: {res.get('body', '')}\n"
            
        return formatted_results
    except Exception as e:
        return f"Error en búsqueda web: {str(e)}"

def search_github_repos(topic: str, max_results: int = 3) -> str:
    """Busca herramientas open-source para no reinventar la rueda."""
    query = f"site:github.com {topic}"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return f"No se encontraron repositorios para: '{topic}'"
            
        formatted_results = f"📦 PROYECTOS OPEN-SOURCE EN GITHUB PARA '{topic}':\n"
        for i, res in enumerate(results, 1):
            formatted_results += f"[{i}] {res.get('title', '')}\n"
            formatted_results += f"    Detalle: {res.get('body', '')}\n"
            
        return formatted_results
    except Exception as e:
        return f"Error buscando en GitHub: {str(e)}"