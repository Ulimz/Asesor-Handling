import sys
import os

# Set up path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.database import engine
from app.db.models import Base
from app.db import models # Register models

print("🔄 Registering models...")
print(f"📋 Registered Tables in Metadata: {Base.metadata.tables.keys()}")

try:
    print("🛠 Enabling pgvector extension...")
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("✅ Extension enabled.")

    print("🛠 Attempting create_all...")
    Base.metadata.create_all(bind=engine)
    print("✅ create_all finished.")
except Exception as e:
    print(f"❌ create_all failed: {e}")

# Forced individual creation if needed
try:
    print("🔨 Forcing creation of LegalDocument table directly...")
    models.LegalDocument.__table__.create(bind=engine, checkfirst=True)
    models.DocumentChunk.__table__.create(bind=engine, checkfirst=True)
    print("✅ Forced creation success.")
except Exception as e:
    print(f"⚠️ Forced creation failed (maybe already exists): {e}")
