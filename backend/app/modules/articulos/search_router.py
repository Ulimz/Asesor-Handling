from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine
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
    # 1. Search relevant chunks
    results = rag_engine.search(query=request.query, company_slug=request.company_slug, db=db, limit=5)
    
    if not results:
        return {
            "answer": "No he encontrado información relevante en los documentos para responder a tu pregunta.",
            "sources": []
        }
        
    # 2. Generate answer using Gemini
    answer = rag_engine.generate_answer(query=request.query, context_chunks=results)
    
    return {
        "answer": answer,
        "sources": results
    }
