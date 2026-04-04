<#
Starter
#>
param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $projectRoot "SICKLE-CELL-UI\sickle-cell-ui"
$venvActivate = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"

function Log($msg, $color='White') { Write-Host $msg -ForegroundColor $color }

function Check-Command($cmd, $name) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Log "ERROR: $name not found. Please install and make sure it's on PATH." Red
        exit 1
    }
}

Log "================================================" Green
Log "Starting back end and front end" Green
Log "================================================" Green

if (-not $FrontendOnly) { Check-Command python "Python" }
if (-not $BackendOnly)  { Check-Command npm "npm" }

if (-not $BackendOnly) {
    Log "\nStarting backend..." Yellow
    $backCmd = "cd '$projectRoot'; if (Test-Path '$venvActivate') { & '$venvActivate' }; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    Start-Process -FilePath powershell.exe -ArgumentList "-NoExit", "-Command", $backCmd -WorkingDirectory $projectRoot
    Start-Sleep -Seconds 2
    Log "Backend should be available at http://localhost:8000" Green
}

if (-not $BackendOnly) {
    Log "\nStarting frontend..." Yellow
    $frontCmd = "cd '$frontendDir'; npm start"
    Start-Process -FilePath powershell.exe -ArgumentList "-NoExit", "-Command", $frontCmd -WorkingDirectory $frontendDir
    Start-Sleep -Seconds 2
    Log "Frontend should be available at http://localhost:3000" Green
}

Log "\nUse .\stop_backend.ps1 to stop backend/frontend processes by name." Cyan
Log "If you close windows manually, make sure the servers are stopped before restarting." Cyan
