param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$KukiLocalRoot = Join-Path $env:LOCALAPPDATA "KukiAI"
$VenvRoot = Join-Path $KukiLocalRoot ".venv"
$Python = Join-Path $VenvRoot "Scripts\python.exe"
$env:PYTHONPYCACHEPREFIX = Join-Path $env:TEMP "kuki-pycache"

function Get-PreferredPythonCommand {
    $candidates = @(
        @("python"),
        @("py", "-3.12"),
        @("py", "-3.11")
    )

    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        $args = @()
        if ($candidate.Length -gt 1) {
            $args = $candidate[1..($candidate.Length - 1)]
        }

        $job = Start-Job -ScriptBlock {
            param($Exe, $Args)
            & $Exe @($Args + @("--version"))
            if ($LASTEXITCODE -ne 0) {
                throw "Python exited with code $LASTEXITCODE"
            }
        } -ArgumentList $exe, $args

        if (-not (Wait-Job $job -Timeout 10)) {
            Stop-Job $job -ErrorAction SilentlyContinue
            Remove-Job $job -Force -ErrorAction SilentlyContinue
            continue
        }

        Receive-Job $job -ErrorAction SilentlyContinue | Out-Null
        $state = $job.State
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if ($state -eq "Completed") {
            return @{ Exe = $exe; Args = $args }
        }
        else {
            continue
        }
    }

    throw "No compatible Python command was found. Install Python 3.11 or 3.12, then rerun this script."
}

function Test-VenvPython {
    param([string]$PythonPath)

    if (-not (Test-Path $PythonPath)) {
        return $false
    }

    $job = Start-Job -ScriptBlock {
        param($Path)
        & $Path --version
        if ($LASTEXITCODE -ne 0) {
            throw "Python exited with code $LASTEXITCODE"
        }
    } -ArgumentList $PythonPath

    if (-not (Wait-Job $job -Timeout 10)) {
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        return $false
    }

    Receive-Job $job -ErrorAction SilentlyContinue | Out-Null
    $state = $job.State
    Remove-Job $job -Force -ErrorAction SilentlyContinue
    return $state -eq "Completed"
}

function New-KukiVenv {
    $pythonCommand = Get-PreferredPythonCommand
    New-Item -ItemType Directory -Path $KukiLocalRoot -Force | Out-Null
    Write-Host "Creating .venv with $($pythonCommand.Exe) $($pythonCommand.Args -join ' ')..."
    & $pythonCommand.Exe @($pythonCommand.Args + @("-m", "venv", $VenvRoot))
}

$NeedsInstall = $Install

if (-not (Test-VenvPython $Python)) {
    if (Test-Path $VenvRoot) {
        $backup = Join-Path $KukiLocalRoot (".venv.broken-{0}" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
        Write-Host "Existing local virtual environment is not responding. Moving it to $backup"
        Move-Item -LiteralPath $VenvRoot -Destination $backup
    }
    else {
        Write-Host "Local virtual environment not found."
    }

    New-KukiVenv
    $NeedsInstall = $true
}

if ($NeedsInstall) {
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
