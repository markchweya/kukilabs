param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Virtual environment not found. Creating .venv with your default Python..."
    python -m venv (Join-Path $ProjectRoot ".venv")
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if ($Install) {
    Write-Host "Installing/updating dependencies..."
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
}
else {
    Write-Host "Skipping dependency install. Use .\run_kuki.ps1 -Install after changing requirements."
}

$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$ProjectRoot;$env:PYTHONPATH"
}
else {
    $ProjectRoot
}

# Run outside the OneDrive-backed repo folder so Streamlit does not read a stale
# project .streamlit/config.toml placeholder.
Push-Location $env:USERPROFILE
try {
    & $Python -m streamlit run (Join-Path $ProjectRoot "app.py")
}
finally {
    Pop-Location
}
