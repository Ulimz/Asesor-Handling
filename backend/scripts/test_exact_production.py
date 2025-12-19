#!/usr/bin/env python3
"""
Simulate exact production scenario
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

def test_production_scenario():
    # Use PRODUCTION database
    db_url = "postgresql://postgres:mZRhruQHnIHV1CZk9j-~KHY4owdqkrBE@interchange.proxy.rlwy.net:29083/railway"
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    service = CalculatorService(db)
    
    print("🧪 Simulating EXACT production scenario")
    print("=" * 60)
    print("Company: EasyJet")
    print("Category: Agente de Rampa")
    print("Level: Nivel 3")
    print("Horas Perentorias: 10")
    print("=" * 60)
    print()
    
    req = CalculationRequest(
        company_slug="easyjet",
        user_level="Agente de Rampa",
        user_group="Nivel 3",
        gross_annual_salary=0,
        payments=14,
        contract_percentage=100,
        dynamic_variables={
            "PLUS_HORA_PERENTORIA": 10
        }
    )
    
    result = service.calculate_smart_salary(req)
    
    print(f"\n📊 RESULTS:")
    print(f"Total: {result.gross_monthly_total:.2f}€\n")
    
    print("Breakdown:")
    for item in result.breakdown:
        if item.amount != 0:
            print(f"  {item.name}: {item.amount:.2f}€")
    
    # Check specific items
    print(f"\n🔍 VERIFICATION:")
    plus_prog = next((item for item in result.breakdown if "Progresión" in item.name), None)
    hora_perent = next((item for item in result.breakdown if "Perentoria" in item.name), None)
    
    if plus_prog:
        print(f"  ✅ Plus Progresión: {plus_prog.amount:.2f}€")
    else:
        print(f"  ❌ Plus Progresión: NOT FOUND")
        
    if hora_perent:
        print(f"  ✅ Hora Perentoria: {hora_perent.amount:.2f}€")
    else:
        print(f"  ❌ Hora Perentoria: NOT FOUND")
    
    db.close()

if __name__ == "__main__":
    test_production_scenario()
