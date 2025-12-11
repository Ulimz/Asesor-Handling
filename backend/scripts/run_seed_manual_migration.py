import json
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_path)

from app.db.models import SalaryConceptDefinition

# Load Cloud Env
load_dotenv(os.path.join(backend_path, '.env'))

# Ensure DATABASE_URL is set to CLOUD
if os.getenv("CLOUD_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.getenv("CLOUD_DATABASE_URL")
if os.getenv("DATABASE_URL", "").startswith("postgres://"):
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)

print(f"✅ Loaded Environment. Target DB: {os.getenv('DATABASE_URL')[:30]}...")

engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(bind=engine)

def seed_manual_migration():
    db = SessionLocal()
    
    json_path = os.path.join(backend_path, "data", "concepts", "manual_migration.json")
    if not os.path.exists(json_path):
        print("❌ Error: manual_migration.json not found!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        concepts = json.load(f)

    print(f"🚀 Seeding {len(concepts)} manual concepts...")
    
    count = 0
    for c in concepts:
        exists = db.query(SalaryConceptDefinition).filter_by(
            company_slug=c['company_slug'],
            code=c['variable_code']
        ).first()

        if not exists:
            new_concept = SalaryConceptDefinition(
                company_slug=c['company_slug'],
                name=c['name'],
                code=c['variable_code'],
                description=c['description'],
                input_type=c['type'],
                default_price=c['default_price']
            )
            db.add(new_concept)
            print(f"   ➕ Added: {c['name']} ({c['company_slug']})")
            count += 1
        else:
             print(f"   ⚠️ Skipped (exists): {c['name']}")

    db.commit()
    print(f"✅ Successfully migrated {count} custom concepts to Cloud.")
    db.close()

if __name__ == "__main__":
    seed_manual_migration()
