@echo off
REM Cloudflare Tunnel Setup for FalconsScan AI
REM Tunnels port 9000 (reverse proxy) to the internet

echo.
echo ========================================
echo Cloudflare Tunnel - FalconsScan AI
echo ========================================
echo.

REM Download cloudflared
echo Step 1: Downloading cloudflared...
powershell -Command "(New-Object System.Net.ServicePointManager).SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflare-cli/releases/download/v2024.2.1/cloudflared-windows-amd64.exe' -OutFile 'C:\cloudflared.exe' -ErrorAction SilentlyContinue"

if exist C:\cloudflared.exe (
    echo ✓ cloudflared downloaded
) else (
    echo.
    echo ERROR: Download failed. Please:
    echo 1. Download from: https://github.com/cloudflare/cloudflare-cli/releases
    echo 2. Save as: C:\cloudflared.exe
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Login to Cloudflare
echo.
echo Step 2: Login to Cloudflare...
echo Opening browser for login...
C:\cloudflared.exe tunnel login

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Login failed
    pause
    exit /b 1
)

REM Display tunnel info
echo.
echo Step 3: Creating tunnel...
REM List existing tunnels to get the name
C:\cloudflared.exe tunnel list

echo.
echo Your tunnel is created! Now starting...
echo.

REM Start tunnel for port 9000
echo Starting Cloudflare tunnel for port 9000...
echo.
cls
C:\cloudflared.exe tunnel run --url http://localhost:9000

pause
