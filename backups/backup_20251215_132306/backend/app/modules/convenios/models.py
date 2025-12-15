from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class Convenio(Base):
    __tablename__ = "convenios"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    color = Column(String, nullable=False, default="#334155")
    is_active = Column(Boolean, default=True)


