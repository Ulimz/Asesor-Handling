from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.modules.usuarios.models import User, UserProfile
from app.modules.usuarios.router import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/admin",
    tags=["Panel de Administración"],
    responses={404: {"description": "Not found"}},
)

# --- Dependency ---
def require_superuser(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Administrador."
        )
    return current_user

# --- Schemas (Local for simplicity or move to schemas/admin.py) ---
class AdminUserSchema(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at_approx: datetime | None = None # We don't have created_at in User model yet, but UserProfile has.

    class Config:
        from_attributes = True

class AdminStats(BaseModel):
    total_users: int
    total_profiles: int
    active_users: int

# --- Endpoints ---

@router.get("/stats", response_model=AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    _ = Depends(require_superuser)
):
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_profiles = db.query(UserProfile).count()
    
    return {
        "total_users": total_users,
        "total_profiles": total_profiles,
        "active_users": active_users
    }

@router.get("/users", response_model=List[AdminUserSchema])
def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: Session = Depends(get_db),
    _ = Depends(require_superuser)
):
    query = db.query(User)
    
    if search:
        query = query.filter(User.email.contains(search) | User.full_name.contains(search))
        
    users = query.offset(skip).limit(limit).all()
    return users
