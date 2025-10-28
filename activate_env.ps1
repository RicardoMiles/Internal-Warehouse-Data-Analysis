$VENV_DIR = "venv"

if (Test-Path "$VENV_DIR\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment from $VENV_DIR..."
    & "$VENV_DIR\Scripts\Activate.ps1"
} else {
    Write-Host "Error: Virtual environment folder '$VENV_DIR' not found."
}
