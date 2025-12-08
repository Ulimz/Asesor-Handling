from pydantic import BaseModel
from datetime import date

class ReclamacionBase(BaseModel):
    user_id: int
    company_id: int
    type: str
    description: str
    date: date
    status: str = "pendiente"

class ReclamacionCreate(ReclamacionBase):
    pass

class Reclamacion(ReclamacionBase):
    id: int
    class Config:
        orm_mode = True
