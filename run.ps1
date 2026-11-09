# Start Kuki on Windows: sets up Python, builds the web app once, runs the server.
#   .\run.ps1            start Kuki at http://127.0.0.1:8765
#   .\run.ps1 -Full      also install optional photo OCR + recording transcription
param([switch]$Full)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Setting up Python environment (first run only)..."
    py -3 -m venv backend\.venv
}
& $py -m pip install -q -r backend\requirements.txt
if ($Full) { & $py -m pip install -q -r backend\requirements-optional.txt }

if (-not (Test-Path "frontend\dist\index.html")) {
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "Building the web app (first run only)..."
        Push-Location frontend; npm ci --silent; npm run build --silent; Pop-Location
    } else {
        Write-Warning "npm not found: install Node.js 20+ to build the web app, or run the API alone."
    }
}

try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 http://127.0.0.1:11434/api/tags | Out-Null }
catch { Write-Host "Note: Ollama isn't running. Kuki will work in offline mode until you start it." }

Write-Host "Kuki is starting at http://127.0.0.1:8765"
Set-Location backend
& ".venv\Scripts\python.exe" -m kuki
