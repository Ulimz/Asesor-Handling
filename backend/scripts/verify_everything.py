#!/usr/bin/env python3
"""
Verify EVERYTHING in production
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.models import SalaryConceptDefinition, SalaryTable

# Production DB
db_url = "postgresql://postgres:mZRhruQHnIHV1CZk9j-~KHY4owdqkrBE@interchange.proxy.rlwy.net:29083/railway"

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 70)
print("PRODUCTION DATABASE VERIFICATION")
print("=" * 70)

# 1. Check Hora Perentoria
print("\n1. HORA PERENTORIA:")
perent = db.query(SalaryConceptDefinition).filter(
    SalaryConceptDefinition.company_slug == "easyjet",
    SalaryConceptDefinition.code == "PLUS_HORA_PERENTORIA"
).first()

if perent and perent.level_values:
    agente_nivel3 = perent.level_values.get("Agente de Rampa", {}).get("Nivel 3")
    print(f"   ✅ Exists with level_values")
    print(f"   Price for Agente Rampa Nivel 3: {agente_nivel3}€/hora")
else:
    print(f"   ❌ NOT FOUND or missing level_values")

# 2. Check Plus Progresión
print("\n2. PLUS PROGRESIÓN:")
prog = db.query(SalaryTable).filter(
    SalaryTable.company_id == "easyjet",
    SalaryTable.concept == "PLUS_PROGRESION",
    SalaryTable.level == "Agente de Rampa - Nivel 3"
).first()

if prog:
    print(f"   ✅ Exists in SalaryTable")
    print(f"   Amount: {prog.amount}€ (annual)")
    print(f"   Monthly: {prog.amount / 14:.2f}€")
else:
    print(f"   ❌ NOT FOUND in SalaryTable")

# 3. Count all EasyJet data
print("\n3. EASYJET DATA COUNT:")
concepts = db.query(SalaryConceptDefinition).filter(
    SalaryConceptDefinition.company_slug == "easyjet"
).count()
tables = db.query(SalaryTable).filter(
    SalaryTable.company_id == "easyjet"
).count()

print(f"   Concepts: {concepts}")
print(f"   Salary Tables: {tables}")

print("\n" + "=" * 70)
print("If you see ✅ for both items above, the DATABASE is correct.")
print("The problem is in the BACKEND CODE not being updated in Railway.")
print("=" * 70)

db.close()
