import os
import httpx
import asyncio

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")
    return api_key

async def call_gemini_api(question: str, system_prompt: str) -> str:
    """Chama a Gemini API para obter uma resposta à pergunta fornecida usando `system_prompt`."""
    api_key = get_api_key()
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt},
                    {"text": question}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "topK": 40
        }
    }

    
    max_retries = 3
    backoff = 2
    async with httpx.AsyncClient() as client:
        for attempt in range(1, max_retries + 1):
            response = await client.post(GEMINI_API_URL, headers=headers, json=payload, timeout=120)
            if response.status_code == 200:
                data = response.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    return str(data)
            elif response.status_code == 503 and attempt < max_retries:
                await asyncio.sleep(backoff * attempt)
                continue
            else:
                raise RuntimeError(f"Gemini API error: {response.status_code} {response.text}")
