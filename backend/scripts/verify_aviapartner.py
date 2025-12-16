
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_aviapartner():
    session = SessionLocal()
    try:
        print("--- Verifying Aviapartner Data ---")
        
        company_id = "aviapartner"
        company_name = "Aviapartner"
        print(f"✅ Using Company ID: {company_id}")
        
        # 2. Check Group Names for '€'
        print("\nChecking Group Names for '€' symbol...")
        groups = session.execute(text(
            "SELECT DISTINCT \"group\" FROM salary_tables WHERE company_id = :cid ORDER BY \"group\""
        ), {"cid": company_id}).fetchall()
        
        dirty_groups = [g[0] for g in groups if '€' in g[0]]
        
        if dirty_groups:
            print(f"❌ Found dirty group names: {dirty_groups}")
        else:
            print("✅ All group names are clean (no '€' found).")
            print(f"   Groups found: {[g[0] for g in groups]}")

        # 3. Check Levels (Look for Level 1)
        print("\nChecking Salary Levels...")
        levels = session.execute(text(
            "SELECT DISTINCT level FROM salary_tables WHERE company_id = :cid ORDER BY level"
        ), {"cid": company_id}).fetchall()
        
        # Convert levels to a list or set for checking
        level_values = [str(l[0]) for l in levels]
        
        if "1" in level_values or "Level 1" in level_values:
             print("✅ Level 1 found.")
        else:
             print("❌ Level 1 NOT found (checking raw values).")
        
        print(f"   Levels found: {sorted(level_values)}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_aviapartner()
