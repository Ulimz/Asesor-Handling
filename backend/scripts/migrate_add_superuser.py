import os
from sqlalchemy import create_engine, text

# Force backend/modules path if needed, but here we just need raw SQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("🔌 Connected to DB. Adding 'is_superuser' column...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;"))
            conn.commit()
            print("✅ Column 'is_superuser' added successfully.")
        except Exception as e:
            if "already exists" in str(e):
                print("⚠️ Column 'is_superuser' already exists.")
            else:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate()
