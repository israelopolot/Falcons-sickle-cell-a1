# FalconsScan AI - Clean ngrok Installation

This script will help you install ngrok freshly without any old configurations.

## Quick Start (Copy & Paste)

### 1️⃣ If ngrok is NOT installed yet:

**Option A: Direct Download (Recommended)**
```powershell
# Download and extract ngrok
$url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
$zip = "$env:TEMP\ngrok.zip"
$dest = "C:\ngrok"

New-Item -ItemType Directory -Path $dest -Force | Out-Null
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $dest -Force
Remove-Item $zip

# Add to PATH
$env:Path += ";C:\ngrok"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::User)

# Verify
C:\ngrok\ngrok --version
```

**Option B: Windows Package Manager**
```powershell
winget install ngrok
```

---

### 2️⃣ Configure ngrok with Your Auth Token

Go to: **https://dashboard.ngrok.com**
1. Sign up for FREE account
2. Copy your Auth Token
3. In PowerShell, run:

```powershell
ngrok config add-authtoken YOUR_TOKEN_HERE
```

---

### 3️⃣ Run Fresh Setup

```powershell
cd d:\sickle-cell-ai
.\deploy_ngrok_fresh.ps1
```

This will:
- ✓ Start FastAPI backend (port 8000)
- ✓ Start React frontend (port 3000)  
- ✓ Start ngrok tunnels (creates public HTTPS URLs)
- ✓ Show you the public URLs to access from phone

---

## Verify Installation Worked

After running the script:

1. **Check ngrok status**: http://localhost:4040
2. **Check backend**: http://localhost:8000/health
3. **Check frontend**: http://localhost:3000
4. **Check tunnels**: Look at http://localhost:4040 for HTTPS URLs

---

## If Something Goes Wrong

### "ngrok: command not found"
```powershell
# Install via direct download (Option A above)
# OR verify PATH: $env:Path -split ';' | Select-String ngrok
```

### "Invalid auth token"
```powershell
# Get new token from https://dashboard.ngrok.com
# Clear old config
Remove-Item -Path $env:USERPROFILE\.ngrok2 -Recurse -Force -ErrorAction SilentlyContinue
# Reconfigure
ngrok config add-authtoken YOUR_NEW_TOKEN
```

### "Ports 3000/8000 already in use"
```powershell
# Find and kill processes
netstat -ano | findstr ":3000\|:8000"
taskkill /PID <PID> /F
```

---

## Access Your App

### 🔗 From Android Phone
1. Run: `.\deploy_ngrok_fresh.ps1`
2. Open http://localhost:4040 → Find Frontend HTTPS URL
3. On phone: Open that HTTPS URL in Chrome
4. Accept disclaimer → Use app!

### 💻 From Your PC (Local)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

**Questions?** Check the logs in each terminal window!
