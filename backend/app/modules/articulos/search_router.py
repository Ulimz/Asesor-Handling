from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine
from app.constants import VALID_COMPANIES, SECTOR_COMPANIES
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
    user_context: Optional[dict] = None

class AuditStatus(BaseModel):
    verified: bool
    risk_level: str
    reason: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    audit: Optional[AuditStatus] = None

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

    # --- HYBRID RAG: TOOL CALLING (Structured Data) ---
    # If intent is SALARY, inject SQL data from CalculatorService
    structured_data_context = ""
    from app.services.calculator_service import CalculatorService
    from app.prompts import IntentType
    
    if intent == IntentType.SALARY and request.company_slug:
        try:
            # Extract profile from User user_context (provided by frontend)
            # Default to "Serv. Auxiliares" / "Nivel 3" if missing
            user_ctx = request.user_context or {}
            
            group = user_ctx.get('job_group', "Serv. Auxiliares")
            level = user_ctx.get('salary_level', "Nivel 3")
            
            # Map logic for "Entry Level" variations if needed, or rely on strict string matching.
            # ideally the frontend sends strings that match DB keys.

            calc_service = CalculatorService(db)
            
            # Inject data for the SPECIFIC user profile
            # AND ALSO the full GROUP table for comparisons
            
            # 1. User specific table (High precision for "Mi sueldo")
            user_table = calc_service.get_formatted_salary_table(
                request.company_slug, 
                group, 
                level
            )
            
            # 2. Group table (Context for "Diferencia nivel 1 y 2")
            group_table = calc_service.get_group_salary_table_markdown(
                request.company_slug,
                group
            )
            
            structured_data_context = f"{user_table}\n\n{group_table}"
            print(f"   💰 Injecting SQL Salary Tables (User + Full Group) for {request.company_slug}")
            
        except Exception as e:
            print(f"Failed to inject structured data: {e}")
    # --------------------------------------------------

    # --- MAPPING SECTOR COMPANIES ---
    # Companies that adhere to the Sector Agreement (convenio-sector)
    # We map them here so RAG searches the correct documents.
    target_slug = request.company_slug
    
    if request.company_slug in SECTOR_COMPANIES:
        print(f"🔀 Redirecting '{request.company_slug}' to 'convenio-sector' for document search")
        target_slug = "convenio-sector"
    # --------------------------------

    # 1. Search relevant chunks (increased limit to capture tables)
    results = rag_engine.search(query=final_query, company_slug=target_slug, db=db, limit=12)
    
    # 4. Generate Answer (RAG)
    # Returns dict {"text": str, "audit": dict}
    gen_result = rag_engine.generate_answer(
        query=request.query, 
        context_chunks=results, 
        intent=intent,
        user_context=request.user_context, # Pass user_context here
        structured_data=structured_data_context,
        history=request.history,
        db=db
    )
    
    # Handle legacy string return just in case
    if isinstance(gen_result, str):
        final_answer = gen_result
        audit_data = None
    else:
        final_answer = gen_result.get("text", "Error generanda respuesta")
        audit_data = gen_result.get("audit")

    return {
        "answer": final_answer,
        "sources": results,
        "audit": audit_data
    }

