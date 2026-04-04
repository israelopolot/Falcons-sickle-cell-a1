# FalconsScan AI - Mobile Deployment Guide

## 📱 Accessing the App on Android Phones

### **Option 1: Local Network (Same WiFi) - RECOMMENDED FOR TESTING**

#### **Your Local IP: `172.16.49.163`**

**Frontend URL:** `http://172.16.49.163:3000`  
**Backend API:** `http://172.16.49.163:8000`

**For Android Users on Same Network:**
1. Connect phone to **same WiFi network** as the computer running the servers
2. Open Chrome/Firefox browser on Android
3. Enter: `http://172.16.49.163:3000`
4. 🎉 App loads!

**Pros:** 
- ✅ Fast, no latency
- ✅ Works immediately
- ✅ No external account needed
- ✅ Secure (local network only)

**Cons:**
- ❌ Only works on same WiFi
- ❌ Not accessible from home (different network)

---

### **Option 2: ngrok - Global Internet Access**

Expose your local servers to the public internet with a unique public URL.

#### **Step 1: Expose Frontend with ngrok**

```bash
# In a new terminal
ngrok http 3000
```

This will show output like:
```
Session Status                online
Public URL                    https://1a2b3c4d5e6f.ngrok.io
```

**Share this URL:** Anyone worldwide can access your app:
```
https://1a2b3c4d5e6f.ngrok.io
```

#### **Step 2: Update Backend URL in App**

Edit the `.env` file in `SICKLE-CELL-UI/sickle-cell-ui/`:

```env
REACT_APP_API_URL=https://YOUR_NGROK_FRONTEND_URL
```

But wait - the frontend and backend are on different ports! You need to expose both:

#### **Best Approach: Use Reverse Proxy**

Create a simple proxy configuration that routes both:
- `/` → Frontend (port 3000)
- `/api/` → Backend (port 8000)

Or expose backend separately:

```bash
# Terminal 1 - Frontend
ngrok http 3000

# Terminal 2 - Backend (different ngrok account needed)
ngrok http 8000
```

Then update app to call backend API at the ngrok backend URL.

**Pros:**
- ✅ Global internet access
- ✅ Share URL with anyone worldwide
- ✅ Works on cellular (4G/5G)

**Cons:**
- ❌ ~200ms latency (you're routing through ngrok)
- ❌ Need ngrok account
- ❌ Free tier has rate limits
- ❌ URL changes on restart (unless paid account)

---

### **Option 3: Docker + Cloud Deployment (RECOMMENDED FOR PRODUCTION)**

Deploy to cloud platforms like Heroku, AWS, Google Cloud, or DigitalOcean.

#### **Step 1: Create Dockerfile**

```dockerfile
# Build stage for frontend
FROM node:16 AS frontend-builder
WORKDIR /app/frontend
COPY SICKLE-CELL-UI/sickle-cell-ui/package*.json ./
RUN npm ci
COPY SICKLE-CELL-UI/sickle-cell-ui/public ./public
COPY SICKLE-CELL-UI/sickle-cell-ui/src ./src
RUN npm run build

# Python backend stage
FROM python:3.10-slim
WORKDIR /app

# Copy backend files
COPY requirements.txt .
COPY app/ ./app/
COPY models/ ./models/
COPY inference.py .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./static

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install uvicorn and serve package
RUN pip install uvicorn serve

# Expose ports
EXPOSE 8000 3000

# Start both backend and frontend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & serve -s static -l 3000"]
```

#### **Step 2: Deploy to Heroku (Free/Paid)**

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Push to Heroku
git push heroku main

# View app
heroku open
```

#### **Step 3: Deploy to Google Cloud Run (FREE tier available)**

```bash
# Requires gcloud CLI
gcloud builds submit --tag gcr.io/PROJECT-ID/sickle-cell-ai
gcloud run deploy sickle-cell-ai --image gcr.io/PROJECT-ID/sickle-cell-ai --platform managed
```

**Pros:**
- ✅ Professional hosting
- ✅ Good performance
- ✅ Permanent URL
- ✅ Auto HTTPS
- ✅ Scalable for many users

**Cons:**
- ❌ Requires setup time
- ❌ May incur costs
- ❌ More complex deployment

---

### **Option 4: Progressive Web App (PWA) - Android Home Screen Install**

Make the app installable like a native app on Android home screen.

The app already has PWA capabilities! Users can:

1. Open in Chrome: `https://your-domain.com`
2. Menu (3 dots) → "Install app"
3. App appears on home screen 📱

---

## **Quick Comparison Table**

| Method | Setup Time | Cost | Speed | Global | Permanent | Best For |
|--------|-----------|------|-------|--------|-----------|----------|
| **Local WiFi** | Immediate | Free | Fastest | ❌ | ✅ | Testing locally |
| **ngrok** | 5 min | Free (limited) | 200ms | ✅ | ❌ | Quick sharing |
| **Docker + Cloud** | 30 min | $5-50/mo | Fast | ✅ | ✅ | Production |
| **PWA Install** | Already built | Free | Fast | ✅ | ✅ | User experience |

---

## **Recommended Setup for Different Scenarios**

### **Scenario 1: Testing with Friends/Family (Same Building)**
→ Use **Local WiFi** (Option 1)  
→ Share IP: `http://172.16.49.163:3000`

### **Scenario 2: Demo to Anyone Temporarily**
→ Use **ngrok** (Option 2)  
→ Share public URL

### **Scenario 3: Public Healthcare Use**
→ Use **Docker + Cloud** (Option 3)  
→ Deploy to cloud provider  
→ Use domain name (e.g., `falconsscan.healthcare`)

### **Scenario 4: App Store Distribution**
→ Combine **PWA** + **Cloud deployment**  
→ Users install from home screen  
→ Or build native APK with React Native

---

## **Current Status**

✅ **Local WiFi Ready (Option 1)**
- Frontend: `http://172.16.49.163:3000`
- Backend: `http://172.16.49.163:8000`

**Next Steps:**
1. **For immediate testing:** Share local IP URL with friends on same WiFi
2. **For demo:** Set up ngrok (10 minutes)
3. **For production:** Docker + cloud deployment (1-2 hours)

---

## **Android Phone Access Instructions**

### **For Users (Share These Instructions)**

#### **On Android Phone:**

1. **Connect to WiFi** (same network as the computer)
2. **Open Chrome/Firefox browser**
3. **Type in address bar:**
   ```
   http://172.16.49.163:3000
   ```
4. **Accept Medical Disclaimer** ⚠️
5. **Choose:**
   - 📷 **Scan Blood Smear** - Upload image
   - 📋 **Enter Lab Values** - Input Hb, WBC, Platelets

#### **Features Available:**
- ✅ Blood smear image analysis (ML model)
- ✅ Lab values analysis with ML confidence scores
- ✅ Offline processing (no data saved)
- ✅ Works on cellular too (if cloud deployed)

---

## **Next: Full Production Deployment**

This guide covers getting started. For full production:
1. Set up custom domain
2. Enable HTTPS
3. Add user authentication
4. Set up database (if needed for multi-user)
5. Create backend scaling strategy
6. Monitor performance metrics

Let me know which approach you want to pursue! 🚀
