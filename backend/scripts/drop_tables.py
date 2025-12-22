import sys
import os
from sqlalchemy import text

# Set up path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.database import engine

def drop_tables():
    print("🔥 Dropping Legal Tables...")
    try:
        with engine.connect() as conn:
            # Order matters: chunks depend on documents
            conn.execute(text("DROP TABLE IF EXISTS document_chunks CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS legal_documents CASCADE"))
            conn.commit()
        print("✅ Tables dropped.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

if __name__ == "__main__":
    drop_tables()
