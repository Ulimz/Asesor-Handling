#!/usr/bin/env python3
"""
Verify Convenio Sector data in database
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryTable, SalaryConceptDefinition

def verify_sector():
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
        print("🔍 Checking CONVENIO-SECTOR data in database...\n")
        
        # Check SalaryTable
        print("📊 Salary Tables:")
        tables = db.query(SalaryTable).filter(SalaryTable.company_id == "convenio-sector").all()
        print(f"   Found {len(tables)} entries")
        if tables:
            for t in tables[:3]:
                print(f"   - {t.group} / {t.level}: {t.amount}€")
        
        # Check SalaryConceptDefinition
        print("\n🔧 Concept Definitions:")
        concepts = db.query(SalaryConceptDefinition).filter(
            SalaryConceptDefinition.company_slug == "convenio-sector"
        ).all()
        print(f"   Found {len(concepts)} entries")
        if concepts:
            for c in concepts[:5]:
                print(f"   - {c.code}: {c.name} ({c.default_price}€)")
        
        print("\n✅ Verification complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_sector()
