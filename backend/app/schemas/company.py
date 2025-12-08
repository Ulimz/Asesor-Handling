from pydantic import BaseModel

class CompanyBase(BaseModel):
    name: str
    sector: str
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    class Config:
        orm_mode = True
