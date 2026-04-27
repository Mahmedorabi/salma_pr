from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import numpy as np
import uvicorn
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Stroke Prediction API", version="1.0.0")

# Load the trained model
try:
    with open('stroke_QA.pkl', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    raise Exception("Model file 'stroke_QA.pkl' not found")

# Define the input data structure
class PatientData(BaseModel):
    gender: str = Field(..., description="Male or Female")
    age: float = Field(..., ge=0, le=120, description="Age in years")
    hypertension: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    heart_disease: int = Field(..., ge=0, le=1, description="0 = No, 1 = Yes")
    ever_married: str = Field(..., description="Yes or No")
    work_type: str = Field(..., description="Private, Self-employed, Govt_job, or children")
    Residence_type: str = Field(..., description="Urban or Rural")
    avg_glucose_level: float = Field(..., ge=50, le=500, description="Average glucose level")
    bmi: float = Field(..., ge=10, le=70, description="Body Mass Index")
    smoking_status: str = Field(..., description="formerly smoked, never smoked, smokes, or Unknown")

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "Male",
                "age": 67.0,
                "hypertension": 0,
                "heart_disease": 1,
                "ever_married": "Yes",
                "work_type": "Private",
                "Residence_type": "Urban",
                "avg_glucose_level": 228.69,
                "bmi": 36.6,
                "smoking_status": "formerly smoked"
            }
        }

# Response model
class PredictionResponse(BaseModel):
    stroke_probability: float = Field(..., description="Probability of stroke (0-100%)")
    risk_category: str = Field(..., description="Risk category")
    prediction_timestamp: str = Field(..., description="When prediction was made")

def preprocess_data(data: PatientData) -> np.ndarray:
    """Convert patient data to model format"""
    # Create binary encodings
    gender_male = 1 if data.gender == 'Male' else 0
    ever_married_yes = 1 if data.ever_married == 'Yes' else 0
    residence_urban = 1 if data.Residence_type == 'Urban' else 0
    
    # Work type encoding
    work_private = 1 if data.work_type == 'Private' else 0
    work_self_employed = 1 if data.work_type == 'Self-employed' else 0
    work_children = 1 if data.work_type == 'children' else 0
    
    # Smoking status encoding
    smoking_formerly = 1 if data.smoking_status == 'formerly smoked' else 0
    smoking_never = 1 if data.smoking_status == 'never smoked' else 0
    smoking_smokes = 1 if data.smoking_status == 'smokes' else 0

    # Create feature array
    features = [
        data.age, data.hypertension, data.heart_disease, data.avg_glucose_level,
        data.bmi, gender_male, ever_married_yes, work_private, work_self_employed,
        work_children, residence_urban, smoking_formerly, smoking_never, smoking_smokes
    ]

    return np.array([features])

def get_risk_category(probability: float) -> str:
    """Determine risk category based on probability"""
    prob_percentage = probability * 100
    
    if prob_percentage >= 50:
        return "High Risk"
    elif prob_percentage >= 25:
        return "Moderate Risk"
    elif prob_percentage >= 10:
        return "Low-Moderate Risk"
    else:
        return "Low Risk"

# API Endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Stroke Prediction API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
def predict_stroke_risk(data: PatientData):
    """Predict stroke risk based on patient data"""
    try:
        # Preprocess input data
        input_features = preprocess_data(data)
        
        # Make prediction
        probabilities = model.predict_proba(input_features)[0]
        stroke_probability = probabilities[1]  # Probability of stroke
        
        # Get risk category
        risk_category = get_risk_category(stroke_probability)
        
        return PredictionResponse(
            stroke_probability=round(stroke_probability * 100, 2),
            risk_category=risk_category,
            prediction_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
