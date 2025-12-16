
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# URL from seed_standalone.py
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/asistente_handling"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_jet2():
    session = SessionLocal()
    try:
        print("--- Checking Jet2 Data ---")
        # Use simple string for query to avoid sql alchemy text issues if any
        sql = text("SELECT concept, amount FROM salary_tables WHERE company_id='jet2' AND \"group\"='Servicios Auxiliares' AND level='Nivel 2'")
        results = session.execute(sql).fetchall()
        if not results:
            print("NO DATA FOUND for 'jet2' / 'Servicios Auxiliares' / 'Nivel 2'")
        else:
            for r in results:
                print(f"Concept: {r[0]}, Amount: {r[1]}")
                
        print("\n--- Checking All Jet2 Groups ---")
        sql_groups = text("SELECT DISTINCT \"group\" FROM salary_tables WHERE company_id='jet2'")
        groups = session.execute(sql_groups).fetchall()
        print(f"Groups found: {[g[0] for g in groups]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_jet2()
