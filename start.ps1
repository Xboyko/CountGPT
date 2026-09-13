# CountGPT — Windows PowerShell convenience launcher.
#
# This repo's venv is typically created in WSL (venv/bin/activate), not a
# native Windows venv (venv\Scripts\Activate.ps1). Prefer WSL so you reuse
# that environment and the Linux start.sh Ollama/WSL detection.
#
#   .\start.ps1
#   $env:START_RELOAD = "1"; .\start.ps1
#
# If PowerShell blocks scripts:
#   powershell -ExecutionPolicy Bypass -File .\start.ps1

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

function Test-WslCanSeeProject {
    if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
        return $false
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "start.sh"))) {
        return $false
    }
    # Current directory is the repo; WSL maps it when the tree is visible.
    & wsl -e test -f start.sh
    return ($LASTEXITCODE -eq 0)
}

if (Test-WslCanSeeProject) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  CountGPT — launching via WSL (venv is typically Linux)"
    Write-Host "  Open:  http://127.0.0.1:7860"
    Write-Host "============================================================"
    Write-Host ""
    & wsl -e bash start.sh
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "WSL + start.sh not available — native Windows fallback."
Write-Host "Note: this user's venv is typically WSL. Native path uses venv\Scripts."
Write-Host ""

if (-not $env:OLLAMA_HOST) {
    $env:OLLAMA_HOST = "http://127.0.0.1:11434"
}

$activate = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path -LiteralPath $activate) {
    . $activate
    Write-Host "Using existing Windows venv"
} else {
    Write-Host "Creating native venv (WSL venv cannot be reused here)..."
    python -m venv venv
    . $activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
}

if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
    python -m pip install -r requirements.txt
}

$pkl = Join-Path $PSScriptRoot "rules_with_embeddings.pkl"
if (-not (Test-Path -LiteralPath $pkl)) {
    Write-Host "rules_with_embeddings.pkl missing — running python setup_data.py"
    python setup_data.py
    if (-not (Test-Path -LiteralPath $pkl)) {
        Write-Error "Could not create rules_with_embeddings.pkl. Run: python setup_data.py"
        exit 1
    }
}

$reloadArgs = @()
if ($env:START_RELOAD -eq "1") {
    $reloadArgs = @("--reload")
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  CountGPT  ->  http://127.0.0.1:7860"
Write-Host "============================================================"
Write-Host "Local only — no public domain. Stop with Ctrl+C."
Write-Host ""

& uvicorn app:app --host 0.0.0.0 --port 7860 @reloadArgs
exit $LASTEXITCODE
