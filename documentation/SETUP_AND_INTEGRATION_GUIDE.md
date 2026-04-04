# FalconsScan AI - Complete Project Setup & Integration Guide

## 📋 Project Overview

FalconsScan AI is a complete medical AI application for blood cell analysis combining:
- **Backend**: Python FastAPI with PyTorch ML model
- **Frontend**: React web application
- **AI Model**: ResNet18-based sickle cell classifier
- **Security**: Zero data collection, local processing
- **Medical Standards**: HIPAA-aligned, accessibility compliant

---

## 🏗️ Project Architecture

```
sickle-cell-ai/
├── Backend (Python)
│   ├── app/
│   │   └── main.py          (FastAPI server with endpoints)
│   ├── inference.py          (ML model inference)
│   ├── analyze_smear.py      (Blood smear analysis)
│   ├── models/
│   │   └── sickle_classifier.pth  (PyTorch model)
│   ├── requirements.txt       (Python dependencies)
│   └── .venv/                (Virtual environment)
│
├── Frontend (React)
│   └── SICKLE-CELL-UI/
│       └── sickle-cell-ui/
│           ├── src/
│           │   ├── App.js               (Main component with API integration)
│           │   ├── App.css              (Responsive styles)
│           │   └── index.js
│           ├── public/
│           │   └── index.html           (Security headers)
│           ├── package.json
│           └── .env                     (API configuration)
│
├── Documentation
│   ├── README.md              (This file)
│   ├── BACKEND_SETUP.md       (Backend configuration)
│   ├── FRONTEND_SETUP.md      (React setup)
│   └── API_DOCUMENTATION.md   (API endpoints)
│
└── Scripts
    ├── start_backend.ps1      (Backend startup)
    └── start_frontend.ps1     (Frontend startup)
```

---

## 🚀 Quick Start (Complete Setup)

### Prerequisites
- Python 3.10+
- Node.js 16+
- PyTorch with CUDA support (optional, CPU works fine)
- 2GB+ RAM free

### Step 1: Clone/Setup Backend

```bash
cd d:\sickle-cell-ai

# Create virtual environment if not exists
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Verify model file exists
# Should be at: d:\sickle-cell-ai\models\sickle_classifier.pth
```

### Step 2: Start Backend Server

**Option A: Using PowerShell Script**
```powershell
.\start_backend.ps1
```

**Option B: Manual Start**
```bash
cd d:\sickle-cell-ai
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Server Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Step 3: Start Frontend Server

**Option A: Using PowerShell Script**
```powershell
.\start_frontend.ps1
```

**Option B: Manual Start**
```bash
cd d:\sickle-cell-ai\SICKLE-CELL-UI\sickle-cell-ui
npm install  # Only first time
npm start
```

**Browser will open at:** `http://localhost:3000`

---

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 2. Predict Image (Blood Smear Analysis)
```
POST /predict
Content-Type: multipart/form-data

Body: image file (JPG, PNG, WebP, BMP, max 10MB)
```

**Response:**
```json
{
  "label": "normal",
  "confidence": 0.95,
  "probabilities": {
    "normal": 0.95,
    "sickle": 0.05
  },
  "interpretation": "High confidence - normal blood cell morphology detected",
  "recommendations": [...],
  "is_sickle_positive": false
}
```

### 3. Analyze Lab Values
```
POST /analyze-lab-values?hb=13.5&wbc=8.2&platelets=250
```

**Response:**
```json
{
  "hb": 13.5,
  "wbc": 8.2,
  "platelets": 250.0,
  "analysis": {
    "hemoglobin": {
      "value": 13.5,
      "status": "NORMAL",
      "interpretation": "Hemoglobin within normal range"
    },
    "wbc": {...},
    "platelets": {...}
  },
  "risk_assessment": "LOW - All values within normal ranges",
  "recommendations": [...],
  "disclaimer": "..."
}
```

Access API documentation at: `http://localhost:8000/docs`

---

## 🔧 Configuration

### Frontend Environment (.env)
```env
# API URL - Change for production
REACT_APP_API_URL=http://localhost:8000

# Environment
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0

# Features
REACT_APP_DISABLE_ANALYTICS=true
```

### Backend Model Path (app/main.py)
```python
MODEL_PATH = "models/sickle_classifier.pth"
```

---

## 📊 Testing the Integration

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Test Image Prediction
```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:8000/predict
```

### 3. Test Lab Values Analysis
```bash
curl "http://localhost:8000/analyze-lab-values?hb=13.5&wbc=8.2&platelets=250" -X POST
```

### 4. Test Frontend
- Navigate to http://localhost:3000
- Accept medical disclaimer
- Try uploading an image or entering lab values
- Should see results from the backend

---

## 🛡️ Security Considerations

### Production Deployment

#### 1. CORS Configuration
Update `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. HTTPS
- Deploy backend on HTTPS only
- Update frontend `.env`:
```env
REACT_APP_API_URL=https://api.yourdomain.com
```

#### 3. Rate Limiting
Add rate limiting middleware:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

#### 4. Environment Security
- Never commit `.env.local` to version control
- Use environment variables in production
- Rotate API keys regularly

---

## 🚢 Production Deployment

### Option 1: Docker Deployment (Recommended)

**Create `Dockerfile.backend`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -f Dockerfile.backend -t sickle-cell-ai-backend .
docker run -p 8000:8000 sickle-cell-ai-backend
```

### Option 2: Direct Server Deployment

**Linux/Ubuntu:**
```bash
# Install dependencies
sudo apt-get install python3-pip python3-venv nginx

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

**Windows Server:**
```powershell
# Using Python directly
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Cloud Deployment

#### Heroku
```bash
heroku create sickle-cell-ai
git push heroku main
```

#### AWS
- Use Flask/FastAPI with AWS Lambda
- S3 for model storage
- API Gateway for routing

#### Google Cloud
- Cloud Run for FastAPI
- Cloud Storage for models
- Cloud Build for CI/CD

---

## 🧪 Testing

### Backend Tests
```bash
# Install pytest
pip install pytest

# Run tests
pytest test_backend.py -v
```

### Frontend Tests
```bash
# Install testing libraries
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test
```

### Integration Tests
1. Start both backend and frontend
2. Test each endpoint via UI
3. Verify data flows correctly
4. Check error handling

---

## 📈 Performance Optimization

### Backend
- Model quantization for faster inference
- Caching predictions for common inputs
- Batch processing for multiple images
- GPU acceleration with CUDA

### Frontend
- Service Worker for offline support
- Code splitting for lazy loading
- Image compression before upload
- Memoization for expensive calculations

---

## 🐛 Troubleshooting

### Backend Won't Start
**Error:** `ModuleNotFoundError: No module named 'torch'`
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

**Error:** `Port 8000 already in use`
```bash
# Find and kill existing process
netstat -ano | findstr :8000
taskkill /PID {PID} /F

# Or use different port
uvicorn app.main:app --port 8001
```

### Frontend Won't Connect to Backend
**Error:** `Failed to fetch from http://localhost:8000`
1. Verify backend is running: `http://localhost:8000/health`
2. Check CORS is enabled in FastAPI
3. Verify API URL in `.env` file
4. Network debug: Check browser console for exact error

### Image Upload Fails
**Error:** `File size exceeds 10MB limit`
- Use smaller image files
- Compress image first

**Error:** `Image format not supported`
- Ensure format is JPG, PNG, WebP, or BMP
- Convert image if needed

---

## 📚 Additional Resources

### Documentation Files
- `SECURITY.md` - Security & privacy specifications
- `PERFORMANCE.md` - Performance optimization
- `README_FULL.md` - Complete UI documentation
- `QUICK_START.md` - Quick reference

### External Resources
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [PyTorch Docs](https://pytorch.org/docs/)
- [React Docs](https://react.dev/)
- [Bootstrap Docs](https://getbootstrap.com/)

---

## 🤝 Contributing

### Code Standards
- Follow PEP 8 for Python
- Use functional components in React
- Write meaningful commit messages
- Update documentation

### Pull Request Process
1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Submit pull request
5. Wait for review

---

## 📄 License

[Specify your license - MIT, Apache 2.0, etc.]

---

## 📞 Support

### Getting Help
1. Check documentation files
2. Review API documentation at `/docs`
3. Check troubleshooting section
4. Contact development team

### Reporting Issues
- Describe the issue clearly
- Include error messages
- Provide steps to reproduce
- Attach screenshots if relevant

---

## 🗓️ Development Roadmap

### Version 1.0 (Current) ✅
- ✅ Image-based sickle cell detection
- ✅ Lab values analysis
- ✅ Web UI with responsive design
- ✅ HIPAA-aligned security
- ✅ Medical disclaimers

### Version 1.1 (Planned)
- [ ] Advanced image analysis with cell segmentation
- [ ] Patient history tracking (optional, encrypted)
- [ ] PDF report generation
- [ ] Multi-language support
- [ ] Mobile app

### Version 2.0 (Future)
- [ ] Multi-model ensemble
- [ ] Real-time microscopy analysis
- [ ] EHR integration
- [ ] Batch analysis
- [ ] Advanced ML interpretability

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Mar 26, 2026 | Initial release - Image & lab value analysis |
| 0.9.0 | Mar 20, 2026 | Beta testing - Integration complete |
| 0.5.0 | Mar 10, 2026 | Development - UI & API in progress |

---

## ✅ Project Checklist

### Development
- [x] Backend API development
- [x] Frontend UI development
- [x] Backend-Frontend integration
- [x] Image prediction endpoint
- [x] Lab values analysis endpoint
- [x] Error handling
- [x] Security implementation
- [x] Medical disclaimers
- [x] Responsive design
- [x] Accessibility (WCAG 2.1 AA)

### Testing
- [ ] Unit tests (backend)
- [ ] Unit tests (frontend)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Security tests
- [ ] Performance tests
- [ ] Accessibility tests

### Deployment
- [ ] Production-ready build
- [ ] Server configuration
- [ ] SSL/HTTPS setup
- [ ] Database setup (if needed)
- [ ] Backup strategy
- [ ] Monitoring setup
- [ ] Documentation finalization

---

**Status**: 🟢 **Ready for Testing**

Last Updated: March 26, 2026
