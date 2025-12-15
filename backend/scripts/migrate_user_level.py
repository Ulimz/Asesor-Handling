import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add backend to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import engine

def migrate():
    print("Migrating salary_level to VARCHAR...")
    with engine.connect() as conn:
        # Check if column exists and type (optional but good)
        # Just brute force alter
        try:
            conn.execute(text("ALTER TABLE users ALTER COLUMN salary_level TYPE VARCHAR;"))
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
