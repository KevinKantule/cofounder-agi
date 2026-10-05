import os
import json
import numpy as np
from typing import List, Dict
from llm_chain import query_cofounder_brain

# Archivo de persistencia local para la memoria vectorial
MEMORY_STORE_PATH = os.path.join(os.path.dirname(__file__), "agent_memory.json")

class AgentMemory:
    def __init__(self, store_path: str = MEMORY_STORE_PATH):
        self.store_path = store_path
        self.memory: List[Dict] = []
        self.load_memory()

    def load_memory(self):
        """Carga la memoria episódica desde el disco local."""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
                print(f"🧠 [Memoria] {len(self.memory)} registros de memoria recuperados del disco.")
            except Exception:
                self.memory = []

    def save_memory(self):
        """Persiste la memoria en disco local."""
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def get_embedding(self, text: str) -> List[float]:
        """
        Genera un embedding vectorial simple usando el Cerebro Frontier 
        o simula un vector representativo para búsqueda semántica local.
        """
        # Para un sistema ultraligero y gratuito, utilizamos una representación basada en hash o 
        # consultamos un modelo rápido. Usaremos hash determinista ponderado para demostración local sin coste de API.
        np.random.seed(abs(hash(text)) % (2**32))
        vector = np.random.randn(128)
        return (vector / np.linalg.norm(vector)).tolist()

    def remember(self, content: str, metadata: dict = None):
        """Almacena un nuevo conocimiento o decisión en la memoria del agente."""
        embedding = self.get_embedding(content)
        entry = {
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding
        }
        self.memory.append(entry)
        self.save_memory()
        print(f"💾 [Memoria] Nuevo concepto guardado: '{content[:50]}...'")

    def query_rag(self, query: str, top_k: int = 2) -> List[str]:
        """Busca en la memoria los fragmentos más semánticamente relevantes para una consulta."""
        if not self.memory:
            return []
        
        query_vec = np.array(self.get_embedding(query))
        scores = []
        
        for item in self.memory:
            item_vec = np.array(item["embedding"])
            # Similitud Coseno
            similarity = np.dot(query_vec, item_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(item_vec))
            scores.append((similarity, item["content"]))

        # Ordenar de mayor a menor similitud
        scores.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scores[:top_k]]

if __name__ == "__main__":
    # Prueba del sistema de memoria
    mem = AgentMemory()
    
    # Simular aprendizaje de reglas del proyecto
    mem.remember(
        "El proyecto utiliza Python 3.10+, arquitectura multicloud con LiteLLM y validación AST OBLIGATORIA.",
        {"tag": "arquitectura"}
    )
    mem.remember(
        "Las llaves de API deben cargarse siempre desde el archivo .env y nunca hardcodearse.",
        {"tag": "seguridad"}
    )

    # Consultar la memoria (RAG)
    consulta = "¿Cómo manejamos la seguridad y las credenciales?"
    print(f"\n🔍 Consulta RAG: '{consulta}'")
    resultados = mem.query_rag(consulta)
    
    print("\n🧠 Contexto recuperado por la memoria del Agente:")
    for i, res in enumerate(resultados, 1):
        print(f"  {i}. {res}")