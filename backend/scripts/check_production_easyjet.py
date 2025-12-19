#!/usr/bin/env python3
"""
Test production database to verify EasyJet data
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryConceptDefinition, SalaryTable

def check_production():
    # Railway production DB
    db_url = "postgresql://postgres:mZRhruQHnIHV1CZk9j-~KHY4owdqkrBE@interchange.proxy.rlwy.net:29083/railway"
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("🔍 Checking EasyJet data in PRODUCTION\n")
    
    # 1. Check Hora Perentoria concept
    perentoria = db.query(SalaryConceptDefinition).filter(
        SalaryConceptDefinition.company_slug == "easyjet",
        SalaryConceptDefinition.code == "PLUS_HORA_PERENTORIA"
    ).first()
    
    if perentoria:
        print("✅ PLUS_HORA_PERENTORIA found:")
        print(f"   Input Type: {perentoria.input_type}")
        print(f"   Default Price: {perentoria.default_price}")
        print(f"   Level Values: {perentoria.level_values}\n")
    else:
        print("❌ PLUS_HORA_PERENTORIA NOT FOUND!\n")
    
    # 2. Check Plus Progresión in salary tables
    prog_tables = db.query(SalaryTable).filter(
        SalaryTable.company_id == "easyjet",
        SalaryTable.concept == "PLUS_PROGRESION",
        SalaryTable.level.like("%Agente de Rampa - Nivel 3%")
    ).all()
    
    print(f"📊 Plus Progresión tables for Agente Rampa Nivel 3:")
    if prog_tables:
        for table in prog_tables:
            print(f"   Group: {table.group}")
            print(f"   Level: {table.level}")
            print(f"   Amount: {table.amount}")
    else:
        print("   ❌ NOT FOUND!")
    
    # 3. Check all EasyJet concepts
    all_concepts = db.query(SalaryConceptDefinition).filter(
        SalaryConceptDefinition.company_slug == "easyjet"
    ).all()
    
    print(f"\n📋 Total EasyJet concepts: {len(all_concepts)}")
    for concept in all_concepts:
        print(f"   - {concept.code}: {concept.name}")
    
    db.close()

if __name__ == "__main__":
    check_production()
