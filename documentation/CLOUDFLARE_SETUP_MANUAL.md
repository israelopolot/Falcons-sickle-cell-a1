# FalconsScan AI - Cloudflare Tunnel Setup (Manual)

## Quick Setup - 3 Steps (5 minutes)

### Step 1: Download cloudflared
1. Go to: https://bin.equinox.io/c/VdrWfqd0Fc/cloudflared-stable-windows-amd64.exe
2. **Save the file as:** `C:\cloudflared.exe`

### Step 2: Login to Cloudflare (FREE)
Open PowerShell and type:
```powershell
C:\cloudflared.exe tunnel login
```
- This opens a browser
- Sign up or login (it's FREE)
- Authorize the request
- The tunnel will be created automatically

### Step 3: Start Your Public Tunnel
```powershell
C:\cloudflared.exe tunnel run --url http://localhost:9000
```

**That's it!** You'll see output like:
```
2026-03-28 21:45:33 INF |--- Tunnel token: ...
2026-03-28 21:45:34 INF |  Your tunnel is now connected to the Cloudflare edge!
2026-03-28 21:45:35 INF |  https://yellow-example-123.trycloudflare.com is now available
```

---

## Use the HTTPS URL on Your Phone

Copy the URL from step 3 output (example: `https://yellow-example-123.trycloudflare.com`)

**On your Android phone:**
1. Open Chrome
2. Paste the HTTPS URL
3. Accept disclaimer
4. Test lab values!

---

## Why This Works

- ✅ Port 9000 (reverse proxy) is already working on your PC
- ✅ Cloudflare tunnels it securely to the internet
- ✅ Your phone on public WiFi can now access it
- ✅ FREE and unlimited!

---

## Keep It Running

**Important:** Keep the PowerShell window open while using the app. The tunnel stops when you close it.

**New URL each time:** Every time you restart, you get a new HTTPS URL. Just copy the new one and use on your phone.

---

## Next Steps

1. Download cloudflared from: https://bin.equinox.io/c/VdrWfqd0Fc/cloudflared-stable-windows-amd64.exe
2. Run: `C:\cloudflared.exe tunnel login`
3. Run: `C:\cloudflared.exe tunnel run --url http://localhost:9000`
4. Copy the HTTPS URL and use on your phone!

**Let me know once you have cloudflared.exe downloaded, and I can help with the rest!** 🚀
