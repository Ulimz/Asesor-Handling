
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
    print("Checking SalaryTable for Year 2025...")
    try:
        count25 = session.execute(text("SELECT count(*) FROM salary_tables WHERE year = 2025")).scalar()
        print(f"Records 2025: {count25}")

        print("\nDistinct Concepts 2025:")
        concepts = session.execute(text("SELECT DISTINCT concept FROM salary_tables WHERE year = 2025")).fetchall()
        for c in concepts:
            print(c[0])

        print("\nSearching for PERENTORIA:")
        query = text("""
            SELECT company_id, "group", level, concept, amount
            FROM salary_tables 
            WHERE concept LIKE '%PERENTORIA%' 
              AND year = 2025 
            LIMIT 5
        """)
        rows = session.execute(query).fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_prices()
