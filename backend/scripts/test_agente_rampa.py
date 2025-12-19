#!/usr/bin/env python3
"""
Test EasyJet Agente de Rampa - Nivel 3
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

def test_agente_rampa():
    print("🧪 Testing: Agente de Rampa - Nivel 3\n")
    
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
    
    req = CalculationRequest(
        company_slug="easyjet",
        user_level="Agente de Rampa",  # Category
        user_group="Nivel 3",  # Level
        gross_annual_salary=0,
        payments=14,
        contract_percentage=100,
        dynamic_variables={
            "PLUS_HORA_PERENTORIA": 10  # 10 horas perentorias
        }
    )
    
    print(f"Request params:")
    print(f"  company_slug: {req.company_slug}")
    print(f"  user_level (category): {req.user_level}")
    print(f"  user_group (level): {req.user_group}")
    print(f"  dynamic_variables: {req.dynamic_variables}\n")
    
    res = service.calculate_smart_salary(req)
    
    print(f"\n📊 Results:")
    print(f"   Total: {res.gross_monthly_total:.2f}€\n")
    print(f"   Breakdown:")
    for item in res.breakdown:
        print(f"   - {item.name}: {item.amount:.2f}€")
    
    # Check specific concepts
    plus_prog = next((item for item in res.breakdown if "Progresión" in item.name), None)
    hora_perent = next((item for item in res.breakdown if "Perentoria" in item.name), None)
    
    print(f"\n🔍 Verification:")
    if plus_prog:
        print(f"   ✅ Plus Progresión found: {plus_prog.amount:.2f}€")
    else:
        print(f"   ❌ Plus Progresión NOT found!")
        
    if hora_perent:
        print(f"   ✅ Hora Perentoria found: {hora_perent.amount:.2f}€")
    else:
        print(f"   ❌ Hora Perentoria NOT found!")
    
    db.close()

if __name__ == "__main__":
    test_agente_rampa()
