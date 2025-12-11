import os
import sys
from dotenv import load_dotenv

# Add backend to path so imports work
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load .env from backend directory
load_dotenv(os.path.join('backend', '.env'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.modules.usuarios import models as user_models
from app.services.jwt_service import get_password_hash

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Try CLOUD_DATABASE_URL
    DATABASE_URL = os.getenv("CLOUD_DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: Could not find DATABASE_URL or CLOUD_DATABASE_URL")
    sys.exit(1)

# Fix postgres:// if needed
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to DB: {DATABASE_URL[:20]}...")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("✅ Connected. Attempting to user...")
    
    # Create a test user
    test_email = "direct_test_db@example.com"
    
    # Check if exists
    existing = db.query(user_models.User).filter(user_models.User.email == test_email).first()
    if existing:
        print(f"⚠️ User {test_email} already exists. Deleting...")
        db.delete(existing)
        db.commit()
    
    new_user = user_models.User(
        email=test_email,
        full_name="Direct DB Test",
        hashed_password="hashed_password_dummy", # Creating dummy hash manually or import
        # Skipping get_password_hash import complexity if we can mock it, 
        # but models.py imports are standard.
        is_active=True,
        company_slug="iberia",
        job_group="Administrativo",
        salary_level=1,
        contract_type="Fijo"
    )
    
    print("Adding user...")
    db.add(new_user)
    db.commit()
    print("✅ User inserted successfully!")
    
    db.refresh(new_user)
    print(f"User ID: {new_user.id}")
    db.close()

except Exception as e:
    print("❌ ERROR:")
    print(e)
    # traceback
    import traceback
    traceback.print_exc()
