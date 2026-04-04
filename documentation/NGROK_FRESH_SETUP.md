# 🆕 FalconsScan AI - Fresh ngrok Setup

## Step 1: Download ngrok (if not already installed)

### Option A: Download Directly (Recommended)
1. Go to: https://ngrok.com/download
2. Select: **Windows** → Download the installer
3. Run the installer and choose installation location
4. ngrok will be added to your system PATH automatically

### Option B: Windows Package Manager
```powershell
winget install ngrok
```

## Step 2: Verify Installation

Open PowerShell and run:
```powershell
ngrok --version
```

Should print: `ngrok version X.X.X`

## Step 3: Create Free ngrok Account

1. Go to: https://ngrok.com/sign-up
2. Create a **FREE** account (no credit card needed!)
3. After signup, go to Dashboard: https://dashboard.ngrok.com
4. Copy your **Auth Token**

## Step 4: Configure ngrok with Your Auth Token

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

Replace `YOUR_AUTH_TOKEN_HERE` with your actual token from step 3.

## Step 5: Run Fresh ngrok Setup

```powershell
cd d:\sickle-cell-ai
.\deploy_ngrok_fresh.ps1
```

---

## What This Does

✅ **3 Terminal Windows Open Automatically:**
1. **Terminal 1**: FastAPI Backend (port 8000)
2. **Terminal 2**: React Frontend (port 3000)  
3. **Terminal 3**: ngrok tunneling both ports

✅ **Public URLs Created:**
- Frontend: `https://YOUR-RANDOM-NAME.ngrok-free.app`
- Backend: `https://YOUR-OTHER-NAME.ngrok-free.app`

✅ **View Live Tunnels:**
- Dashboard: http://localhost:4040

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "ngrok command not found" | Install ngrok from https://ngrok.com/download |
| "Invalid auth token" | Get your token from https://dashboard.ngrok.com |
| "Port already in use" | Close other terminals using ports 3000/8000 |
| "ngrok connection timeout" | Check your internet connection |

---

## Access Your App

### From Android Phone
1. Copy the **Frontend** `https://` URL from the output
2. Open Chrome on your phone
3. Paste the URL → Accept disclaimer → Use app!

### From PC
- Open: `http://localhost:3000` (local access)
- API Docs: `http://localhost:8000/docs` (local access)

---

## ⚠️ Important Notes

- **Free Tier Limits**: 20 requests/minute (plenty for testing!)
- **URLs Change on Restart**: Get new URLs each time you run the script
- **Keep Terminal Open**: Close terminal = tunnel closes
- **Session Duration**: 2 hours max per session, then restart

**→ Ready? Run:** `.\deploy_ngrok_fresh.ps1`
