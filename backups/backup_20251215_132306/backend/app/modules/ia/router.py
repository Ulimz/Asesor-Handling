from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter(prefix="/ia", tags=["ia"])

class IAQuery(BaseModel):
    question: str
    context: str = ""

@router.post("/ask")
def ask_ia(query: IAQuery):
    # Ejemplo de integración con OpenAI (puedes adaptar a Azure o modelo propio)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key de OpenAI no configurada")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Eres un experto en derecho laboral español especializado en handling aeroportuario."},
            {"role": "user", "content": query.question + ("\nContexto: " + query.context if query.context else "")}
        ]
    }
    try:
        response = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
