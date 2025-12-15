from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base import Base

class Articulo(Base):
    __tablename__ = "articulos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=False)
    is_active = Column(Boolean, default=True)


