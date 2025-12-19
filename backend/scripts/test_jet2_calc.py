#!/usr/bin/env python3
"""
Test Jet2 Calculator (uses Convenio Sector)
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

def test_jet2():
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
        print("🧪 Testing JET2 Calculator (should use Convenio Sector data)\n")
        
        req = CalculationRequest(
            company_slug="jet2",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            dynamic_variables={}
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        print(f"Result: {res.gross_monthly_total:.2f}€")
        print(f"Expected: 1330.88€ (from Sector table)")
        
        if abs(res.gross_monthly_total - 1330.88) < 1.0:
            print("\n✅ PASS: Jet2 is using Convenio Sector data correctly!")
        else:
            print(f"\n❌ FAIL: Still using fallback or wrong data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_jet2()
