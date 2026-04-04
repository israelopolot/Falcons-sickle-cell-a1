# FalconsScan AI Full Stack Stop Script for Windows PowerShell
# Stops uvicorn, npm, and ngrok if running.

function Log($msg, $color='White') { Write-Host $msg -ForegroundColor $color }

Log "================================================" Green
Log "FalconsScan AI - Full Stack Stop" Green
Log "================================================" Green

$processFilters = @(
    @{name='uvicorn'; pattern='uvicorn'},
    @{name='npm'; pattern='npm'},
    @{name='ngrok'; pattern='ngrok'}
)

foreach ($f in $processFilters) {
    $procs = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "*$($f.pattern)*" }
    if ($procs) {
        foreach ($p in $procs) {
            Log "Stopping $($f.name): PID $($p.Id) ($($p.ProcessName))" Yellow
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        }
    } else {
        Log "$($f.name) not running." Gray
    }
}

Log "\nAll known service processes were requested to stop." Green
Log "Check Task Manager if any remain." Yellow
