
import requests
import json
import random
import string
import sys
import os

# Configuration
# BASE_URL = "https://intelligent-vitality-production.up.railway.app" # Cloud
BASE_URL = "http://localhost:8000" # Local (ensure server is running or proxy active)
# actually, better to test against LOCAL first if I can run the server, but I can't easily spin up the server here.
# I will assume I can run against the cloud URL if I want to reproduce USER experience, OR 
# I can use "localhost" if I start the server in a background process.
# Given I'm in the Agent environment, I should probably rely on the code I have. 
# But wait, I can modify the script to use the local DB functions directly to simulate the API "Logic" if I can't hit the API.
# BUT, the user issue might be network/API layer.
# Let's try to hit the deployed URL first? No, I don't have internet access for that usually? 
# I DO have `read_url_content` but not generic `requests` for everything? 
# Wait, `run_command` can run python scripts that use `requests`. 

# Let's try to use the Local DB + Router Functions directly (Integration Test style) to avoid network issues.
# This ensures we test the LOGIC.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import SessionLocal
from app.modules.usuarios.router import create_user, create_profile, get_my_profiles
from app.schemas.user import UserCreate
from app.schemas.profile import ProfileCreate
from app.modules.usuarios.models import User

def generate_random_email():
    return f"test_user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}@example.com"

def simulate_flow():
    db = SessionLocal()
    email = generate_random_email()
    password = "password123"
    
    print(f"🚀 Starting Onboarding Simulation for: {email}")
    
    try:
        # 1. Create User (Register)
        print("\n1️⃣ Registering User...")
        user_in = UserCreate(
            email=email,
            password=password,
            full_name="Test User Flow",
            company_slug="azul-handling", # Initial slug often sent
            preferred_name="",
            job_group="",
            salary_level="",
            contract_type=""
        )
        
        # We need to mock 'current_user' for subsequent calls, so we get the DB object
        # But wait, router functions depend on Depends() which I can't easily mock in a script without FastAPI test client.
        # So I will call the LOGIC directly or use TestClient? 
        # Using DB directly coupled with Model logic is safer for this environment.
        
        # Actually, let's just use the router functions but provide the dependencies manually.
        
        created_user = create_user(user_in, db)
        print(f"   ✅ User Created: ID {created_user.id}")
        
        # 2. Update Profile Phase (Preferred Name)
        print("\n2️⃣ Updating Preferred Name...")
        created_user.preferred_name = "Simulated Uli"
        db.commit()
        db.refresh(created_user)
        print(f"   ✅ Name Updated: {created_user.preferred_name}")
        
        # 3. Create Profile (The problematic step)
        print("\n3️⃣ Creating Professional Profile...")
        profile_in = ProfileCreate(
            alias="Mi Perfil Simulado",
            company_slug="easyjet",
            job_group="Serv. Auxiliares",
            salary_level="Nivel 3",
            contract_percentage=100,
            contract_type="Fijo",
            is_active=True
        )
        
        # CALLING THE ROUTER FUNCTION DIRECTLY
        # def create_profile(profile: ProfileCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
        
        created_profile = create_profile(profile_in, db, created_user)
        print(f"   ✅ Profile Created: ID {created_profile.id}")
        print(f"      Active: {created_profile.is_active}")
        
        # 4. Verify Fetch
        print("\n4️⃣ Verifying Persistence (Get Profiles)...")
        profiles = get_my_profiles(db, created_user)
        
        if len(profiles) > 0:
            print(f"   ✅ SUCCESS! Found {len(profiles)} profiles.")
            print(f"   - {profiles[0].alias} (Active: {profiles[0].is_active})")
        else:
            print("   ❌ FAILURE! No profiles found after creation.")

    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_flow()
