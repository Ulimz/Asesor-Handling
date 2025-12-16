import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal

def verify_easyjet():
    db = SessionLocal()
    try:
        print("--- Verifying EasyJet Data ---")
        
        # 1. Check distinct Groups
        result = db.execute(text("SELECT DISTINCT \"group\" FROM salary_tables WHERE company_id = 'easyjet' ORDER BY \"group\""))
        groups = [row[0] for row in result]
        print(f"\nDistinc Groups ({len(groups)}):")
        for g in groups:
            print(f" - {g}")
            
        # 2. Check distinct Levels for a specific group
        if groups:
            target_group = groups[0] 
            # Pick one that is likely a real group, e.g. "Administrativos" or "Servicios Auxiliares"
            for g in groups:
                if "Auxiliares" in g: target_group = g; break
            
            print(f"\nLevels in Group '{target_group}':")
            result_levels = db.execute(text(f"SELECT DISTINCT \"level\" FROM salary_tables WHERE company_id = 'easyjet' AND \"group\" = '{target_group}' ORDER BY \"level\""))
            levels = [row[0] for row in result_levels]
            for l in levels:
                print(f" - {l}")

            # 3. Sample salary entry
            print(f"\nSample Salary Entry for '{target_group}' / '{levels[0] if levels else 'Any'}':")
            sample = db.execute(text(f"SELECT concept, amount FROM salary_tables WHERE company_id = 'easyjet' AND \"group\" = '{target_group}' AND \"level\" = '{levels[0]}' LIMIT 5"))
            for row in sample:
                print(f" - {row[0]}: {row[1]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_easyjet()
