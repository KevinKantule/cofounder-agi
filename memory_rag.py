import lancedb
import requests
import json
import os
from typing import List, Dict, Any
from event_bridge import emit_event

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
DB_PATH = ".lancedb_data"

class LocalVectorMemory:
    def __init__(self, db_path: str = DB_PATH):
        # Conexión embebida a LanceDB (almacenamiento ligero en disco)
        self.db = lancedb.connect(db_path)
        self.table_name = "cofounder_memory"
        self._ensure_table_exists()

    def _get_embedding(self, text: str) -> List[float]:
        """Obtiene el vector embedding usando nomic-embed-text local vía Ollama."""
        payload = {
            "model": "nomic-embed-text",
            "prompt": text
        }
        try:
            res = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=10)
            if res.status_code == 200:
                return res.json().get("embedding", [])
        except Exception as e:
            print(f"⚠️ Error obteniendo embeddings de Ollama: {e}")
        return []

    def _ensure_table_exists(self):
        """Crea la tabla inicial en LanceDB si no existe."""
        if self.table_name not in self.db.table_names():
            # Crear tabla vacía con un vector de prueba para definir el esquema (dimensiones de nomic-embed-text = 768)
            dummy_vec = [0.0] * 768
            initial_data = [{
                "vector": dummy_vec,
                "text": "Sistema de Memoria Inicializado",
                "category": "system_init",
                "metadata": json.dumps({"source": "init"})
            }]
            self.db.create_table(self.table_name, data=initial_data)

    def add_memory(self, text: str, category: str = "general_rule", metadata: Dict[str, Any] = None):
        """Guarda un fragmento de contexto o regla en la base de datos vectorial."""
        vector = self._get_embedding(text)
        if not vector:
            print("❌ No se pudo generar el vector. Memoria no guardada.")
            return False

        meta_json = json.dumps(metadata if metadata else {})
        tbl = self.db.open_table(self.table_name)
        tbl.add([{
            "vector": vector,
            "text": text,
            "category": category,
            "metadata": meta_json
        }])
        print(f"🧠 Memoria guardada exitosamente en LanceDB: [{category}] '{text[:40]}...'")
        return True

    def query_memory(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Busca en LanceDB los recuerdos o reglas más relevantes para la consulta actual."""
        emit_event("memory", "working", "hipocampo", "Consultando memoria vectorial")
        query_vec = self._get_embedding(query)
        if not query_vec:
            emit_event("memory", "error", "hipocampo", "No se pudo generar el embedding")
            return []

        tbl = self.db.open_table(self.table_name)
        # Búsqueda por distancia coseno nativa en LanceDB
        results = tbl.search(query_vec).limit(limit).to_list()
        
        # Filtrar la inicialización del sistema si aparece
        filtered = [r for r in results if r.get("category") != "system_init"]
        emit_event("memory", "success", "hipocampo", f"{len(filtered)} recuerdos recuperados")
        return filtered

# --- PRUEBA RÁPIDA DEL SISTEMA DE MEMORIA LOCAL ---
if __name__ == "__main__":
    print("🧪 Probando Memoria RAG Local (LanceDB + nomic-embed-text)...\n")
    
    memory = LocalVectorMemory()
    
    # 1. Guardar algunas reglas históricas del proyecto
    memory.add_memory(
        "Regla de Código: Utilizar siempre FastAPI con Tipado Pydantic estricto en el backend.",
        category="architecture_rule"
    )
    memory.add_memory(
        "Regla de Seguridad: No exponer credenciales ni contraseñas en el archivo .env sin cifrado.",
        category="security_rule"
    )
    
    # 2. Consultar memoria
    consulta = "¿Cómo debemos estructurar las APIs del backend?"
    print(f"\n🔍 Consultando memoria para: '{consulta}'...")
    recuerdos = memory.query_memory(consulta, limit=2)
    
    for idx, r in enumerate(recuerdos, 1):
        print(f"\nRecuerdo #{idx}:")
        print(f" - Texto: {r['text']}")
        print(f" - Categoria: {r['category']}")
