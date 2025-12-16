
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def check_prices():
    print("Checking SalaryTable for AZUL HANDLING (2025)...")
    try:
        # 1. Count Records
        azul_count = session.execute(text("SELECT count(*) FROM salary_tables WHERE company_id = 'azul-handling' AND year = 2025")).scalar()
        print(f"Total Azul Records (2025): {azul_count}")

        # 2. Check Specific Concepts
        concepts_to_check = [
            'PLUS_RCO', 'PLUS_ARCO', 'PLUS_DIFERENTE_PUESTO', 
            'HORA_COMPLEMENTARIA_ESP', 'PLUS_FRACCIONADA_T1'
        ]
        
        print("\n--- SAMPLE VALUES ---")
        for c in concepts_to_check:
            res = session.execute(text(f"SELECT amount, 'group' FROM salary_tables WHERE company_id = 'azul-handling' AND concept = '{c}' AND year = 2025 LIMIT 1")).fetchone()
            if res:
                print(f"{c}: {res[0]}€")
            else:
                print(f"{c}: NOT FOUND ❌")

        # 3. Check Base Salary Sample
        print("\n--- BASE SALARY (Technician L3) ---")
        res_base = session.execute(text("SELECT amount FROM salary_tables WHERE company_id = 'azul-handling' AND concept = 'SALARIO_BASE' AND level = 'Nivel 3' AND \"group\" = 'Técnicos Gestores' AND year = 2025")).fetchone()
        if res_base:
            print(f"Base Salary: {res_base[0]}€")
        else:
            print("Base Salary: NOT FOUND ❌")
            
        print("\n--- Hours Sample (Extra - Admin L4) ---")
        res_hour = session.execute(text("SELECT amount FROM salary_tables WHERE company_id = 'azul-handling' AND concept = 'HORA_EXTRA' AND level = 'Nivel 4' AND \"group\" = 'Administrativos' AND year = 2025")).fetchone()
        if res_hour:
             print(f"Hora Extra: {res_hour[0]}€")
        else:
             print("Hora Extra: NOT FOUND ❌ (Check Extraction)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_prices()
