#!/usr/bin/env python3
"""
Test Tabla 2 pluses (checkbox proportional)
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

def test_tabla2_pluses():
    print("🧪 Testing Tabla 2 Pluses (Checkbox Proportional)\n")
    
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
    
    # Test with 75% jornada - Plus Coordinador should be proportional
    req = CalculationRequest(
        company_slug="easyjet",
        user_level="Agente de Rampa",
        user_group="Nivel 3",
        gross_annual_salary=0,
        payments=14,
        contract_percentage=75,  # 75% jornada
        dynamic_variables={
            "PLUS_FUNCION_COORD_HEADSET": 1  # Checkbox activated
        }
    )
    
    print(f"Request params:")
    print(f"  Jornada: {req.contract_percentage}%")
    print(f"  Plus Coordinador: ACTIVADO\n")
    
    res = service.calculate_smart_salary(req)
    
    print(f"📊 Results:")
    print(f"   Total: {res.gross_monthly_total:.2f}€\n")
    print(f"   Breakdown:")
    for item in res.breakdown:
        print(f"   - {item.name}: {item.amount:.2f}€")
    
    # Verify Plus Coordinador
    plus_coord = next((item for item in res.breakdown if "Coordinador" in item.name), None)
    
    print(f"\n🔍 Verification:")
    if plus_coord:
        expected = 128.15 * 0.75  # Should be proportional
        print(f"   Plus Coordinador: {plus_coord.amount:.2f}€")
        print(f"   Expected (128.15 × 75%): {expected:.2f}€")
        if abs(plus_coord.amount - expected) < 0.01:
            print(f"   ✅ CORRECTO - Es proporcional!")
        else:
            print(f"   ❌ ERROR - NO es proporcional!")
    else:
        print(f"   ❌ Plus Coordinador NOT found!")
    
    db.close()

if __name__ == "__main__":
    test_tabla2_pluses()
