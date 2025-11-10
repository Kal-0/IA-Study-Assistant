from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env automaticamente
load_dotenv()

app = FastAPI(title="IsCoolGPT - Gemini API integration")

class AskRequest(BaseModel):
    question: str

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

async def call_gemini_api(question: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"parts": [{"text": question}]}
        ]
    }
    params = {"key": api_key}
    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=20)
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API error: {response.status_code} {response.text}")
        data = response.json()
        # Extract the answer from the Gemini API response
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return str(data)

@app.post("/ask")
async def ask(req: AskRequest):
    """Recebe uma pergunta e retorna a resposta do Gemini API."""
    try:
        # answer = await call_gemini_api(req.question) ================= remove
        
        answer = "answer from gemini api"

        return {
            "question": req.question,
            "answer": answer
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test(q: str = "hello"):
    """Simple test endpoint that echoes a query parameter."""
    return {"message": "test ok", "echo": q}

@app.get("/health")
async def health():
    """Health endpoint used by load balancers / orchestration."""
    return {"status": "ok"}
