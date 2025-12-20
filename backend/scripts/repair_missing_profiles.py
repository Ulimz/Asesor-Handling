
import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User, UserProfile

def repair_profiles(dry_run=True):
    db = SessionLocal()
    print(f"🛠️ STARTING PROFILE REPAIR (Dry Run: {dry_run})")
    
    # 1. Get all users
    users = db.query(User).all()
    print(f"👥 Scanning {len(users)} users...")
    
    repaired_count = 0
    skipped_count = 0
    
    for user in users:
        # Check if user has legacy data
        has_data = user.company_slug and user.job_group
        
        # Check if user has profiles
        profile_count = db.query(UserProfile).filter(UserProfile.user_id == user.id).count()
        
        if has_data and profile_count == 0:
            print(f"   ⚠️  User {user.id} ({user.email}) has data but NO profiles. REPAIRING...")
            
            if not dry_run:
                try:
                    new_profile = UserProfile(
                        user_id=user.id,
                        alias=f"{user.company_slug.capitalize()} (Recuperado)",
                        company_slug=user.company_slug,
                        job_group=user.job_group,
                        salary_level=user.salary_level or "Nivel 1", # Fallback if missing
                        contract_percentage=100,
                        contract_type=user.contract_type or "Fijo",
                        is_active=True
                    )
                    db.add(new_profile)
                    db.commit()
                    print(f"      ✅ Created Profile ID: {new_profile.id}")
                    repaired_count += 1
                except Exception as e:
                    print(f"      ❌ Failed to repair: {e}")
                    db.rollback()
            else:
                 print(f"      [DRY RUN] Would create profile for {user.company_slug}")
                 repaired_count += 1
                 
        elif profile_count > 0:
            # print(f"   ✅ User {user.id} already has {profile_count} profiles. Skipping.")
            skipped_count += 1
        else:
            # No data and no profiles (maybe clean account)
            pass
            
    print(f"\n📊 SUMMARY:")
    print(f"   - Users Scanned: {len(users)}")
    print(f"   - Profiles Repaired/Pending: {repaired_count}")
    print(f"   - Users Skipped (Already OK): {skipped_count}")
    
    db.close()

if __name__ == "__main__":
    # Check for argument to run for real
    is_dry = True
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        is_dry = False
        
    repair_profiles(dry_run=is_dry)
