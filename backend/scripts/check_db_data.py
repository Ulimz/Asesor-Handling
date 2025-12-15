
import sys
import asyncio
from pathlib import Path
from sqlalchemy import select, text

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal
from app.db.models import SalaryTable

async def check_data():
    db = SessionLocal()
    try:
        # Use sync query here because SessionLocal yields a sync session, unless we are using AsyncSession
        # But wait, db.models might be async? 
        # Check database.py again... it used 'sqlalchemy.create_engine', so it's SYNC.
        # So I don't need async/await for the DB calls themselves if using sync engine.
        
        result = db.execute(select(SalaryTable.company_id).distinct())
        companies = result.all()
        # companies is list of tuples like [('iberia',)]
        print(f"Companies in DB (ID): {companies}")
        
        if companies:
            first_company_id = companies[0][0]
            if first_company_id:
                result_groups = db.execute(select(SalaryTable.group).where(SalaryTable.company_id == first_company_id).distinct())
                groups = result_groups.scalars().all()
                print(f"Groups for {first_company_id}: {groups}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(check_data())
