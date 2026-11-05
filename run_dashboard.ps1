# Ejecuta el dashboard con el entorno que contiene las dependencias del proyecto.
$projectPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"

if (-not (Test-Path $projectPython)) {
    Write-Error "No se encontró venv\\Scripts\\python.exe. Crea el entorno e instala: python -m pip install -r requirements.txt"
    exit 1
}

& $projectPython -m streamlit run (Join-Path $PSScriptRoot "dashboard.py")
