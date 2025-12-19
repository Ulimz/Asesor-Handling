import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def promote(email):
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print(f"🔍 Promoting {email} to Superuser...")
        result = conn.execute(text("UPDATE users SET is_superuser = TRUE WHERE email = :email"), {"email": email})
        conn.commit()
        if result.rowcount > 0:
            print(f"✅ User {email} is now a SUPERUSER.")
        else:
            print(f"⚠️ User {email} not found.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_admin_cloud.py <email>")
        exit(1)
    promote(sys.argv[1])
