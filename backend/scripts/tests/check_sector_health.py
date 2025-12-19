
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.services.calculator_service import CalculatorService
from app.services.rag_engine import RagEngine
from app.schemas.salary import CalculationRequest

def run_health_check():
    print("🛡️  INITIATING SECTOR AGREEMENT SHIELD PROTOCOL (Health Check)...")
    
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
    print("\n🧪 [1/3] Testing Calculator (Base Salary for Sector)...")
    try:
        # Create a request for Sector agreement
        req = CalculationRequest(
            company_slug="convenio-sector",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0, # Use table
            payments=14,
            dynamic_variables={}
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        # Expected: Administrativos Nivel entrada = 18632.39 (from JSON)
        expected_annual = 18632.39
        expected_monthly = expected_annual / 14
        
        if abs(res.gross_monthly_total - expected_monthly) < 1.0:
            print(f"   ✅ PASS: Base salary correctly calculated as {res.gross_monthly_total:.2f}€/month")
        else:
            print(f"   ❌ FAIL: Expected {expected_monthly:.2f}€, got {res.gross_monthly_total:.2f}€")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    # --- TEST 2: CALCULATOR (Variable Concepts) ---
    print("\n🧪 [2/3] Testing Calculator (Plus Nocturnidad)...")
    try:
        req = CalculationRequest(
            company_slug="convenio-sector",
            user_group="Administrativos",
            user_level="Nivel entrada",
            gross_annual_salary=0,
            payments=14,
            dynamic_variables={
                "PLUS_NOCTURNIDAD": 10.0 # 10 hours
            }
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        # Expected: 10 hours * 1.61€ (from JSON base_value_2025)
        expected_noct = 10.0 * 1.61
        
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

    # --- TEST 3: RAG (Vector Search) ---
    print("\n🧪 [3/3] Testing RAG Brain (Search 'Plus Nocturnidad')...")
    try:
        rag = RagEngine()
        query = "plus nocturnidad artículo 28"
        results = rag.search(query, company_slug="general", db=db, limit=5)
        
        found_target = False
        for r in results:
            content = r.get("content", "")
            ref = r.get("article_ref", "")
            
            # Check for key phrase
            if "nocturnidad" in content.lower() and ("artículo 28" in content.lower() or "28.1" in content):
                found_target = True
                print(f"   ✅ PASS: Found 'Nocturnidad' in {ref}")
                break
        
        if not found_target:
            print("   ❌ FAIL: 'Nocturnidad' article NOT found in top 5 results.")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    db.close()
    
    print("\n" + "="*40)
    if all_passed:
        print("✅✅ SECTOR AGREEMENT SYSTEM IS HEALTHY AND SECURE ✅✅")
    else:
        print("🛑 WARNING: SYSTEM INTEGRITY COMPROMISED. DO NOT DEPLOY.")
    print("="*40)

if __name__ == "__main__":
    run_health_check()
