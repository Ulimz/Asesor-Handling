import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- CONFIG ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/asistente_handling")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- LOGGING ---
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.ERROR) # Only errors
logger = logging.getLogger("verify_easyjet")

def verify():
    print(f"🔌 Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        print("--- 🔍 Verifying EasyJet (2025) Data ---")

        # 1. Check Groups
        res = session.execute(text("SELECT DISTINCT \"group\" FROM salary_tables WHERE company_id = 'easyjet' AND year = 2025 ORDER BY \"group\""))
        groups = [row[0] for row in res]
        print(f"✅ Groups Found ({len(groups)}): {groups}")

        # 2. Check Levels count per Group
        for g in groups:
            res = session.execute(text("SELECT COUNT(DISTINCT level) FROM salary_tables WHERE company_id='easyjet' AND \"group\"=:g AND year=2025"), {"g": g})
            count = res.scalar()
            print(f"   🔹 Group '{g}' has {count} distinct levels.")

        # 3. Sample Check: "Jefe de Área Tipo A - Nivel 7"
        sample_level = "Jefe de Área Tipo A - Nivel 7"
        res = session.execute(text("SELECT concept, amount FROM salary_tables WHERE company_id='easyjet' AND level=:l AND year=2025 ORDER BY concept"), {"l": sample_level})
        rows = res.fetchall()
        print(f"\n🔍 Sample Check for '{sample_level}':")
        for row in rows:
            print(f"   - {row[0]}: {row[1]}")

        # 4. Sample Check: "Auxiliar de Rampa" (Check Transport/Extra Override)
        sample_level_2 = "Auxiliar de Rampa"
        res = session.execute(text("SELECT concept, amount FROM salary_tables WHERE company_id='easyjet' AND level=:l AND year=2025 ORDER BY concept"), {"l": sample_level_2})
        rows_2 = res.fetchall()
        print(f"\n🔍 Sample Check for '{sample_level_2}':")
        for row in rows_2:
            print(f"   - {row[0]}: {row[1]}")
            
        # 5. Check Perentoria variance
        print("\n🔍 Verifying Perentoria Prices (Sample):")
        levels_to_check = ["Jefe de Área Tipo A - Nivel 1", "Jefe de Área Tipo A - Nivel 7", "Agente Administrativo - Nivel 1"]
        for lvl in levels_to_check:
             res = session.execute(text("SELECT amount FROM salary_tables WHERE company_id='easyjet' AND level=:l AND concept='PLUS_HORA_PERENTORIA' AND year=2025"), {"l": lvl})
             val = res.scalar()
             print(f"   - {lvl}: {val} (Expected variation)")

    except Exception as e:
        logger.error(f"💥 Error verification: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify()
