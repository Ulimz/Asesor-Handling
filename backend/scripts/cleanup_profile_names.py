
import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import UserProfile

def cleanup_names():
    db = SessionLocal()
    print("🧹 Cleaning up profile names...")
    
    # Find profiles with value
    profiles = db.query(UserProfile).filter(UserProfile.alias.like("%(Recuperado)%")).all()
    
    count = 0
    for p in profiles:
        old_alias = p.alias
        # Remove the suffix and any potential double spaces
        new_alias = old_alias.replace(" (Recuperado)", "").replace("(Recuperado)", "").strip()
        
        p.alias = new_alias
        count += 1
        print(f"   ✨ Renamed ID {p.id}: '{old_alias}' -> '{new_alias}'")
    
    if count > 0:
        db.commit()
        print(f"✅ Successfully cleaned {count} profiles.")
    else:
        print("✅ No profiles needed cleaning.")
    
    db.close()

if __name__ == "__main__":
    cleanup_names()
