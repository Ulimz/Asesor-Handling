from sqlalchemy import Column, Integer, String, Boolean, Date
from app.db.base import Base

class Jurisprudencia(Base):
    __tablename__ = "jurisprudencia"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    source = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


