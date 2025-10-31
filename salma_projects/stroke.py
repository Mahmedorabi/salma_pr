from fastapi import FastAPI, File, UploadFile
import ollama
import tempfile

app = FastAPI()

@app.post("/stroke")
async def detect_emotion(image: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await image.read())
        image_path = tmp.name

    result = ollama.chat(
        model="llama3.2-vision",
        messages=[{
            "role": "user",
            "content": "Classify this face image. Reply with only one word: 'Stroke' or 'Non stroke'. Stroke = sudden one-sided facial weakness (mouth droop, can't fully close eye, uneven smile, facial paralysis or numbness). If any sign present -> Stroke, otherwise -> Non stroke.",
            "images": [image_path]
        }]
    )

    return {"stroke": result["message"]["content"].strip()}