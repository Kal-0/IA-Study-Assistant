from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.gemini_service import call_gemini_api
from app.services.local_gemma3_service import call_local_gemma_api

# --- Persona / system prompt (definido aqui) ---
SYSTEM_PROMPT = (
    "Você é o IsCoolGPT, um assistente de estudos inteligente e paciente. "
    "Seu papel é ajudar estudantes a compreender conceitos acadêmicos complexos, "
    "fornecendo explicações detalhadas, exemplos e referências teóricas sempre que possível. "
    "Responda de forma clara, organizada e didática, mantendo um tom acessível e acadêmico ao mesmo tempo."
)



app = FastAPI(title="IsCoolGPT - IA Assistente de Estudos ")

class AskRequest(BaseModel):
    question: str


@app.get("/health")
async def health():
    """Health endpoint."""
    return {"status": "ok"}


@app.post("/ask/gemma")
async def ask_gemma(req: AskRequest):
    """Encaminha a pergunta para a API local do Gemma3 e retorna a resposta."""
    try:
        answer = await call_local_gemma_api(req.question, SYSTEM_PROMPT)
        return {
            "question": req.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/gemini")
async def ask_gemini(req: AskRequest):
    """Encaminha a pergunta para a API Gemini e retorna a resposta."""
    try:
        answer = await call_gemini_api(req.question, SYSTEM_PROMPT)
        return {
            "question": req.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





