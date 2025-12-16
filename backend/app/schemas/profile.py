from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProfileBase(BaseModel):
    alias: str
    company_slug: str
    job_group: str
    salary_level: str
    contract_percentage: Optional[int] = 100
    contract_type: Optional[str] = "indefinido"
    is_active: Optional[bool] = False

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    alias: Optional[str] = None
    company_slug: Optional[str] = None
    job_group: Optional[str] = None
    salary_level: Optional[str] = None
    contract_percentage: Optional[int] = None
    contract_type: Optional[str] = None
    is_active: Optional[bool] = None

class Profile(ProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
