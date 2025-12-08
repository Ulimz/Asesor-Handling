from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.db.base import Base

class Reclamacion(Base):
    __tablename__ = "reclamaciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="pendiente")


