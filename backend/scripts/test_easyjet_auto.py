#!/usr/bin/env python3
"""
Test EasyJet automatic concept assignment
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

def test_easyjet_auto_concepts():
    print("🧪 Testing EasyJet Automatic Concept Assignment\n")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    service = CalculatorService(db)
    
    # Test 1: Jefe de Área Tipo A - Nivel 3 (should have Plus Función + Plus Progresión)
    print("📊 Test 1: Jefe de Área Tipo A - Nivel 3 (100% jornada)")
    req = CalculationRequest(
        company_slug="easyjet",
        user_level="Jefe de Área Tipo A",  # Category
        user_group="Nivel 3",  # Level within category
        gross_annual_salary=0,
        payments=14,
        contract_percentage=100,
        dynamic_variables={}
    )
    
    res = service.calculate_smart_salary(req)
    
    print(f"\n   Salario Total: {res.gross_monthly_total:.2f}€")
    print(f"\n   Breakdown:")
    for item in res.breakdown:
        print(f"   - {item.name}: {item.amount:.2f}€")
    
    # Expected:
    # - Base: 29456 / 14 = 2104€
    # - Plus Función: 6287.76 / 12 = 523.98€
    # - Plus Progresión: 994.42 / 14 = 71.03€
    
    print("\n" + "="*50)
    
    # Test 2: Agente de Rampa - Nivel 3 (75% jornada, should have Ad Personam + Plus Progresión)
    print("\n📊 Test 2: Agente de Rampa - Nivel 3 (75% jornada)")
    req = CalculationRequest(
        company_slug="easyjet",
        user_level="Agente de Rampa",  # Category
        user_group="Nivel 3",  # Level
        gross_annual_salary=0,
        payments=14,
        contract_percentage=75,
        dynamic_variables={}
    )
    
    res = service.calculate_smart_salary(req)
    
    print(f"\n   Salario Total: {res.gross_monthly_total:.2f}€")
    print(f"\n   Breakdown:")
    for item in res.breakdown:
        print(f"   - {item.name}: {item.amount:.2f}€")
    
    # Expected:
    # - Base (75%): 21532 / 14 * 0.75 = 1153.50€
    # - Ad Personam (75%): 421.54 / 14 * 0.75 = 22.58€
    # - Plus Progresión (75%): 994.42 / 14 * 0.75 = 53.27€
    
    db.close()
    print("\n✅ Tests complete")

if __name__ == "__main__":
    test_easyjet_auto_concepts()
