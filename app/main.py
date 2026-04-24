import io
import os
from pathlib import Path
from typing import Optional
import pickle
import numpy as np

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import torch
import torch.nn as nn

from inference import load_model, preprocess, predict

# Initialize FastAPI app
app = FastAPI(
    title="FalconsScan AI - Blood Cell Analysis API",
    description="Medical blood cell analysis using machine learning",
    version="1.0.0"
)

# CORS Configuration for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static build if available
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend_build"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# Load image classification model once at startup
MODEL_PATH = "models/sickle_classifier.pth"
if not Path(MODEL_PATH).exists():
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

model, classes = load_model(MODEL_PATH)

# Load lab values model and normalization parameters
LAB_VALUES_MODEL_PATH = "models/lab_values_model.pth"
LAB_VALUES_NORMALIZATION_PATH = "models/lab_values_normalization.pkl"

lab_values_model = None
lab_values_normalization = None

if Path(LAB_VALUES_MODEL_PATH).exists() and Path(LAB_VALUES_NORMALIZATION_PATH).exists():
    # Define lab values model architecture (must match training)
    class LabValuesModelArch(nn.Module):
        def __init__(self, input_size=5, hidden_size=64, num_classes=3):
            super(LabValuesModelArch, self).__init__()
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.relu1 = nn.ReLU()
            self.dropout1 = nn.Dropout(0.3)
            
            self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
            self.relu2 = nn.ReLU()
            self.dropout2 = nn.Dropout(0.3)
            
            self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        
        def forward(self, x):
            x = self.fc1(x)
            x = self.relu1(x)
            x = self.dropout1(x)
            
            x = self.fc2(x)
            x = self.relu2(x)
            x = self.dropout2(x)
            
            x = self.fc3(x)
            return x
    
    lab_values_model = LabValuesModelArch()
    lab_values_model.load_state_dict(torch.load(LAB_VALUES_MODEL_PATH, map_location=torch.device('cpu')))
    lab_values_model.eval()
    
    with open(LAB_VALUES_NORMALIZATION_PATH, 'rb') as f:
        lab_values_normalization = pickle.load(f)


# ============== Response Models ==============

class PredictionResponse(BaseModel):
    """Response model for image prediction"""
    label: str
    confidence: float
    probabilities: dict
    interpretation: str
    recommendations: list
    is_sickle_positive: bool


class LabValuesAnalysisResponse(BaseModel):
    """Response model for lab values analysis"""
    hb: float
    wbc: float
    rbc: float
    rdw: float
    platelets: float
    analysis: dict
    risk_assessment: str
    ml_prediction: Optional[dict] = None
    recommendations: list
    disclaimer: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    version: str


# ============== Helper Functions ==============

def get_medical_interpretation(label: str, confidence: float) -> tuple:
    """
    Get medical interpretation of prediction
    Returns: (interpretation, recommendations, is_sickle_positive)
    """
    is_sickle = label.lower() == "sickle"
    
    if is_sickle:
        if confidence > 0.9:
            interpretation = "High confidence detection of sickle cell morphology"
            recommendations = [
                "Consult with a hematologist for confirmatory testing",
                "Consider hemoglobin electrophoresis",
                "Review complete blood count (CBC) results",
                "Evaluate patient symptoms and medical history"
            ]
        elif confidence > 0.7:
            interpretation = "Moderate confidence detection of potential sickle cell morphology"
            recommendations = [
                "Recommend additional testing (hemoglobin electrophoresis)",
                "Consider repeat blood smear evaluation",
                "Consult with medical specialist",
                "Evaluate in context of clinical presentation"
            ]
        else:
            interpretation = "Low confidence detection - further evaluation recommended"
            recommendations = [
                "Recommend repeat testing",
                "Consider additional laboratory analysis",
                "Consult with medical specialist",
                "Correlate with clinical findings"
            ]
    else:
        if confidence > 0.9:
            interpretation = "High confidence - normal blood cell morphology detected"
            recommendations = [
                "Results suggest normal blood smear appearance",
                "Continue routine medical monitoring",
                "Follow up with regular health check-ups",
                "No immediate action required based on image analysis"
            ]
        else:
            interpretation = "Results inconclusive - further evaluation recommended"
            recommendations = [
                "Recommend repeat blood smear analysis",
                "Consider additional laboratory testing",
                "Consult with medical professional",
                "Evaluate in context of symptoms"
            ]
    
    return interpretation, recommendations, is_sickle


def analyze_lab_values(hb: float, wbc: float, rbc: float, rdw: float, platelets: float) -> tuple:
    """
    Analyze lab values using trained ML model
    Returns: (analysis_dict, risk_assessment, recommendations, ml_prediction)
    
    Normal Ranges:
    - Hemoglobin (Hb): 12.0-17.5 g/dL (varies by gender/age)
    - WBC: 4.5-11.0 × 10^9/L
    - RBC: 4.0-6.0 × 10^12/L
    - RDW: 11.5-14.5%
    - Platelets: 150-400 × 10^9/L
    """
    
    analysis = {
        "hemoglobin": {
            "value": hb,
            "status": None,
            "interpretation": ""
        },
        "wbc": {
            "value": wbc,
            "status": None,
            "interpretation": ""
        },
        "rbc": {
            "value": rbc,
            "status": None,
            "interpretation": ""
        },
        "rdw": {
            "value": rdw,
            "status": None,
            "interpretation": ""
        },
        "platelets": {
            "value": platelets,
            "status": None,
            "interpretation": ""
        }
    }
    
    risk_indicators = []
    
    # Analyze Hemoglobin
    if hb < 7.0:
        analysis["hemoglobin"]["status"] = "CRITICAL"
        analysis["hemoglobin"]["interpretation"] = "Critically low hemoglobin - severe anemia"
        risk_indicators.append("severe_anemia")
    elif hb < 9.0:
        analysis["hemoglobin"]["status"] = "ABNORMAL_LOW"
        analysis["hemoglobin"]["interpretation"] = "Low hemoglobin - possible anemia (common in sickle cell)"
        risk_indicators.append("anemia")
    elif hb < 12.0:
        analysis["hemoglobin"]["status"] = "LOW"
        analysis["hemoglobin"]["interpretation"] = "Below normal hemoglobin"
        risk_indicators.append("low_hemoglobin")
    elif hb <= 17.5:
        analysis["hemoglobin"]["status"] = "NORMAL"
        analysis["hemoglobin"]["interpretation"] = "Hemoglobin within normal range"
    else:
        analysis["hemoglobin"]["status"] = "HIGH"
        analysis["hemoglobin"]["interpretation"] = "Elevated hemoglobin"
    
    # Analyze WBC
    if wbc < 3.0:
        analysis["wbc"]["status"] = "ABNORMAL_LOW"
        analysis["wbc"]["interpretation"] = "Low white blood cell count - leukopenia"
        risk_indicators.append("leukopenia")
    elif wbc < 4.5:
        analysis["wbc"]["status"] = "LOW"
        analysis["wbc"]["interpretation"] = "Below normal WBC count"
    elif wbc <= 11.0:
        analysis["wbc"]["status"] = "NORMAL"
        analysis["wbc"]["interpretation"] = "WBC count within normal range"
    elif wbc <= 15.0:
        analysis["wbc"]["status"] = "ELEVATED"
        analysis["wbc"]["interpretation"] = "Mildly elevated WBC count"
        risk_indicators.append("elevated_wbc")
    else:
        analysis["wbc"]["status"] = "ABNORMAL_HIGH"
        analysis["wbc"]["interpretation"] = "Significantly elevated WBC count - leukocytosis"
        risk_indicators.append("leukocytosis")
    
    # Analyze RBC
    if rbc < 3.0:
        analysis["rbc"]["status"] = "CRITICAL"
        analysis["rbc"]["interpretation"] = "Critically low RBC count - severe anemia"
        risk_indicators.append("low_rbc")
    elif rbc < 4.0:
        analysis["rbc"]["status"] = "ABNORMAL_LOW"
        analysis["rbc"]["interpretation"] = "Low RBC count - anemia"
        risk_indicators.append("low_rbc")
    elif rbc <= 5.5:
        analysis["rbc"]["status"] = "NORMAL"
        analysis["rbc"]["interpretation"] = "RBC count within normal range"
    else:
        analysis["rbc"]["status"] = "HIGH"
        analysis["rbc"]["interpretation"] = "Elevated RBC count"
    
    # Analyze RDW
    if rdw < 11.0:
        analysis["rdw"]["status"] = "ABNORMAL_LOW"
        analysis["rdw"]["interpretation"] = "Low red blood cell distribution width"
    elif rdw <= 14.5:
        analysis["rdw"]["status"] = "NORMAL"
        analysis["rdw"]["interpretation"] = "RDW within normal range"
    elif rdw <= 16.5:
        analysis["rdw"]["status"] = "ELEVATED"
        analysis["rdw"]["interpretation"] = "Mildly elevated RDW - some red cell size variation"
        risk_indicators.append("elevated_rdw")
    else:
        analysis["rdw"]["status"] = "ABNORMAL_HIGH"
        analysis["rdw"]["interpretation"] = "Significantly elevated RDW - high red cell size variability"
        risk_indicators.append("elevated_rdw")
    
    # Analyze Platelets
    if platelets < 50:
        analysis["platelets"]["status"] = "CRITICAL"
        analysis["platelets"]["interpretation"] = "Critically low platelets - severe thrombocytopenia"
        risk_indicators.append("severe_thrombocytopenia")
    elif platelets < 100:
        analysis["platelets"]["status"] = "ABNORMAL_LOW"
        analysis["platelets"]["interpretation"] = "Low platelet count - moderate thrombocytopenia"
        risk_indicators.append("thrombocytopenia")
    elif platelets < 150:
        analysis["platelets"]["status"] = "LOW"
        analysis["platelets"]["interpretation"] = "Slightly below normal platelet count"
    elif platelets <= 400:
        analysis["platelets"]["status"] = "NORMAL"
        analysis["platelets"]["interpretation"] = "Platelet count within normal range"
    else:
        analysis["platelets"]["status"] = "HIGH"
        analysis["platelets"]["interpretation"] = "Elevated platelet count - thrombocytosis"
        risk_indicators.append("thrombocytosis")
    
    # Get ML model prediction if available
    ml_prediction = None
    if lab_values_model is not None and lab_values_normalization is not None:
        try:
            # Prepare input for ML model
            mean = lab_values_normalization['mean']
            std = lab_values_normalization['std']
            
            input_array = np.array([[hb, wbc, rbc, rdw, platelets]])
            input_normalized = (input_array - mean) / std
            input_tensor = torch.FloatTensor(input_normalized)
            
            # Get prediction
            with torch.no_grad():
                output = lab_values_model(input_tensor)
                probabilities = torch.softmax(output, dim=1)[0]
                prediction = torch.argmax(output, dim=1)[0].item()
            
            class_names = ["Normal", "Carrier (Trait)", "Sickle Cell Disease"]
            ml_prediction = {
                "model_prediction": class_names[prediction],
                "confidence": float(probabilities[prediction].item()),
                "normal_probability": float(probabilities[0].item()),
                "carrier_probability": float(probabilities[1].item()),
                "sickle_probability": float(probabilities[2].item())
            }
        except Exception as e:
            print(f"Warning: ML model prediction failed: {e}")
    
    # Determine overall risk assessment
    if ml_prediction:
        model_label = ml_prediction["model_prediction"]
        confidence_pct = ml_prediction["confidence"] * 100

        if model_label == "Sickle Cell Disease":
            risk_assessment = (
                f"HIGH RISK - Sickle Cell Disease detected ({confidence_pct:.1f}% confidence)"
            )
        elif model_label == "Carrier (Trait)":
            risk_assessment = (
                f"MODERATE RISK - Sickle cell trait detected ({confidence_pct:.1f}% confidence)"
            )
        else:
            risk_assessment = (
                f"LOW RISK - Normal pattern detected ({confidence_pct:.1f}% confidence)"
            )
    else:
        # Fallback to rule-based assessment if ML not available
        if risk_indicators:
            sickle_cell_patterns = [
                "anemia", "low_hemoglobin", "low_rbc", "elevated_wbc", "elevated_rdw", "thrombocytopenia"
            ]
            sickle_indicators = sum(1 for r in risk_indicators if r in sickle_cell_patterns)
            
            if sickle_indicators >= 3:
                risk_assessment = "HIGH - Pattern consistent with sickle cell disease"
            elif sickle_indicators >= 2:
                risk_assessment = "MODERATE - Some indicators present, further testing recommended"
            else:
                risk_assessment = "LOW-MODERATE - Individual abnormalities noted"
        else:
            risk_assessment = "LOW - All values within normal ranges"
    
    recommendations = [
        "Consult with a healthcare provider for complete interpretation",
        "Consider additional testing if abnormalities are confirmed",
        "Correlate with complete blood count (CBC) and clinical symptoms",
        "This analysis is supportive only and not a medical diagnosis"
    ]
    
    return analysis, risk_assessment, recommendations, ml_prediction


# ============== API Endpoints ==============

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        model_loaded=model is not None,
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_image(image: UploadFile = File(...)):
    """
    Analyze blood smear image for sickle cell detection
    
    - **image**: Blood smear image file (PNG, JPG, JPEG, BMP)
    - Returns: Prediction with confidence, interpretation, and recommendations
    
    **Medical Disclaimer**: This analysis is supportive only and not a substitute
    for professional medical diagnosis.
    """
    
    # Validate image format
    allowed_formats = ["image/png", "image/jpg", "image/jpeg", "image/bmp", "image/webp"]
    if image.content_type not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Image format must be PNG, JPG, JPEG, BMP, or WebP. Received: {image.content_type}"
        )
    
    try:
        # Validate file size (max 10MB)
        image_bytes = await image.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 10MB limit"
            )
        
        # Process image
        image_stream = io.BytesIO(image_bytes)
        tensor = preprocess(image_stream)
        
        # Get prediction from model
        out = predict(model, classes, tensor)
        
        # Get medical interpretation
        interpretation, recommendations, is_sickle = get_medical_interpretation(
            out["label"], 
            out["confidence"]
        )
        
        return PredictionResponse(
            label=out["label"],
            confidence=round(out["confidence"], 4),
            probabilities={k: round(v, 4) for k, v in out["probabilities"].items()},
            interpretation=interpretation,
            recommendations=recommendations,
            is_sickle_positive=(out["label"].lower() == "sickle")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/analyze-lab-values", response_model=LabValuesAnalysisResponse)
async def analyze_lab_values_endpoint(
    hb: float,
    wbc: float,
    rbc: float,
    rdw: float,
    platelets: float
):
    """
    Analyze lab values for sickle cell indicators using ML model
    
    - **hb**: Hemoglobin value (g/dL)
    - **wbc**: White Blood Cell count (×10^9/L)
    - **rbc**: Red Blood Cell count (×10^12/L)
    - **rdw**: Red Cell Distribution Width (%)
    - **platelets**: Platelet count (×10^9/L)
    
    **Medical Disclaimer**: This analysis is supportive only and not a substitute
    for professional medical diagnosis.
    """
    
    try:
        # Validate input ranges
        if not (0 < hb <= 25):
            raise HTTPException(
                status_code=400,
                detail="Hemoglobin value must be between 0 and 25 g/dL"
            )
        if not (0 < wbc <= 100):
            raise HTTPException(
                status_code=400,
                detail="WBC value must be between 0 and 100 ×10^9/L"
            )
        if not (0 < rbc <= 10):
            raise HTTPException(
                status_code=400,
                detail="RBC value must be between 0 and 10 ×10^12/L"
            )
        if not (0 < rdw <= 50):
            raise HTTPException(
                status_code=400,
                detail="RDW value must be between 0 and 50%"
            )
        if not (0 < platelets <= 1000):
            raise HTTPException(
                status_code=400,
                detail="Platelet value must be between 0 and 1000 ×10^9/L"
            )
        
        # Analyze values
        analysis, risk_assessment, recommendations, ml_prediction = analyze_lab_values(hb, wbc, rbc, rdw, platelets)
        
        response_data = {
            "hb": round(hb, 1),
            "wbc": round(wbc, 1),
            "rbc": round(rbc, 2),
            "rdw": round(rdw, 1),
            "platelets": round(platelets, 1),
            "analysis": analysis,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "disclaimer": "This analysis is supportive only. Always consult healthcare professionals for clinical decisions."
        }
        
        if ml_prediction:
            response_data["ml_prediction"] = {
                "model_prediction": ml_prediction["model_prediction"],
                "confidence": round(ml_prediction["confidence"], 4),
                "normal_probability": round(ml_prediction["normal_probability"], 4),
                "carrier_probability": round(ml_prediction["carrier_probability"], 4),
                "sickle_probability": round(ml_prediction["sickle_probability"], 4)
            }
        
        return LabValuesAnalysisResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing lab values: {str(e)}"
        )


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "FalconsScan AI",
        "description": "Blood Cell Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "analyze_lab_values": "/analyze-lab-values (POST)",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Called when API starts"""
    print("=" * 50)
    print("FalconsScan AI API Started")
    print(f"Image Model: {MODEL_PATH}")
    print(f"Classes: {classes}")
    if lab_values_model is not None:
        print(f"Lab Values Model: {LAB_VALUES_MODEL_PATH}")
        print("Lab Values ML: ENABLED")
    else:
        print("Lab Values ML: Using rule-based analysis")
    print("=" * 50)
