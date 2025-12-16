from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Deprecated fields (kept for backward compatibility during migration)
    preferred_name = Column(String, nullable=True)
    company_slug = Column(String, nullable=True)
    job_group = Column(String, nullable=True)
    salary_level = Column(String, nullable=True)
    contract_type = Column(String, nullable=True)
    seniority_date = Column(String, nullable=True)

    # Relationships
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    alias = Column(String, nullable=False) # e.g. "Iberia"
    company_slug = Column(String, nullable=False)
    job_group = Column(String, nullable=False)
    salary_level = Column(String, nullable=False)
    
    contract_percentage = Column(Integer, default=100)
    contract_type = Column(String, default="indefinido")
    
    is_active = Column(Boolean, default=False) # Helper for "last used"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profiles")
