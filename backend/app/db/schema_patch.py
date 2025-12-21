import logging
from sqlalchemy import text, inspect
from app.db.database import engine

logger = logging.getLogger(__name__)

def patch_database():
    """
    Checks for missing columns in the database and adds them if necessary.
    This acts as a lightweight 'migration' system for the prototype.
    """
    try:
        inspector = inspect(engine)
        
        # 1. Check 'salary_concept_definitions' for 'level_values'
        if inspector.has_table("salary_concept_definitions"):
            columns = [c["name"] for c in inspector.get_columns("salary_concept_definitions")]
            if "level_values" not in columns:
                logger.warning("Patching DB: Adding 'level_values' to 'salary_concept_definitions'")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE salary_concept_definitions ADD COLUMN level_values JSON;"))
                    conn.commit()
        
        # 2. Check 'salary_tables' for 'variable_type'
        if inspector.has_table("salary_tables"):
            columns = [c["name"] for c in inspector.get_columns("salary_tables")]
            if "variable_type" not in columns:
                logger.warning("Patching DB: Adding 'variable_type' to 'salary_tables'")
                with engine.connect() as conn:
                    # Variable type matches the models.py definition (String)
                    conn.execute(text("ALTER TABLE salary_tables ADD COLUMN variable_type VARCHAR;"))
                    conn.commit()
                    
        logger.info("Database schema patch check completed.")
        
    except Exception as e:
        logger.error(f"Error patching database schema: {e}")
