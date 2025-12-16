
import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add backend directory to path like seed_salary_tables.py
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal

def verify_company_structure(company_id: str):
    session = SessionLocal()
    try:
        print(f"\n--- Verifying Structure for Company: {company_id} ---")
        
        # 1. Check distinct Groups
        result = session.execute(text(
            "SELECT DISTINCT \"group\" FROM salary_tables WHERE company_id = :company_id ORDER BY \"group\""
        ), {"company_id": company_id})
        groups = [row[0] for row in result.fetchall()]
        print(f"DTO Groups Found ({len(groups)}):")
        for g in groups:
            print(f"  - {g}")
            
        # 2. Check distinct Levels (sample top 10)
        result = session.execute(text(
            "SELECT DISTINCT \"level\" FROM salary_tables WHERE company_id = :company_id ORDER BY \"level\" LIMIT 10"
        ), {"company_id": company_id})
        levels = [row[0] for row in result.fetchall()]
        print(f"\nSample Levels Found (First 10 of many):")
        for l in levels:
            print(f"  - {l}")
            
        # 3. Check Count
        result = session.execute(text(
            "SELECT COUNT(*) FROM salary_tables WHERE company_id = :company_id"
        ), {"company_id": company_id})
        count = result.scalar()
        print(f"\nTotal Records: {count}")

        if len(groups) <= 1 and (len(groups) == 0 or groups[0] == "General"):
            print("\n❌ WARNING: Only 'General' group found (or none). This indicates the extraction issue is present.")
        elif len(groups) > 1:
             print("\n✅ SUCCESS: Multiple groups detected.")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_structure.py <company_id>")
        sys.exit(1)
    
    company = sys.argv[1]
    verify_company_structure(company)
