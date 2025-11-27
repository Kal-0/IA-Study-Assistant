import os
import httpx

# Tenta pegar a URL da variável de ambiente. 
# Se não existir (ex: rodando local sem config), usa o localhost.
LOCAL_GEMMA_URL = os.getenv("LOCAL_WORKER_URL", "http://localhost:8009") 

# Garante que o endpoint /generate esteja no final
if not LOCAL_GEMMA_URL.endswith("/generate"):
    LOCAL_GEMMA_URL = f"{LOCAL_GEMMA_URL}/generate"

async def call_local_gemma_api(prompt: str, system_prompt: str) -> str:
    """Encaminha a requisição para a API local do Gemma3 e retorna o texto de resposta."""
    payload = {
        "prompt": prompt,
        "system_prompt": system_prompt,
    }

    print(f"📡 Conectando ao Worker em: {LOCAL_GEMMA_URL}") # Log para debug

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(LOCAL_GEMMA_URL, json=payload, timeout=60)
            
            if resp.status_code != 200:
                raise RuntimeError(f"Erro no Worker Local: {resp.status_code} - {resp.text}")
            
            data = resp.json()
            return data.get("response", str(data))
            
        except httpx.RequestError as e:
            # Erro de conexão (ex: Túnel caiu ou URL errada)
            raise RuntimeError(f"Falha ao conectar com o Worker Local ({LOCAL_GEMMA_URL}). O túnel está ativo? Erro: {e}")