# Stroke Detection API

A unified REST API that combines two stroke detection models into a single service:

- **Image-based detection** — classifies brain scan images (CT/MRI) as Stroke or Normal using a CNN
- **Clinical risk prediction** — estimates stroke probability from patient health data using a trained ML classifier

> **Medical Disclaimer:** This system is for research and educational purposes only. It must not be used as a substitute for professional medical diagnosis or treatment.

---

## Project Structure

```
stroke_detection_api/
├── main.py                              # Unified FastAPI application
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container build instructions
├── stroke_image/
│   ├── stroke_image_v2.keras            # Trained CNN model
│   └── Stroke image detact.ipynb        # Model training notebook
└── stroke_QA/
    ├── stroke_QA.pkl                    # Trained ML classifier
    ├── brain_stroke.csv                 # Training dataset (4,983 records)
    └── stroke-predication (1).ipynb     # Model training notebook
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Status check |
| `GET` | `/health` | Health check |
| `POST` | `/image/predict` | Brain scan image → Stroke / Normal |
| `POST` | `/qa/predict` | Patient clinical data → Stroke risk % |

Interactive API docs available at `http://<host>:8000/docs`

---

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker

### Build and run

```bash
docker build -t stroke-api .
docker run -p 8000:8000 stroke-api
```

### Run in background

```bash
docker run -d -p 8000:8000 --restart always --name stroke-api stroke-api
```

---

## Deploy on AWS EC2

### 1. Launch an EC2 instance

- **AMI**: Ubuntu 22.04 LTS
- **Instance type**: `t3.medium` or larger (model loading requires ~1.5 GB RAM)
- **Security Group**: open inbound port `80` (HTTP) and `22` (SSH)

### 2. Connect and install Docker

```bash
ssh -i your-key.pem ubuntu@<ec2-public-ip>

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

Log out and back in for the group change to take effect.

### 3. Transfer files and deploy

```bash
# From your local machine — copy project files
scp -i your-key.pem -r . ubuntu@<ec2-public-ip>:~/stroke-api

# On the EC2 instance
cd ~/stroke-api
docker build -t stroke-api .
docker run -d -p 80:8000 --restart always --name stroke-api stroke-api
```

The API is now accessible at `http://<ec2-public-ip>/docs`

---

## Usage Examples

### Image Prediction

```bash
curl -X POST "http://<host>/image/predict" \
     -H "accept: application/json" \
     -F "file=@brain_scan.jpg"
```

Response:
```json
{
  "prediction": "Stroke",
  "confidence": "87.3%"
}
```

### Clinical Risk Prediction

```bash
curl -X POST "http://<host>/qa/predict" \
     -H "Content-Type: application/json" \
     -d '{
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
     }'
```

Response:
```json
{
  "stroke_probability": 85.3,
  "risk_category": "High Risk",
  "prediction_timestamp": "2026-04-27T14:32:11.123456"
}
```

### Python Client

```python
import requests

# Image prediction
with open("brain_scan.jpg", "rb") as f:
    response = requests.post("http://<host>/image/predict", files={"file": f})
print(response.json())

# Clinical prediction
patient = {
    "gender": "Female", "age": 45.0, "hypertension": 1,
    "heart_disease": 0, "ever_married": "Yes", "work_type": "Private",
    "Residence_type": "Urban", "avg_glucose_level": 180.5,
    "bmi": 28.3, "smoking_status": "never smoked"
}
response = requests.post("http://<host>/qa/predict", json=patient)
print(response.json())
```

---

## Clinical Prediction — Input Fields

| Field | Type | Values |
|-------|------|--------|
| `gender` | string | `Male`, `Female` |
| `age` | float | 0 – 120 |
| `hypertension` | int | `0` = No, `1` = Yes |
| `heart_disease` | int | `0` = No, `1` = Yes |
| `ever_married` | string | `Yes`, `No` |
| `work_type` | string | `Private`, `Self-employed`, `Govt_job`, `children` |
| `Residence_type` | string | `Urban`, `Rural` |
| `avg_glucose_level` | float | 50 – 500 mg/dL |
| `bmi` | float | 10 – 70 |
| `smoking_status` | string | `never smoked`, `formerly smoked`, `smokes`, `Unknown` |

### Risk Categories

| Category | Probability |
|----------|-------------|
| Low Risk | < 10% |
| Low-Moderate Risk | 10% – 24% |
| Moderate Risk | 25% – 49% |
| High Risk | ≥ 50% |

---

## Model Information

### Image Model (CNN)
- **Framework**: TensorFlow / Keras
- **Input**: 224 × 224 RGB image
- **Output**: Binary classification — `Stroke` / `Normal`
- **Format**: `.keras`

### Clinical Model (ML Classifier)
- **Framework**: Scikit-learn
- **Input**: 14 engineered features from 10 patient attributes
- **Output**: Stroke probability (0 – 100%)
- **Training data**: 4,983 patient records
- **Format**: `.pkl`

---

## Retrain the Models

```bash
# Image model
jupyter notebook "stroke_image/Stroke image detact.ipynb"

# Clinical model
jupyter notebook "stroke_QA/stroke-predication (1).ipynb"
```

Replace the model files (`stroke_image_v2.keras`, `stroke_QA.pkl`) with the newly trained versions, then rebuild the Docker image.

---

## License

MIT License