from fastapi import FastAPI, File, UploadFile
import ollama
import tempfile

app = FastAPI()

@app.post("/emotion")
async def detect_emotion(image: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        image_path = tmp.name

    result = ollama.chat(
        model="llama3.2-vision",
        messages=[{
            "role": "user",
            "content": "Detect the emotion in this image. Reply with one word only (e.g., happy, sad, angry, surprised, neutral).",
            "images": [image_path]
        }]
    )

    return {"emotion": result["message"]["content"].strip()}