import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Setup Environment
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# OVERRIDE DATABASE_URL with CLOUD_DATABASE_URL
cloud_db = os.getenv("CLOUD_DATABASE_URL")
if cloud_db:
    print("🌍 Targeting Cloud Database...")
    if cloud_db.startswith("postgres://"):
        cloud_db = cloud_db.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = cloud_db

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_concepts():
    db = SessionLocal()
    
    try:
        # 1. Update Name for HC_ESPECIAL
        print("Updating HC_ESPECIAL name...")
        db.execute(text("UPDATE salary_concept_definitions SET name = 'Horas Complementarias Especiales' WHERE code = 'HC_ESPECIAL' AND company_slug = 'azul'"))
        
        # 2. Delete Obsolete PLUS_FRACC (The generic one, not _1, _2, _3)
        # Assuming the generic one has code 'PLUS_FRACC' or similar that matches but isn't the specific ones.
        # Use exact code match if known, or careful filtering.
        # Based on user description "Plus Jornada Fraccionada" likely code "PLUS_FRACC" or "PLUS_FRACCIONADA"
        
        print("Finding obsolete 'Plus Jornada Fraccionada'...")
        # Check what we have first
        result = db.execute(text("SELECT code, name FROM salary_concept_definitions WHERE company_slug = 'azul' AND code LIKE 'PLUS_FRACC%'"))
        for row in result:
            print(f"Found: {row.code} - {row.name}")
            if row.code == 'PLUS_FRACC' or row.name == 'Plus de Jornada Fraccionada':
                print(f"Deleting obsolete concept: {row.code}")
                db.execute(text(f"DELETE FROM salary_concept_definitions WHERE code = '{row.code}' AND company_slug = 'azul'"))

        db.commit()
        print("✅ Cleanup Completed.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_concepts()
