from pydantic import BaseModel
from datetime import date as dt_date

class ReclamacionBase(BaseModel):
    user_id: int
    company_id: int
    type: str
    description: str
    date: dt_date
    status: str = "pendiente"

class ReclamacionCreate(ReclamacionBase):
    pass

class Reclamacion(ReclamacionBase):
    id: int
    class Config:
        from_attributes = True
