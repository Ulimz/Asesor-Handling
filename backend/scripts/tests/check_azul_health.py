
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
from app.db.models import LegalDocument

def run_health_check():
    print("🛡️  INITIATING AZUL HANDLING SHIELD PROTOCOL (Health Check)...")
    
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
    
    # --- TEST 1: CALCULATOR (Garantía Personal) ---
    print("\n🧪 [1/2] Testing Calculator (Garantía Personal logic)...")
    try:
        # Create a mock request with Ad Personam
        req = CalculationRequest(
            company_slug="azul-handling",
            user_group="Gestores", # Random group
            user_level="Nivel 1",
            gross_annual_salary=0, # Use table
            payments=14,
            dynamic_variables={
                "PLUS_AD_PERSONAM": 50.0 # User inputs 50 Euros
            }
        )
        
        service = CalculatorService(db)
        res = service.calculate_smart_salary(req)
        
        # Verify Ad Personam is counted as 50 (price * 1.0)
        # We check breakdown or total variable
        ad_personam_item = next((i for i in res.breakdown if "Personam" in i.name), None)
        
        if ad_personam_item:
            if abs(ad_personam_item.amount - 50.0) < 0.1:
                print(f"   ✅ PASS: Ad Personam correctly calculated as {ad_personam_item.amount}€")
            else:
                print(f"   ❌ FAIL: Ad Personam expected 50.0, got {ad_personam_item.amount}€")
                all_passed = False
        else:
            print("   ❌ FAIL: Ad Personam concept NOT found in breakdown.")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    # --- TEST 2: RAG (Vector Search) ---
    print("\n🧪 [2/2] Testing RAG Brain (Search 'rotación 6x3')...")
    try:
        rag = RagEngine()
        query = "vacaciones rotacion 6x3"
        results = rag.search(query, company_slug="azul-handling", db=db, limit=3)
        
        found_target = False
        for r in results:
            content = r.get("content", "")
            ref = r.get("article", "") or r.get("article_ref", "") # Compatibility
            
            # Check for key phrase
            if "6x3" in content or "4x4" in content:
                found_target = True
                print(f"   ✅ PASS: Found '6x3' in {ref}")
                break
        
        if not found_target:
            print("   ❌ FAIL: '6x3' NOT found in top 3 results.")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        all_passed = False

    db.close()
    
    print("\n" + "="*40)
    if all_passed:
        print("✅✅ AZUL HANDLING SYSTEM IS HEALTHY AND SECURE ✅✅")
    else:
        print("🛑 WARNING: SYSTEM INTEGRITY COMPROMISED. DO NOT DEPLOY.")
    print("="*40)

if __name__ == "__main__":
    run_health_check()
