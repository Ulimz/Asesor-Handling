from pydantic import BaseModel

class ArticuloBase(BaseModel):
    title: str
    content: str
    convenio_id: int
    is_active: bool = True

class ArticuloCreate(ArticuloBase):
    pass

class Articulo(ArticuloBase):
    id: int
    class Config:
        orm_mode = True
