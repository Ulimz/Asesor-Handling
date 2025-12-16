
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.user import User, UserCreate, UserProfileUpdate
from .models import User as UserModel
from app.services.jwt_service import create_access_token, verify_token, get_password_hash, verify_password

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user_id = int(payload.get("sub"))
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        db_user = UserModel(
            email=user.email, 
            full_name=user.full_name, 
            hashed_password=get_password_hash(user.password),
            company_slug=user.company_slug,
            preferred_name=user.preferred_name,
            job_group=user.job_group,
            salary_level=user.salary_level,
            contract_type=user.contract_type
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        print(f"CRITICAL ERROR creating user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=User)
def update_user_profile(
    profile_data: UserProfileUpdate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Update fields only if provided
    if profile_data.preferred_name is not None:
        current_user.preferred_name = profile_data.preferred_name
    if profile_data.company_slug is not None:
        current_user.company_slug = profile_data.company_slug
    if profile_data.job_group is not None:
        current_user.job_group = profile_data.job_group
    if profile_data.salary_level is not None:
        current_user.salary_level = profile_data.salary_level
    if profile_data.contract_type is not None:
        current_user.contract_type = profile_data.contract_type
    if profile_data.seniority_date is not None:
        current_user.seniority_date = profile_data.seniority_date
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return None

# ==========================================
# PHASE 2: MULTI-PROFILE ENDPOINTS
# ==========================================

from app.schemas.profile import Profile as PydanticProfile, ProfileCreate, ProfileUpdate
from .models import UserProfile

@router.get("/me/profiles", response_model=list[PydanticProfile])
def get_my_profiles(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """List all professional profiles for the current user."""
    return db.query(UserProfile).filter(UserProfile.user_id == current_user.id).all()

@router.post("/me/profiles", response_model=PydanticProfile)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Create a new professional profile."""
    # Ensure only one is active if it's the first one
    existing_count = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).count()
    is_first = existing_count == 0
    
    db_profile = UserProfile(
        user_id=current_user.id,
        alias=profile.alias,
        company_slug=profile.company_slug,
        job_group=profile.job_group,
        salary_level=profile.salary_level,
        contract_percentage=profile.contract_percentage,
        contract_type=profile.contract_type,
        is_active=True if is_first else profile.is_active  # Auto-activate first profile
    )
    
    if db_profile.is_active:
        # Deactivate others
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).update({"is_active": False})
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.put("/me/profiles/{profile_id}", response_model=PydanticProfile)
def update_profile(
    profile_id: int, 
    profile_data: ProfileUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """Update a specific profile."""
    db_profile = db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == current_user.id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    if profile_data.alias is not None: db_profile.alias = profile_data.alias
    if profile_data.company_slug is not None: db_profile.company_slug = profile_data.company_slug
    if profile_data.job_group is not None: db_profile.job_group = profile_data.job_group
    if profile_data.salary_level is not None: db_profile.salary_level = profile_data.salary_level
    if profile_data.contract_percentage is not None: db_profile.contract_percentage = profile_data.contract_percentage
    if profile_data.contract_type is not None: db_profile.contract_type = profile_data.contract_type
    
    # Handle Active Switch
    if profile_data.is_active is not None:
        if profile_data.is_active:
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).update({"is_active": False})
        db_profile.is_active = profile_data.is_active
        
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.delete("/me/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Delete a profile."""
    db_profile = db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == current_user.id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(db_profile)
    db.commit()
    return None

@router.post("/me/profiles/{profile_id}/activate", response_model=PydanticProfile)
def activate_profile(profile_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """Set a profile as the active one."""
    db_profile = db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == current_user.id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Deactivate all
    db.query(UserProfile).filter(UserProfile.user_id == current_user.id).update({"is_active": False})
    
    # Activate target
    db_profile.is_active = True
    db.commit()
    db.refresh(db_profile)
    return db_profile
