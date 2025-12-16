import os
import sys
from sqlalchemy import create_engine, text

def check_companies():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL missing")
        return

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DISTINCT company_id FROM salary_tables ORDER BY company_id"))
        companies = [row[0] for row in result]
        print(f"FOUND COMPANIES ({len(companies)}):")
        for c in companies:
            print(f"- {c}")

if __name__ == "__main__":
    check_companies()
