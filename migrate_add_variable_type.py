import os
import logging
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate_variable_type():
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL environment variable is missing.")
        return

    logger.info(f"🔌 Connecting to DB...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            logger.info("🛠️ Adding 'variable_type' column to 'salary_tables'...")
            conn.execute(text("ALTER TABLE salary_tables ADD COLUMN IF NOT EXISTS variable_type VARCHAR"))
            conn.commit()
            logger.info("✅ Column 'variable_type' added (or already existed).")
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")

if __name__ == "__main__":
    migrate_variable_type()
