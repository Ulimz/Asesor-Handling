from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.articulo import Articulo, ArticuloCreate
from .models import Articulo as ArticuloModel

router = APIRouter(prefix="/articulos", tags=["articulos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/search")
def search_articulos(q: str, company_slug: str = None):
    # Use the new RagEngine Service
    from app.services.rag_engine import rag_engine
    results = rag_engine.search(q, company_slug)
    # Frontend expects { "results": [...] } wrapper? 
    # Checking previous code: return {"results": formatted_results}
    return {"results": results}

@router.post("/", response_model=Articulo)
def create_articulo(articulo: ArticuloCreate, db: Session = Depends(get_db)):
    db_articulo = ArticuloModel(title=articulo.title, content=articulo.content, convenio_id=articulo.convenio_id)
    db.add(db_articulo)
    db.commit()
    db.refresh(db_articulo)
    return db_articulo

@router.get("/{articulo_id}", response_model=Articulo)
def get_articulo(articulo_id: int, db: Session = Depends(get_db)):
    articulo = db.query(ArticuloModel).filter(ArticuloModel.id == articulo_id).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Articulo not found")
    return articulo
