
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.models import User, UserProfile

def check_profiles():
    db = SessionLocal()
    print("🔍 Inspecting Database for User Profiles...")
    
    users = db.query(User).filter(User.full_name.ilike('%uli%')).all() # Filter by name
    if not users:
         print("No users found with name 'Uli/Juli'. Checking all.")
         users = db.query(User).limit(10).all()

    
    print(f"👥 Found {len(users)} total users.")
    
    for user in users:
        print(f"\n👤 User: {user.full_name} (ID: {user.id}) | Email: {user.email}")
        
        # Check Profiles
        profiles = db.query(UserProfile).filter(UserProfile.user_id == user.id).all()
        
        if profiles:
            print(f"   ✅ Found {len(profiles)} profiles:")
            for p in profiles:
                print(f"      - ID: {p.id} | Alias: {p.alias} | Active: {p.is_active} | Company: {p.company_slug}")
        else:
            print("   ❌ NO PROFILES FOUND.")

    db.close()

if __name__ == "__main__":
    check_profiles()
