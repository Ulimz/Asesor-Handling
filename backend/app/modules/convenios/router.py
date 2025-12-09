from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.convenio import Convenio, ConvenioCreate
from .models import Convenio as ConvenioModel

router = APIRouter(prefix="/convenios", tags=["convenios"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[Convenio])
@router.get("/", response_model=list[Convenio], include_in_schema=False)
def get_convenios(db: Session = Depends(get_db)):
    return db.query(ConvenioModel).filter(ConvenioModel.is_active == True).all()

@router.post("/", response_model=Convenio)
def create_convenio(convenio: ConvenioCreate, db: Session = Depends(get_db)):
    db_convenio = ConvenioModel(
        slug=convenio.slug,
        name=convenio.name, 
        description=convenio.description,
        color=convenio.color
    )
    db.add(db_convenio)
    db.commit()
    db.refresh(db_convenio)
    return db_convenio

@router.get("/{convenio_id}", response_model=Convenio)
def get_convenio(convenio_id: int, db: Session = Depends(get_db)):
    convenio = db.query(ConvenioModel).filter(ConvenioModel.id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convenio not found")
    return convenio
