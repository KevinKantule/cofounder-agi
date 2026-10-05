# business_validation.py
import time
from llm_chain import query_cofounder_brain
from web_tools import search_web, search_github_repos

AGENT_SPECIALIZATIONS = {
    "business_strategist": {
        "prompt": (
            "Eres el Cofundador Estratega y Abogado del Diablo. Tu rol es ANTI-COMPLACENCIA. "
            "No estás aquí para aplaudir ideas, sino para someterlas a un test de estrés brutal. "
            "Analiza los datos de mercado y competencia que se te proporcionan. "
            "Identifica por qué la idea podría fallar financieramente, técnica o logísticamente. "
            "Si hay hardware involucrado, cuestiona los costos (BOM) y la viabilidad de manufactura. "
            "Finalmente, propón un pivote o modelo de negocio más robusto."
        ),
        "preferred_model": "gemini/gemini-3.1-pro-preview" # Requiere alto razonamiento
    },
    "open_source_explorer": {
        "prompt": (
            "Eres el Arquitecto de Integración. Revisa los proyectos Open-Source encontrados. "
            "Propón cómo usar estas herramientas (simuladores, frameworks, librerías) en lugar de "
            "programar desde cero. Destaca si las licencias suelen ser amigables para uso comercial."
        ),
        "preferred_model": "openrouter/qwen/qwen3.8-max"
    }
}

def run_sub_agent(role: str, prompt: str) -> str:
    spec = AGENT_SPECIALIZATIONS.get(role)
    messages = [
        {"role": "system", "content": spec["prompt"]},
        {"role": "user", "content": prompt}
    ]
    return query_cofounder_brain(messages, preferred_model=spec["preferred_model"])

def evaluate_business_idea(idea: str):
    print(f"🎯 [Orquestador de Negocios] Evaluando idea:\n'{idea}'\n")
    
    print("🌐 [Web Scraper] Buscando competidores y viabilidad en el mercado...")
    market_data = search_web(f"competidores viabilidad comercial: {idea}")
    time.sleep(2) # Evitar rate limits del buscador
    
    print("🐙 [Web Scraper] Buscando alternativas Open-Source en GitHub...")
    github_data = search_github_repos(f"open source {idea}")
    
    print("\n🧐 [Sub-Agente: Abogado del Diablo] Analizando viabilidad...")
    prompt_strategist = f"IDEA DE NEGOCIO:\n{idea}\n\nDATOS DEL MERCADO ENCONTRADOS:\n{market_data}"
    business_report = run_sub_agent("business_strategist", prompt_strategist)
    print(f"\n--- DICTAMEN DE NEGOCIO (ANTI-COMPLACENCIA) ---\n{business_report}\n")
    
    print("🏗️ [Sub-Agente: Explorador Open-Source] Analizando integraciones...")
    prompt_explorer = f"IDEA DE NEGOCIO:\n{idea}\n\nPROYECTOS GITHUB ENCONTRADOS:\n{github_data}"
    tech_report = run_sub_agent("open_source_explorer", prompt_explorer)
    print(f"\n--- PROPUESTA TECNOLÓGICA OPEN-SOURCE ---\n{tech_report}\n")

if __name__ == "__main__":
    # Idea de prueba diseñada para poner al límite al agente con hardware y software
    idea_de_prueba = (
        "Quiero desarrollar un sistema IoT comercial basado en microcontroladores de bajo costo "
        "para automatizar el riego y monitoreo térmico en la germinación de cultivos caseros "
        "como almendros de mar y papayas. Incluiría una app móvil con IA."
    )
    evaluate_business_idea(idea_de_prueba)