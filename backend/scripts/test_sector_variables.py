#!/usr/bin/env python3
"""
Test variable concepts calculation for Jet2 (Convenio Sector)
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

def test_variable_concepts():
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
        print("🧪 Testing Variable Concepts for JET2 (Convenio Sector)\n")
        
        # Test with Administrativos / Nivel entrada
        req = CalculationRequest(
            company_slug="jet2",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            contract_percentage=100,
            dynamic_variables={
                "HORA_EXTRA": 10,  # 10 horas extra
                "HORA_PERENTORIA": 5,  # 5 horas perentorias
                "PLUS_AD_PERSONAM": 150.0  # 150€ garantía personal
            }
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        print(f"\n📊 Results:")
        print(f"   Base Salary: {res.gross_monthly_total:.2f}€")
        print(f"\n   Breakdown:")
        for item in res.breakdown:
            print(f"   - {item.name}: {item.amount:.2f}€")
        
        # Expected values for Administrativos/Nivel entrada:
        # HORA_EXTRA: 16.33€/hora × 10 = 163.30€
        # HORA_PERENTORIA: 19.05€/hora × 5 = 95.25€
        # PLUS_AD_PERSONAM: 150€
        
        print(f"\n✅ Expected:")
        print(f"   - Horas Extra (10h × 16.33€): 163.30€")
        print(f"   - Horas Perentorias (5h × 19.05€): 95.25€")
        print(f"   - Garantía Personal: 150.00€")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_variable_concepts()
