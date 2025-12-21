from pydantic import BaseModel

class ConvenioBase(BaseModel):
    slug: str
    name: str
    description: str
    color: str = "#334155"
    is_active: bool = True

class ConvenioCreate(ConvenioBase):
    pass

class Convenio(ConvenioBase):
    id: int
    class Config:
        from_attributes = True
