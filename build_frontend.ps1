<#
Build the React frontend from the repository root.
Usage:
  .\build_frontend.ps1
#>

$frontendDir = Join-Path $PSScriptRoot 'SICKLE-CELL-UI\sickle-cell-ui'

Write-Host "Building frontend in: $frontendDir" -ForegroundColor Cyan
Set-Location $frontendDir

if (-not (Test-Path 'package.json')) {
    Write-Host 'ERROR: Frontend package.json not found in:' -ForegroundColor Red
    Write-Host $frontendDir -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path 'node_modules')) {
    Write-Host 'node_modules not found. Installing frontend dependencies...' -ForegroundColor Yellow
    npm install
}

Write-Host 'Running frontend build...' -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host 'Frontend build completed successfully.' -ForegroundColor Green
} else {
    Write-Host 'Frontend build failed. Check the output above for errors.' -ForegroundColor Red
    exit $LASTEXITCODE
}
