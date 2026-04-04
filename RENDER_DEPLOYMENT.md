# Render Deployment Guide

This project is configured for auto-deployment on Render with GitHub integration.

---

## Prerequisites

- GitHub account connected to Render (https://render.com)
- Repository pushed to GitHub: `https://github.com/allenmutskeine-crypto/sickle-cell-ai`

---

## Backend Deployment (FastAPI)

### 1. Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click `New +` → `Web Service`
3. Connect repository: select `allenmutskeine-crypto/sickle-cell-ai`
4. Configure:
   - **Name**: `sickle-cell-ai-backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free tier
5. Click `Create Web Service`

Render will auto-deploy whenever you push to `main` branch.

**Backend URL** (after deploy): `https://sickle-cell-ai-backend.onrender.com`

---

## Frontend Deployment (React)

### 1. Create Static Site on Render

1. Go to https://dashboard.render.com
2. Click `New +` → `Static Site`
3. Connect repository: select same repo
4. Configure:
   - **Name**: `sickle-cell-ai-frontend`
   - **Build Command**: `cd SICKLE-CELL-UI/sickle-cell-ui && npm install && npm run build`
   - **Publish Directory**: `SICKLE-CELL-UI/sickle-cell-ui/build`
   - **Plan**: Free tier
5. Click `Create Static Site`

Render will auto-deploy on push.

**Frontend URL** (after deploy): `https://sickle-cell-ai-frontend.onrender.com`

---

## Update Frontend to Call Backend

In `SICKLE-CELL-UI/sickle-cell-ui/src/App.js` (or API service file):

```javascript
// Use environment variable for API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Example API call:
fetch(`${API_URL}/health`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### Set Environment Variable on Render

In frontend Static Site settings:
- **Environment** → **Add Environment Variable**
  - Key: `REACT_APP_API_URL`
  - Value: `https://sickle-cell-ai-backend.onrender.com`
- Redeploy

---

## Enable Auto-Deploy

Both services auto-deploy on GitHub push by default.

To disable/manage:
- Service Settings → **Auto-Deploy**: toggle on/off

---

## Monitor & Logs

- Dashboard shows build & runtime logs
- Check **Logs** tab if deploy fails
- Common issues:
  - Missing environment variables
  - Port conflicts
  - Dependencies not in `requirements.txt`

---

## Free Tier Limits

- **Compute**: 750 hours/month (one service 24/7)
- **Bandwidth**: 100GB/month
- Services spin down after 15min inactivity (cold start ~30s)

---

## Next Steps After Deploy

1. Test backend: `https://sickle-cell-ai-backend.onrender.com/docs`
2. Test frontend: `https://sickle-cell-ai-frontend.onrender.com`
3. Update API calls to use backend URL
4. Test end-to-end image upload / lab value inference

---

## Troubleshooting

**Backend won't start** → Check `render.yaml` and `requirements.txt`
**Frontend build fails** → Check Node version compatibility, build command
**API calls fail** → Verify `REACT_APP_API_URL` is set correctly

---

For more: https://render.com/docs
