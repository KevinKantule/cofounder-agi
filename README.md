
# Cofounder AGI 🚀

Cofounder AGI es un sistema híbrido multi-agente autónomo diseñado para actuar como un "Cofundador Técnico" y Desarrollador de Software. El sistema automatiza la ideación de negocios, la escritura de código, revisión, ejecución y depuración utilizando un bucle de razonamiento ReAct con autorización humana en el ciclo (HITL).

## 🧠 Arquitectura del Proyecto

El sistema divide las capacidades de razonamiento para optimizar velocidad y memoria RAM:
*   **Orquestador y Estratega (Nube):** Utiliza un *fallback chain* jerárquico (Gemini 3.1 Pro, Groq, OpenRouter) para diseñar la arquitectura del software y analizar la viabilidad del negocio sin consumir recursos locales.
*   **Router Predictivo Local (Ollama):** Un modelo ultraligero que clasifica en milisegundos si el *prompt* es charla general o ingeniería técnica, ahorrando peticiones a la nube.
*   **Programador Ejecutor (Ollama):** Un agente especializado en código que procesa instrucciones complejas y escribe *scripts* de manera gratuita e ilimitada en local.
*   **Memoria Vectorial (LanceDB):** Base de datos *Zero-Copy* en disco que indexa contexto histórico y reglas de arquitectura mediante *embeddings* locales.
*   **Guardarraíles (Sandbox MCP):** Entorno de validación sintáctica (AST) que previene la ejecución de comandos destructivos en la máquina anfitriona.

## 📦 Dependencias e Instalación

**Requisitos previos:**
*   Python 3.10 o superior.
*   [Ollama](https://ollama.com/) instalado y ejecutándose en segundo plano.

**1. Clonar el repositorio y crear el entorno virtual:**
```bash
git clone [https://github.com/tu-usuario/cofounder-agi.git](https://github.com/tu-usuario/cofounder-agi.git)
cd cofounder-agi
python -m venv .venv

**2. Activar el entorno virtual:**
Windows: .\.venv\Scripts\Activate.ps1

Mac/Linux: source .venv/bin/activate

**3. Instalar las librerías necesarias:**
```bash
pip install smolagents litellm python-dotenv openai duckduckgo-search lancedb requests streamlit


⚙️ Configuración de Modelos y Ollama
El proyecto requiere descargar modelos específicos en tu instalación de Ollama para el Router, el Coder, el Asistente General y la Memoria Vectorial.

Abre una terminal y ejecuta los siguientes comandos para descargar el catálogo base:

```bash
ollama pull llama3.2:1b         # Router Predictivo (alta velocidad)
ollama pull qwen2.5-coder:7b    # Sub-Agente Coder (escritura de software)
ollama pull gemma:4b            # Sub-Agente Generalista/Analítico
ollama pull nomic-embed-text    # Motor de Embeddings para Memoria RAG LanceDB


🔐 Variables de Entorno
Copia el archivo de ejemplo y configúralo con tus credenciales:
1. Duplica el archivo .env.example y renómbralo a .env.
2. Consigue tus API Keys gratuitas en Google AI Studio, Groq Cloud y OpenRouter.
3. Reemplaza los valores en el archivo .env.


🚀 Ejecución y Ejemplo de Uso
Una vez configuradas las dependencias y descargados los modelos, levanta el panel de control interactivo (asegúrate de tener el entorno virtual activado):

```bash
streamlit run dashboard.py

Ejemplo de flujo básico en el Dashboard:
1. Se abrirá la interfaz en http://localhost:8501.
2. En la barra de chat, escribe un requerimiento técnico, por ejemplo: 
"SaaS para gestión de inventarios con FastAPI"
3. El Router Predictivo (llama3.2:1b) clasificará la intención como "Ingeniería".
4. El agente consultará a la Memoria Vectorial (LanceDB) por reglas históricas, evaluará la viabilidad web con el Abogado del Diablo, y enviará los requerimientos al Coder (qwen2.5-coder:7b).
5. Observarás en la barra lateral el dictamen del Reviewer auditando el código. Si es aprobado, el sistema pedirá tu confirmación en consola para guardar y probar el archivo físicamente.