from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.jurisprudencia import Jurisprudencia, JurisprudenciaCreate
from .models import Jurisprudencia as JurisprudenciaModel

router = APIRouter(prefix="/jurisprudencia", tags=["jurisprudencia"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Jurisprudencia)
def create_jurisprudencia(jurisprudencia: JurisprudenciaCreate, db: Session = Depends(get_db)):
    db_juris = JurisprudenciaModel(**jurisprudencia.dict())
    db.add(db_juris)
    db.commit()
    db.refresh(db_juris)
    return db_juris

@router.get("/{jurisprudencia_id}", response_model=Jurisprudencia)
def get_jurisprudencia(jurisprudencia_id: int, db: Session = Depends(get_db)):
    jurisprudencia = db.query(JurisprudenciaModel).filter(JurisprudenciaModel.id == jurisprudencia_id).first()
    if not jurisprudencia:
        raise HTTPException(status_code=404, detail="Jurisprudencia not found")
    return jurisprudencia
