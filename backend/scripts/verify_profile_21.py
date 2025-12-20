
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User, UserProfile

def check_p21():
    db = SessionLocal()
    print("🔍 Checking Profile 21...", flush=True)
    
    p = db.query(UserProfile).filter(UserProfile.id == 21).first()
    
    if p:
        print(f"✅ Profile 21 FOUND!", flush=True)
        print(f"   - User ID: {p.user_id}", flush=True)
        print(f"   - Alias: {p.alias}", flush=True)
        print(f"   - Active: {p.is_active}", flush=True)
        
        user = db.query(User).filter(User.id == p.user_id).first()
        if user:
            print(f"   - Owner: {user.full_name} ({user.email})", flush=True)
    else:
        print("❌ Profile 21 NOT FOUND.", flush=True)

    db.close()

if __name__ == "__main__":
    check_p21()
