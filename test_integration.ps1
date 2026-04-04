#!/bin/bash
# FalconsScan AI - Integration Test Script
# Tests all components are properly configured

param(
    [switch]$SkipBackend = $false,
    [switch]$SkipFrontend = $false,
    [switch]$Verbose = $false
)

# Colors
$Green = 'Green'
$Red = 'Red'
$Yellow = 'Yellow'
$Cyan = 'Cyan'

function Write-Status {
    param([string]$Message, [string]$Status)
    if ($Status -eq "OK") {
        Write-Host "✓ $Message" -ForegroundColor $Green
    } elseif ($Status -eq "FAIL") {
        Write-Host "✗ $Message" -ForegroundColor $Red
    } else {
        Write-Host "ℹ $Message" -ForegroundColor $Cyan
    }
}

Write-Host "`n" -BackgroundColor Black
Write-Host "================================================" -BackgroundColor Black
Write-Host " FalconsScan AI - Integration Test" -BackgroundColor Black
Write-Host "================================================" -BackgroundColor Black

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor $Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Status "Python found: $pythonVersion" "OK"
} else {
    Write-Status "Python not found" "FAIL"
    exit 1
}

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor $Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Status "Node.js found: $nodeVersion" "OK"
} else {
    Write-Status "Node.js not found" "FAIL"
    exit 1
}

# Check model file
Write-Host "`nChecking Model file..." -ForegroundColor $Yellow
if (Test-Path "models\sickle_classifier.pth") {
    $modelSize = (Get-Item "models\sickle_classifier.pth").Length / 1MB
    Write-Status "Model file found: ${modelSize:N2}MB" "OK"
} else {
    Write-Status "Model file not found at models/sickle_classifier.pth" "FAIL"
}

# Check Python dependencies
if (-not $SkipBackend) {
    Write-Host "`nChecking Python dependencies..." -ForegroundColor $Yellow
    python -c "import torch, fastapi, uvicorn; print('OK')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Python dependencies installed" "OK"
    } else {
        Write-Status "Python dependencies missing - Run: pip install -r requirements.txt" "FAIL"
    }
}

# Check NPM dependencies
if (-not $SkipFrontend) {
    Write-Host "`nChecking npm dependencies..." -ForegroundColor $Yellow
    if (Test-Path "SICKLE-CELL-UI\sickle-cell-ui\node_modules") {
        Write-Status "npm dependencies installed" "OK"
    } else {
        Write-Status "npm dependencies missing - Run: npm install" "FAIL"
    }
}

# Check Backend API
if (-not $SkipBackend) {
    Write-Host "`nChecking Backend API..." -ForegroundColor $Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Status "Backend API is running" "OK"
        } else {
            Write-Status "Backend API not responding" "FAIL"
        }
    } catch {
        Write-Status "Backend API not reachable at http://localhost:8000" "FAIL"
        Write-Status "To start: .\start_backend.ps1" "INFO"
    }
}

# Check Frontend
if (-not $SkipFrontend) {
    Write-Host "`nChecking Frontend..." -ForegroundColor $Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Status "Frontend is running" "OK"
        } else {
            Write-Status "Frontend not responding" "FAIL"
        }
    } catch {
        Write-Status "Frontend not reachable at http://localhost:3000" "FAIL"
        Write-Status "To start: .\start_frontend.ps1" "INFO"
    }
}

Write-Host "`n================================================" -ForegroundColor $Green
Write-Host "Test Complete!" -ForegroundColor $Green
Write-Host "================================================" -ForegroundColor $Green

Write-Host "`nNext Steps:" -ForegroundColor $Yellow
if ($SkipBackend -eq $false) {
    Write-Host "1. Start Backend: .\start_backend.ps1" -ForegroundColor $Cyan
}
if ($SkipFrontend -eq $false) {
    Write-Host "2. Start Frontend: .\start_frontend.ps1" -ForegroundColor $Cyan
}
Write-Host "3. Open http://localhost:3000 in browser" -ForegroundColor $Cyan
Write-Host "4. Accept medical disclaimer" -ForegroundColor $Cyan
Write-Host "5. Test with image or lab values" -ForegroundColor $Cyan

Write-Host "`n"
