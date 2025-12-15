from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.alerta import Alerta, AlertaCreate
from .models import Alerta as AlertaModel

router = APIRouter(prefix="/alertas", tags=["alertas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from typing import List

@router.get("/", response_model=List[Alerta])
def get_alertas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alertas = db.query(AlertaModel).filter(AlertaModel.is_active == True).order_by(AlertaModel.created_at.desc()).offset(skip).limit(limit).all()
    return alertas

@router.post("/", response_model=Alerta)
def create_alerta(alerta: AlertaCreate, db: Session = Depends(get_db)):
    db_alerta = AlertaModel(**alerta.dict())
    db.add(db_alerta)
    db.commit()
    db.refresh(db_alerta)
    return db_alerta

@router.get("/{alerta_id}", response_model=Alerta)
def get_alerta(alerta_id: int, db: Session = Depends(get_db)):
    alerta = db.query(AlertaModel).filter(AlertaModel.id == alerta_id).first()
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta not found")
    return alerta
