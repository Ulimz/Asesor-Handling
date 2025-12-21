from pydantic import BaseModel
from datetime import date

class JurisprudenciaBase(BaseModel):
    title: str
    summary: str
    content: str
    date: date
    source: str
    is_active: bool = True

class JurisprudenciaCreate(JurisprudenciaBase):
    pass

class Jurisprudencia(JurisprudenciaBase):
    id: int
    class Config:
        from_attributes = True
