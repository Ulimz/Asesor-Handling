#!/usr/bin/env python3
"""
Simple test for EasyJet Jefe de Área - Plus Función
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

def test_jefe_area():
    print("🧪 Testing: Jefe de Área Tipo A - Nivel 3\n")
    
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
        user_level="Jefe de Área Tipo A",  # Category
        user_group="Nivel 3",  # Level
        gross_annual_salary=0,
        payments=14,
        contract_percentage=100,
        dynamic_variables={}
    )
    
    print(f"Request params:")
    print(f"  company_slug: {req.company_slug}")
    print(f"  user_level (category): {req.user_level}")
    print(f"  user_group (level): {req.user_group}\n")
    
    res = service.calculate_smart_salary(req)
    
    print(f"\n📊 Results:")
    print(f"   Total: {res.gross_monthly_total:.2f}€\n")
    print(f"   Breakdown:")
    for item in res.breakdown:
        print(f"   - {item.name}: {item.amount:.2f}€")
    
    # Check if Plus Función was assigned
    plus_funcion = next((item for item in res.breakdown if "Plus Función" in item.name), None)
    if plus_funcion:
        print(f"\n✅ Plus Función found: {plus_funcion.amount:.2f}€")
    else:
        print(f"\n❌ Plus Función NOT found!")
    
    db.close()

if __name__ == "__main__":
    test_jefe_area()
