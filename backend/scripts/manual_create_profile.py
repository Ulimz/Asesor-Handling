
import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User, UserProfile
from app.schemas.profile import ProfileCreate

def manual_create():
    db = SessionLocal()
    user_id = 59
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        print("❌ User 59 not found.")
        return

    print(f"👤 Testing creation for User: {user.full_name} (Preferred: {user.preferred_name})")
    
    # Simulate Payload
    profile_data = ProfileCreate(
        alias="Test Profile Script",
        company_slug="easyjet",
        job_group="Serv. Auxiliares",
        salary_level="Nivel 3",
        contract_percentage=100,
        contract_type="Fijo",
        is_active=True
    )
    
    try:
        # LOGIC PASTE FROM ROUTER
        existing_count = db.query(UserProfile).filter(UserProfile.user_id == user.id).count()
        is_first = existing_count == 0
        print(f"   Existing profiles: {existing_count}")
        
        db_profile = UserProfile(
            user_id=user.id,
            alias=profile_data.alias,
            company_slug=profile_data.company_slug,
            job_group=profile_data.job_group,
            salary_level=profile_data.salary_level,
            contract_percentage=profile_data.contract_percentage,
            contract_type=profile_data.contract_type,
            is_active=True if is_first else profile_data.is_active
        )
        
        if db_profile.is_active:
             print("   Deactivating others...")
             db.query(UserProfile).filter(UserProfile.user_id == user.id).update({"is_active": False})
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        print(f"✅ Success! Created Profile ID: {db_profile.id}")
        
    except Exception as e:
        print(f"❌ Error during manual creation: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    manual_create()
