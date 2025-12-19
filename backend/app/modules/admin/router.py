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
    role: str = "user"  # "user" | "vip" | "admin"
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

# --- Role Management ---

class UpdateRoleRequest(BaseModel):
    role: str  # "user" | "vip" | "admin"

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser)
):
    # Validate role
    valid_roles = ["user", "vip", "admin"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(valid_roles)}"
        )
    
    # Get target user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # SUPER ADMIN PROTECTION: User ID 1 is untouchable
    if user.id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario tiene privilegios de Super Administrador y no puede ser modificado"
        )
    
    # Prevent admin from removing their own admin privileges
    if user.id == current_user.id and request.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes quitarte tus propios privilegios de administrador"
        )
    
    # Update role and is_superuser
    user.role = request.role
    user.is_superuser = (request.role == "admin")
    
    db.commit()
    db.refresh(user)
    
    return {"message": f"Rol actualizado a '{request.role}'", "user": AdminUserSchema.from_orm(user)}

# --- Status Management ---

class UpdateStatusRequest(BaseModel):
    is_active: bool

@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser)
):
    # Get target user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # SUPER ADMIN PROTECTION: ulises_sevi@hotmail.com is untouchable
    SUPER_ADMIN_EMAIL = "ulises_sevi@hotmail.com"
    if user.email.lower() == SUPER_ADMIN_EMAIL.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario tiene privilegios de Super Administrador y no puede ser modificado"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id and not request.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    # Update status
    user.is_active = request.is_active
    
    db.commit()
    db.refresh(user)
    
    return {"message": f"Usuario {'activado' if request.is_active else 'desactivado'}", "user": AdminUserSchema.from_orm(user)}
