from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.reclamacion import Reclamacion, ReclamacionCreate
from .models import Reclamacion as ReclamacionModel

router = APIRouter(prefix="/reclamaciones", tags=["reclamaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Reclamacion)
def create_reclamacion(reclamacion: ReclamacionCreate, db: Session = Depends(get_db)):
    db_reclamacion = ReclamacionModel(**reclamacion.dict())
    db.add(db_reclamacion)
    db.commit()
    db.refresh(db_reclamacion)
    return db_reclamacion

from datetime import date
from pydantic import BaseModel

class GenerateClaimInput(BaseModel):
    type: str # 'vacaciones', 'nomina', 'horario'
    user_name: str
    company_name: str
    details: str
    date: date = date.today()

class GenerateClaimOutput(BaseModel):
    title: str
    content: str

@router.post("/generate", response_model=GenerateClaimOutput)
def generate_reclamacion(data: GenerateClaimInput):
    if data.type == "vacaciones":
        title = "Solicitud de Vacaciones Anuales"
        template = f"""A la atención del Departamento de RRHH de {data.company_name},

Por medio de la presente, yo, D./Dña. {data.user_name}, solicito el disfrute de mis vacaciones anuales correspondientes al año en curso.

Detalles de la solicitud:
{data.details}

Esta solicitud se realiza con la antelación estipulada en el Convenio Colectivo aplicable.

Quedo a la espera de su confirmación por escrito.

Atentamente,
{data.user_name}
Fecha: {data.date}"""

    elif data.type == "nomina":
        title = "Reclamación de Cantidades en Nómina"
        template = f"""A la atención del Departamento de Nóminas de {data.company_name},

Yo, D./Dña. {data.user_name}, expongo que he detectado discrepancias en mi nómina reciente.

Detalles de la reclamación:
{data.details}

Solicito la revisión de dichos conceptos y el abono de las diferencias correspondientes a la mayor brevedad posible.

Atentamente,
{data.user_name}
Fecha: {data.date}"""
        
    elif data.type == "horario":
        title = "Reclamación sobre Modificación de Horario"
        template = f"""A la atención del Departamento de Operaciones de {data.company_name},

Yo, D./Dña. {data.user_name}, presento esta reclamación en relación a la modificación de mi horario laboral.

Exposición:
{data.details}

Considero que esta modificación no se ajusta a lo establecido en la normativa vigente y solicito su rectificación.

Atentamente,
{data.user_name}
Fecha: {data.date}"""

    else:
        title = "Escrito Formal Genérico"
        template = f"""A la atención de {data.company_name},

Yo, D./Dña. {data.user_name}, expongo lo siguiente:

{data.details}

Solicito que se atienda a esta petición conforme a derecho.

Atentamente,
{data.user_name}
Fecha: {data.date}"""

    return {"title": title, "content": template}

@router.get("/{reclamacion_id}", response_model=Reclamacion)
def get_reclamacion(reclamacion_id: int, db: Session = Depends(get_db)):
    reclamacion = db.query(ReclamacionModel).filter(ReclamacionModel.id == reclamacion_id).first()
    if not reclamacion:
        raise HTTPException(status_code=404, detail="Reclamacion not found")
    return reclamacion
