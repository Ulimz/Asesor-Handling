from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Profile Fields (Phase 2)
    preferred_name = Column(String, nullable=True)
    company_slug = Column(String, nullable=True)
    job_group = Column(String, nullable=True)     # e.g. Administrativo, Tecnico
    salary_level = Column(Integer, nullable=True) # e.g. 1, 2, 3
    contract_type = Column(String, nullable=True) # e.g. Fijo, Eventual
    seniority_date = Column(String, nullable=True) # Stored as ISO date string for simplicity


