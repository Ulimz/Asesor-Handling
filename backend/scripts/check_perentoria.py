#!/usr/bin/env python3
"""
Check PLUS_HORA_PERENTORIA concept definition
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryConceptDefinition

def check_perentoria():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    concept = db.query(SalaryConceptDefinition).filter(
        SalaryConceptDefinition.company_slug == "easyjet",
        SalaryConceptDefinition.code == "PLUS_HORA_PERENTORIA"
    ).first()
    
    if concept:
        print(f"✅ Found PLUS_HORA_PERENTORIA:")
        print(f"   Name: {concept.name}")
        print(f"   Input Type: {concept.input_type}")
        print(f"   Default Price: {concept.default_price}")
        print(f"   Level Values: {concept.level_values}")
    else:
        print("❌ PLUS_HORA_PERENTORIA not found!")
    
    db.close()

if __name__ == "__main__":
    check_perentoria()
