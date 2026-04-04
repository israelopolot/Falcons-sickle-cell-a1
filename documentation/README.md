# Sickle Cell Image-Based Analysis AI

This repository contains a prototype image-based AI system for sickle cell disease analysis and general blood cell classification.

## Structure

- `train.py`: Training script for image classifier (multi-class blood cell types).
- `inference.py`: Inference utilities for making predictions on individual images.
- `app/main.py`: FastAPI app for serving prediction endpoint.
- `generate_synthetic_data.py`: Generate synthetic training data.
- `download_kaggle_data.py`: Download and organize real datasets from Kaggle.
- `organize_kaggle_data.py`: Helper to organize downloaded data into train/val splits.
- `requirements.txt`: Python dependencies.

## Setup

1. Create and activate Python environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Training Options

### Option 1: Real Kaggle Data (Recommended)

1. Set up Kaggle API:
   - Download `kaggle.json` from https://kaggle.com/account → API → Create New Token
   - Place in `C:\Users\<username>\.kaggle\kaggle.json`

2. Download and organize data:
   ```bash
   kaggle datasets download -d paultimothymooney/blood-cells --unzip -p data/kaggle_blood_cells
   python organize_kaggle_data.py
   ```

3. Train model:
   ```bash
   python train.py --data_dir data --epochs 20 --batch_size 16 --model_path models/blood_cell_classifier.pth
   ```

### Option 2: Synthetic Data (Quick Start)

```bash
python generate_realistic_data.py --output_dir data --n_images 500
python train.py --data_dir data --epochs 20 --batch_size 32 --model_path models/sickle_classifier.pth
```

## API Usage

1. Run server:
   ```bash
   .venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Test prediction:
   ```bash
   curl.exe -F "image=@path/to/test_image.jpg" http://127.0.0.1:8000/predict
   ```

## Mobile Testing

Access from phone: `http://<your-pc-ip>:8000/docs`

Example response:
```json
{
  "label": "eosinophil",
  "confidence": 0.94,
  "probabilities": {
    "neutrophil": 0.02,
    "eosinophil": 0.94,
    "lymphocyte": 0.01,
    "monocyte": 0.02,
    "basophil": 0.01
  }
}
```

## Current Capabilities

- ✅ Multi-class blood cell classification (5 WBC types)
- ✅ Trained on real Kaggle dataset (350+ images)
- ✅ Mobile camera photo testing via API
- ✅ High accuracy on validation set
- ⏳ Ready for sickle cell image integration

## Adding Sickle Cell Images

To add sickle cell analysis:

1. Collect real sickle cell microscope images
2. Add to `data/train/sickle/` and `data/val/sickle/`
3. Re-train model for binary classification (normal vs sickle)
4. Update model loading in `app/main.py`

## Notes

Clinical deployment requires regulatory validation, proper dataset consent, and monitoring for bias.
