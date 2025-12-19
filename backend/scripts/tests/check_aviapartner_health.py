
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.services.calculator_service import CalculatorService
from app.schemas.salary import CalculationRequest

def run_health_check():
    print("🛡️  INITIATING AVIAPARTNER SHIELD PROTOCOL (Health Check)...")
    
    # DB Connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ CRITICAL: No DATABASE_URL set.")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    all_passed = True
    
    # --- TEST 1: CALCULATOR (Base Salary) ---
    print("\n🧪 [1/3] Testing Calculator (Base Salary for Aviapartner)...")
    try:
        req = CalculationRequest(
            company_slug="aviapartner",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            dynamic_variables={}
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        expected_annual = 18816.45
        expected_monthly = expected_annual / 14
        
        if abs(res.gross_monthly_total - expected_monthly) < 1.0:
            print(f"   ✅ PASS: Base salary correctly calculated as {res.gross_monthly_total:.2f}€/month")
        else:
            print(f"   ❌ FAIL: Expected {expected_monthly:.2f}€, got {res.gross_monthly_total:.2f}€")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    # --- TEST 2: CALCULATOR (Plus Nocturnidad) ---
    print("\n🧪 [2/3] Testing Calculator (Plus Nocturnidad)...")
    try:
        req = CalculationRequest(
            company_slug="aviapartner",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            dynamic_variables={
                "PLUS_NOCT": 10.0
            }
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        expected_noct = 10.0 * 1.62
        noct_item = next((i for i in res.breakdown if "Nocturnidad" in i.name), None)
        
        if noct_item and abs(noct_item.amount - expected_noct) < 0.1:
            print(f"   ✅ PASS: Nocturnidad correctly calculated as {noct_item.amount:.2f}€")
        else:
            if noct_item:
                print(f"   ❌ FAIL: Expected {expected_noct:.2f}€, got {noct_item.amount:.2f}€")
            else:
                print("   ❌ FAIL: Nocturnidad concept NOT found in breakdown.")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    # --- TEST 3: CALCULATOR (Variable Concepts with level_values) ---
    print("\n🧪 [3/3] Testing Variable Concepts (Horas Extra, Perentorias, HC Especial)...")
    try:
        req = CalculationRequest(
            company_slug="aviapartner",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            contract_percentage=100,
            dynamic_variables={
                "HORA_EXTRA": 10,
                "HORA_PERENTORIA": 5,
                "HC_ESPECIAL": 8
            }
        )
        
        res = service.calculate_smart_salary(req)
        
        hora_extra = next((item for item in res.breakdown if "Extraordinaria" in item.name), None)
        hora_perentoria = next((item for item in res.breakdown if "Perentoria" in item.name), None)
        hc_especial = next((item for item in res.breakdown if "Complementaria Especial" in item.name), None)
        
        # Expected values for Administrativos/Nivel entrada:
        # HORA_EXTRA: 16.48€/hora × 10 = 164.80€
        # HORA_PERENTORIA: 19.23€/hora × 5 = 96.15€
        # HC_ESPECIAL: 19.23€/hora × 8 = 153.84€
        
        tests_passed = True
        if hora_extra and abs(hora_extra.amount - 164.80) < 0.1:
            print(f"   ✅ PASS: Horas Extra = {hora_extra.amount:.2f}€")
        else:
            print(f"   ❌ FAIL: Horas Extra = {hora_extra.amount if hora_extra else 0:.2f}€ (expected 164.80€)")
            tests_passed = False
            
        if hora_perentoria and abs(hora_perentoria.amount - 96.15) < 0.1:
            print(f"   ✅ PASS: Horas Perentorias = {hora_perentoria.amount:.2f}€")
        else:
            print(f"   ❌ FAIL: Horas Perentorias = {hora_perentoria.amount if hora_perentoria else 0:.2f}€ (expected 96.15€)")
            tests_passed = False
            
        if hc_especial and abs(hc_especial.amount - 153.84) < 0.1:
            print(f"   ✅ PASS: HC Especial = {hc_especial.amount:.2f}€")
        else:
            print(f"   ❌ FAIL: HC Especial = {hc_especial.amount if hc_especial else 0:.2f}€ (expected 153.84€)")
            tests_passed = False
        
        if not tests_passed:
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ FAIL: Variable concepts test failed: {e}")
        all_passed = False

    db.close()
    
    print("\n" + "="*40)
    if all_passed:
        print("✅✅ AVIAPARTNER SYSTEM IS HEALTHY AND SECURE ✅✅")
    else:
        print("🛑 WARNING: SYSTEM INTEGRITY COMPROMISED. DO NOT DEPLOY.")
    print("="*40)
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    run_health_check()
