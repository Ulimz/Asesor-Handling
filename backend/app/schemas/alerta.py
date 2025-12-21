from pydantic import BaseModel
from datetime import datetime

class AlertaBase(BaseModel):
    title: str
    description: str
    type: str  # convenio, sentencia, reforma
    created_at: datetime
    is_active: bool = True

class AlertaCreate(AlertaBase):
    pass

class Alerta(AlertaBase):
    id: int
    class Config:
        from_attributes = True
