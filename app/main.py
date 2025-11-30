from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
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

# CORS – permite que o front em localhost e o front hospedado acessem a API
# ---------------- CORS dinâmico por ambiente ----------------

# DEBUG=True libera tudo; em produção, restringe
DEBUG = True  # Mude para False em produção

if DEBUG:
    # Ambiente de desenvolvimento: qualquer origem pode consumir a API via browser
    allow_origins = ["*"]
else:
    # Ambiente de produção: só seus frontends oficiais
    allow_origins = [
        "http://localhost:8000",                    # se você servir o front pelo próprio backend local
        "https://ia-study-assistant.onrender.com",  # URL do app no Render
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Serve os arquivos JS/CSS do Vite em /assets para index.html
app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """# Serve o index.html na raiz."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health():
    """Health endpoint."""
    return {"status": "ok"}




class AskRequest(BaseModel):
    question: str


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





