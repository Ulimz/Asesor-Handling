from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine
from app.constants import VALID_COMPANIES
from pydantic import BaseModel
from typing import List, Optional, Any

router = APIRouter(prefix="/articulos/search", tags=["articulos_search"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    query: str
    company_slug: Optional[str] = None
    history: List[dict] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]

@router.get("/")
def search_articulos(
    q: str = Query(..., description="Consulta semántica"),
    db: Session = Depends(get_db)
):
    results = rag_engine.search(query=q, db=db)
    return {"results": results}

@router.post("/chat", response_model=ChatResponse)
def chat_with_docs(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    # 0. Rewrite query with history if available
    final_query = request.query
    # 0. Rewrite query (handling history + keyword enhancement)
    final_query = rag_engine.rewrite_query(request.query, request.history)
    if final_query != request.query:
        print(f"🔄 Rewritten Query: '{request.query}' -> '{final_query}'")
    
    # 0.5 Validate company_slug
    if request.company_slug and request.company_slug not in VALID_COMPANIES:
        raise HTTPException(status_code=400, detail=f"Invalid company_slug. Must be one of: {', '.join(VALID_COMPANIES)}")

    # 1.5 Detect Intent
    intent = rag_engine.detect_intent(final_query)
    print(f"🧠 Detected Intent: {intent}")

    # 1. Search relevant chunks (increased limit to capture tables)
    results = rag_engine.search(query=final_query, company_slug=request.company_slug, db=db, limit=8)
    
    if not results:
        return {
            "answer": "No he encontrado información relevante en los documentos para responder a tu pregunta.",
            "sources": []
        }
        
    # 2. Generate answer using Gemini with specific Intent
    answer = rag_engine.generate_answer(query=request.query, context_chunks=results, intent=intent)
    
    return {
        "answer": answer,
        "sources": results
    }
