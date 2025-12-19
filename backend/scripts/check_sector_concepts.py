#!/usr/bin/env python3
"""
Check what variable concepts were loaded for Convenio Sector
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryConceptDefinition

def check_concepts():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🔍 Checking Variable Concepts for convenio-sector\n")
        
        concepts = db.query(SalaryConceptDefinition).filter(
            SalaryConceptDefinition.company_slug == "convenio-sector"
        ).all()
        
        print(f"Total concepts: {len(concepts)}\n")
        
        # Check specific problematic ones
        target_codes = ["HORA_EXTRA", "HORA_PERENTORIA", "PLUS_AD_PERSONAM"]
        
        for code in target_codes:
            concept = next((c for c in concepts if c.code == code), None)
            if concept:
                print(f"✅ {code}:")
                print(f"   Name: {concept.name}")
                print(f"   Default Price: {concept.default_price}")
                print(f"   Level Values: {concept.level_values}")
                print(f"   Input Type: {concept.input_type}")
            else:
                print(f"❌ {code}: NOT FOUND")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_concepts()
