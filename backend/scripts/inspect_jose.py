
import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User, UserProfile

def check_jose():
    db = SessionLocal()
    print("🔍 Checking User 'jose@got.es'...", flush=True)
    
    user = db.query(User).filter(User.email == "jose@got.es").first()
    
    if user:
        print(f"✅ User FOUND: ID {user.id} | Name: {user.full_name}", flush=True)
        
        profiles = db.query(UserProfile).filter(UserProfile.user_id == user.id).all()
        if profiles:
            print(f"   ✅ FOUND {len(profiles)} PROFILES:", flush=True)
            for p in profiles:
                print(f"      - ID: {p.id} | Alias: {p.alias} | Active: {p.is_active} | Company: {p.company_slug}", flush=True)
        else:
            print("   ❌ NO PROFILES FOUND for this user.", flush=True)
            
    else:
        print("❌ User 'jose@got.es' NOT FOUND.", flush=True)

    db.close()

if __name__ == "__main__":
    check_jose()
