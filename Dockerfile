FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and models
COPY main.py .
COPY stroke_image/stroke_image_v2.keras stroke_image/stroke_image_v2.keras
COPY stroke_QA/stroke_QA.pkl stroke_QA/stroke_QA.pkl

# Validate that model files are real binaries, not Git LFS pointers
RUN python3 -c "\
import zipfile, sys; \
try: \
    zipfile.ZipFile('stroke_image/stroke_image_v2.keras').close(); \
    print('Model file OK') \
except Exception: \
    print('ERROR: stroke_image_v2.keras is a Git LFS pointer, not the actual model.'); \
    print('Fix: run  git lfs pull  on the build machine, then rebuild.'); \
    sys.exit(1)"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]