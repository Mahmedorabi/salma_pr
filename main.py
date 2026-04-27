from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
import numpy as np
from tensorflow import keras
from PIL import Image
import io
import pickle
from datetime import datetime

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Stroke Detection API", version="1.0.0")

# Load image model
image_model = keras.models.load_model(BASE_DIR / "stroke_image" / "stroke_image_v2.keras")

# Load QA model
with open(BASE_DIR / "stroke_QA" / "stroke_QA.pkl", "rb") as f:
    qa_model = pickle.load(f)


# ── Image Detection ──────────────────────────────────────────────────────────

@app.post("/image/predict")
async def predict_from_image(file: UploadFile = File(...)):
    image_data = await file.read()
    img = Image.open(io.BytesIO(image_data))
    img = img.resize((224, 224)).convert("RGB")
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 224, 224, 3)

    prediction = image_model.predict(img_array)[0][0]

    if prediction >= 0.5:
        result = "Stroke"
        confidence = prediction * 100
    else:
        result = "Normal"
        confidence = (1 - prediction) * 100

    return {"prediction": result, "confidence": f"{confidence:.1f}%"}


# ── Clinical QA Prediction ───────────────────────────────────────────────────

class PatientData(BaseModel):
    gender: str = Field(..., description="Male or Female")
    age: float = Field(..., ge=0, le=120)
    hypertension: int = Field(..., ge=0, le=1)
    heart_disease: int = Field(..., ge=0, le=1)
    ever_married: str = Field(..., description="Yes or No")
    work_type: str = Field(..., description="Private, Self-employed, Govt_job, or children")
    Residence_type: str = Field(..., description="Urban or Rural")
    avg_glucose_level: float = Field(..., ge=50, le=500)
    bmi: float = Field(..., ge=10, le=70)
    smoking_status: str = Field(..., description="formerly smoked, never smoked, smokes, or Unknown")

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Male", "age": 67.0, "hypertension": 0,
                "heart_disease": 1, "ever_married": "Yes", "work_type": "Private",
                "Residence_type": "Urban", "avg_glucose_level": 228.69,
                "bmi": 36.6, "smoking_status": "formerly smoked"
            }
        }


class PredictionResponse(BaseModel):
    stroke_probability: float
    risk_category: str
    prediction_timestamp: str


def _preprocess(data: PatientData) -> np.ndarray:
    features = [
        data.age, data.hypertension, data.heart_disease, data.avg_glucose_level,
        data.bmi,
        1 if data.gender == "Male" else 0,
        1 if data.ever_married == "Yes" else 0,
        1 if data.work_type == "Private" else 0,
        1 if data.work_type == "Self-employed" else 0,
        1 if data.work_type == "children" else 0,
        1 if data.Residence_type == "Urban" else 0,
        1 if data.smoking_status == "formerly smoked" else 0,
        1 if data.smoking_status == "never smoked" else 0,
        1 if data.smoking_status == "smokes" else 0,
    ]
    return np.array([features])


def _risk_category(probability: float) -> str:
    p = probability * 100
    if p >= 50:
        return "High Risk"
    elif p >= 25:
        return "Moderate Risk"
    elif p >= 10:
        return "Low-Moderate Risk"
    return "Low Risk"


@app.post("/qa/predict", response_model=PredictionResponse)
def predict_from_data(data: PatientData):
    try:
        features = _preprocess(data)
        proba = qa_model.predict_proba(features)[0][1]
        return PredictionResponse(
            stroke_probability=round(proba * 100, 2),
            risk_category=_risk_category(proba),
            prediction_timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Health ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Stroke Detection API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}