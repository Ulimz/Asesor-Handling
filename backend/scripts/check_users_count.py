import os
from sqlalchemy import create_engine, text

# Get Database URL from env or use default (WARNING: This will fail if env is not set correctly for cloud)
# I will rely on the user having the env set or I can use the one I saw in other scripts if needed, 
# but for now let's assume the environment where I run this has access or I will use the hardcoded string if provided before.
# Since I am in agentic mode and running locally, I need the connection string.
# I will use the one found in seed_production.py reference or similar if available, 
# but best practice is to read from os.environ.
# Assuming local setup has access to prod via env var or I print a message if not found.

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found. Cannot connect to Cloud DB.")
    exit(1)

# Fix for postgres protocol
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def count_users():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM users;"))
            count = result.scalar()
            print(f"👥 Total Usuarios Registrados: {count}")
            
            # Optional: Show recent users
            result_recent = connection.execute(text("SELECT email, created_at FROM users ORDER BY created_at DESC LIMIT 5;"))
            print("\n🆕 Últimos 5 usuarios:")
            for row in result_recent:
                print(f" - {row[0]}")

    except Exception as e:
        print(f"💥 Error connecting to DB: {e}")

if __name__ == "__main__":
    count_users()
