import os
import logging
from sqlalchemy import create_engine, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_salary")

DATABASE_URL = os.getenv("DATABASE_URL")

def check_easyjet_salary():
    if not DATABASE_URL:
        logger.error("❌ DATABASE_URL environment variable is missing.")
        return

    logger.info(f"🔌 Connecting to DB...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            logger.info("🔍 Checking SALARIO_BASE for EasyJet...")
            # Fetch a few distinct examples to see values
            result = conn.execute(text("SELECT level, amount FROM salary_tables WHERE company_id = 'easyjet' AND concept = 'SALARIO_BASE'"))
            rows = result.fetchall()
            if not rows:
                logger.warning("⚠️ No SALARIO_BASE records found for EasyJet!")
            else:
                for row in rows:
                    logger.info(f"✅ Level: {row[0]} | Amount: {row[1]}")
            
    except Exception as e:
        logger.error(f"💥 Query failed: {e}")

if __name__ == "__main__":
    check_easyjet_salary()
