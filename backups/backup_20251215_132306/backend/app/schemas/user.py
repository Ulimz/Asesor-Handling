from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    company_slug: str | None = None
    preferred_name: str | None = None
    job_group: str | None = None
    salary_level: int | None = None
    contract_type: str | None = None

class UserProfileUpdate(BaseModel):
    preferred_name: str | None = None
    company_slug: str | None = None
    job_group: str | None = None
    salary_level: int | None = None
    contract_type: str | None = None
    seniority_date: str | None = None

class User(UserBase):
    id: int
    preferred_name: str | None = None
    company_slug: str | None = None
    job_group: str | None = None
    salary_level: int | None = None
    contract_type: str | None = None
    seniority_date: str | None = None
    
    class Config:
        orm_mode = True
