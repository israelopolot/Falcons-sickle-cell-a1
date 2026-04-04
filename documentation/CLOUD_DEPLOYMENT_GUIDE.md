# Cloud Deployment Options for FalconsScan AI

## Quick Links
- **Google Cloud Run** (Recommended - Free tier available)
- **Heroku** (Simple, but paid now)
- **AWS Elastic Beanstalk** (More control)
- **Azure Container Instances** (Pay-per-use)
- **DigitalOcean App Platform** ($5/month)

---

## 🔥 Option 1: Google Cloud Run (RECOMMENDED)

**Cost:** Free tier (2M requests/month)  
**Setup Time:** 15-20 minutes  
**Performance:** Excellent globally

### **Step 1: Install Google Cloud CLI**

```bash
# Download from https://cloud.google.com/sdk/docs/install
# Or use Chocolatey (Windows)
choco install google-cloud-sdk
```

### **Step 2: Initialize Google Cloud**

```bash
gcloud init
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### **Step 3: Build & Push Docker Image**

```bash
# Set variables
$PROJECT_ID = "your-project-id"
$SERVICE_NAME = "sickle-cell-ai"
$REGION = "us-central1"

# Build image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Or use Cloud Build (faster)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### **Step 4: Deploy to Cloud Run**

```bash
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest `
  --platform managed `
  --region $REGION `
  --memory 2Gi `
  --timeout 600 `
  --allow-unauthenticated
```

**Result:**
- ✅ Public URL: `https://sickle-cell-ai-XXXXX.run.app`
- ✅ Auto-scaling
- ✅ Free HTTPS
- ✅ Free tier: 2M requests/month

**Android Access:**
- Open: `https://sickle-cell-ai-XXXXX.run.app`
- Works globally on any network

---

## 📦 Option 2: Heroku (Simple but Paid)

**Cost:** $7+/month  
**Setup Time:** 10 minutes

### **Prerequisites**

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login
```

### **Deployment**

```bash
# Create app
heroku create sickle-cell-ai

# Add buildpacks
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Deploy
git push heroku main

# Open app
heroku open
```

**Result:** `https://sickle-cell-ai.herokuapp.com`

---

## ☁️ Option 3: AWS Elastic Beanstalk

**Cost:** Variable (often $15-30/month)  
**Setup Time:** 20-30 minutes

### **Steps**

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker sickle-cell-ai

# Create environment
eb create sickle-cell-ai-env

# Deploy
eb deploy
```

**Result:** `http://sickle-cell-ai-env.elasticbeanstalk.com`

---

## 🚀 Option 4: DigitalOcean App Platform

**Cost:** $5+ /month  
**Setup Time:** 15 minutes

### **Steps**

1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub repo
4. Select Dockerfile
5. Set resources (2GB RAM)
6. Deploy!

**Result:** `https://sickle-cell-ai.ondigitalocean.app`

---

## 📋 Deployment Comparison

| Platform | Cost | Setup | Performance | Auto-scale | Uptime |
|----------|------|-------|-------------|-----------|--------|
| **Google Cloud Run** | Free tier | 15 min | Excellent | ✅ | 99.95% |
| **Heroku** | $7+/mo | 10 min | Good | ✅ | 99.9% |
| **AWS EB** | $15+/mo | 30 min | Excellent | ✅ | 99.99% |
| **Azure** | Pay/use | 20 min | Excellent | ✅ | 99.95% |
| **DigitalOcean** | $5+/mo | 15 min | Good | ✅ | 99.95% |

---

## 🎯 Recommended Path

### **For Testing (Next 2 weeks)**
→ Use **ngrok** (Option 2 in main guide)
→ Run: `.\deploy_ngrok.ps1`

### **For Demo/Proof of Concept (2-8 weeks)**
→ Deploy to **Google Cloud Run** (FREE)
→ Follow steps above

### **For Production (Long-term)**
→ Deploy to **Google Cloud Run** or **AWS**
→ Set up custom domain
→ Enable authentication
→ Monitor metrics

---

## 🔒 Security Considerations

Once deployed, consider:

1. **Add Authentication**
   ```python
   # Add user login to app/main.py
   from fastapi_auth0 import Auth0
   ```

2. **Enable CORS Properly**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Specific domain
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Use HTTPS Only**
   - All cloud platforms provide free HTTPS
   - Don't use HTTP in production

4. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   ```

5. **Enable Health Monitoring**
   - Uptime monitoring
   - Error tracking (Sentry)
   - Performance monitoring (DataDog)

---

## 📱 After Deployment

### **For Android Users**

1. **Via Browser:**
   - Open: `https://your-deployed-url.com`
   - Accept disclaimer
   - Use normally

2. **Install as PWA (Home Screen App):**
   - Open app in Chrome
   - Menu (3 dots) → "Install app"
   - App appears on home screen like native app

3. **Share:**
   - Short URL: Use TinyURL or bit.ly
   - QR Code: Generate at qr-code-generator.com

---

## 📞 Getting Help

- **Google Cloud Run:** https://cloud.google.com/run/docs
- **Heroku:** https://devcenter.heroku.com/
- **Docker:** https://docs.docker.com/
- **ngrok:** https://ngrok.com/docs

---

## 🚀 Next Steps

1. **Immediate (Today):** Test locally on WiFi
2. **This Week:** Set up ngrok for remote demo
3. **This Month:** Deploy to Google Cloud Run
4. **Production:** Add auth, custom domain, monitoring

Need specific help with deployment? Let me know which platform you want to use!
