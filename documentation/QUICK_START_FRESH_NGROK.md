# FalconsScan AI - FRESH ngrok Setup Complete ✓

All old configurations have been cleared! Here's what to do next:

---

## ⚡ QUICK START (3 steps)

### Step 1: Install ngrok (If needed)

**Check if ngrok is installed:**
```powershell
ngrok --version
```

**If not installed, run THIS ONE COMMAND:**
```powershell
$url="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"; $zip="$env:TEMP\ngrok.zip"; $dest="C:\ngrok"; New-Item -ItemType Directory -Path $dest -Force | Out-Null; Invoke-WebRequest -Uri $url -OutFile $zip; Expand-Archive -Path $zip -DestinationPath $dest -Force; Remove-Item $zip; $env:Path += ";C:\ngrok"; [Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::User); C:\ngrok\ngrok --version
```

Or manually: https://ngrok.com/download (choose Windows)

---

### Step 2: Get Your Free Auth Token

1. Go to: **https://dashboard.ngrok.com**
2. Sign up for FREE account (no credit card!)
3. Look for **"Auth Token"** section
4. Copy your token (looks like: `2eV9...abc123...`)

Then configure ngrok:
```powershell
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual token!

---

### Step 3: Start Everything!

```powershell
cd d:\sickle-cell-ai
.\deploy_ngrok_fresh.ps1
```

This will open 3 new terminal windows:
- ✓ Backend (FastAPI on port 8000)
- ✓ Frontend (React on port 3000)
- ✓ ngrok (tunneling both ports)

---

## 📱 Access Your App

### From Android Phone
1. **Wait 30 seconds** for everything to start
2. Open browser: **http://localhost:4040** (on your PC)
3. Look for the **"Forwarding"** section
4. Copy the **Frontend HTTPS URL** (the one showing `https://...`)
5. On your phone, open that HTTPS URL in Chrome
6. Accept the medical disclaimer
7. **Done!** Upload blood cell images or enter lab values

### From Your PC (Local)
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## ✅ Verify Everything Works

After running `deploy_ngrok_fresh.ps1`:

**Check 1: All servers running?**
```powershell
# In a NEW terminal
Invoke-RestMethod http://localhost:8000/health
```
Should return: `{"status":"ok"}`

**Check 2: ngrok working?**
Open: `http://localhost:4040`
Look for "Forwarding" section with HTTPS URLs

**Check 3: Can you see frontend?**
Open: `http://localhost:3000` (should load FalconsScan AI)

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ngrok command not found" | Install ngrok (Step 1 above) |
| "Invalid auth token" | Get new token from https://dashboard.ngrok.com |
| "Ports in use" | Close other terminals or restart your PC |
| "Backend not responding" | Wait 15 seconds, sometimes slow to start |
| "Frontend not loading" | Check `http://localhost:3000` works locally first |

---

## 📊 Success Checklist

- [ ] ngrok installed (`ngrok --version` works)
- [ ] Auth token configured (`ngrok config show` shows token)
- [ ] `deploy_ngrok_fresh.ps1` ran successfully
- [ ] 3 new terminal windows opened
- [ ] `http://localhost:4040` shows active tunnels
- [ ] Can see HTTPS URLs in the Forwarding section
- [ ] Android phone can access the HTTPS URL
- [ ] App loads and shows medical disclaimer

---

## 📞 Still Having Issues?

**Check the 3 terminal windows for errors:**
1. Terminal 1: Backend output (look for "Uvicorn running on...")
2. Terminal 2: Frontend output (look for "webpack compiled...")
3. Terminal 3: ngrok output (look for "started tunnel")

Each should show "success" or "running" messages.

**Common issue:** Ports already in use
```powershell
# Kill everything on ports 3000 & 8000
Get-NetTCPConnection -LocalPort 3000, 8000 -ErrorAction SilentlyContinue | 
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Then try again: `.\deploy_ngrok_fresh.ps1`

---

**You're all set! Run:** `.\deploy_ngrok_fresh.ps1` 🚀
