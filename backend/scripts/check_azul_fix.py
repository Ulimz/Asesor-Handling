
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("No DATABASE_URL set.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Checking PLUS_AD_PERSONAM for azul-handling...")
    res = conn.execute(text("SELECT code, default_price FROM salary_concept_definitions WHERE company_slug='azul-handling' AND code='PLUS_AD_PERSONAM'")).fetchall()
    print(res)

    print("\nChecking TURNICIDAD codes...")
    res2 = conn.execute(text("SELECT code, default_price FROM salary_concept_definitions WHERE company_slug='azul-handling' AND code LIKE 'PLUS_TURNICIDAD%'")).fetchall()
    print(res2)

    print("\nChecking SalaryTable pollution...")
    res3 = conn.execute(text("SELECT * FROM salary_tables WHERE company_id='azul-handling' AND concept='PLUS_AD_PERSONAM' LIMIT 5")).fetchall()
    print(res3)
