from fastapi import Body, Depends, FastAPI, Header, HTTPException
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY is missing. Set it in your .env file.")

API_KEY_CREDITS = {API_KEY: 5}
app = FastAPI()


def verify_api_key(x_api_key: str | None = Header(default=None, alias="x-api-key")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="Invalid API key, or no credits")

    return x_api_key


@app.post("/generate")
def generate(prompt: str = Body(...), x_api_key: str = Depends(verify_api_key)):
    if API_KEY_CREDITS.get(x_api_key, 0) <= 0:
        raise HTTPException(status_code=401, detail="Invalid API key, or no credits")

    API_KEY_CREDITS[x_api_key] -= 1

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama request failed: {str(exc)}") from exc

    return {"response": response["message"]["content"]}