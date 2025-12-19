#!/usr/bin/env python3
"""
Debug Calculator Service for Convenio Sector
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.services.calculator_service import CalculatorService
from app.schemas.salary import CalculationRequest
from app.db.models import SalaryTable

def debug_calculator():
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
        print("🔍 Debugging Calculator for Convenio Sector\n")
        
        # Check what's in the database
        print("📊 Database Query:")
        entry = db.query(SalaryTable).filter(
            SalaryTable.company_id == "convenio-sector",
            SalaryTable.group == "Administrativos",
            SalaryTable.level == "Nivel entrada",
            SalaryTable.concept == "SALARIO_BASE_ANUAL"
        ).first()
        
        if entry:
            print(f"   Found: {entry.amount}€ (annual)")
            print(f"   Expected monthly (14 pagas): {entry.amount / 14:.2f}€")
        else:
            print("   ❌ NOT FOUND in database")
        
        # Now test the actual calculator
        print("\n🧮 Calculator Service Test:")
        req = CalculationRequest(
            company_slug="convenio-sector",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            dynamic_variables={}
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        print(f"   Result: {res.gross_monthly_total:.2f}€")
        print(f"   Base Salary Item: {res.base_salary:.2f}€")
        
        print("\n📋 Breakdown:")
        for item in res.breakdown:
            print(f"   - {item.name}: {item.amount:.2f}€")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_calculator()
