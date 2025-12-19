#!/usr/bin/env python3
"""
Check what was seeded in EasyJet tables
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryTable

def check_easyjet_tables():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("🔍 EasyJet Salary Tables:\n")
    
    tables = db.query(SalaryTable).filter(SalaryTable.company_id == "easyjet").limit(10).all()
    
    for table in tables:
        print(f"Group: {table.group}")
        print(f"Level: {table.level}")
        print(f"Concept: {table.concept}")
        print(f"Amount: {table.amount}")
        print("---")
    
    db.close()

if __name__ == "__main__":
    check_easyjet_tables()
