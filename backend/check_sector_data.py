
import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def check_sector():
    with engine.connect() as conn:
        print("--- CONVENIO SECTOR ---")
        res = conn.execute(text("""
            SELECT "group", level, concept, amount 
            FROM salary_tables 
            WHERE company_id = 'convenio-sector'
            AND concept IN ('HORA_EXTRA', 'HORA_PERENTORIA')
            ORDER BY "group", level, concept
        """))
        for r in res.fetchall():
            print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")

if __name__ == "__main__":
    check_sector()
