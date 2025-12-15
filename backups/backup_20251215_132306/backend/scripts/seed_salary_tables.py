import sys
import os
import logging
from pathlib import Path

# Add backend to sys.path to allow imports from app
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal
from app.db.models import SalaryTable, SalaryConceptDefinition
from scripts.extract_salary_tables import extract_iberia_salaries, extract_groundforce_salaries, extract_boe_salaries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_salaries():
    db = SessionLocal()
    try:
        logger.info("Starting Salary Table Seeding...")

        # 1. Clear existing SalaryTable data for target companies
        # We perform a clean sync for these companies to avoid duplicates
        companies_to_sync = ["iberia", "groundforce", "menzies", "swissport"]
        deleted_rows = db.query(SalaryTable).filter(SalaryTable.company_id.in_(companies_to_sync)).delete(synchronize_session=False)
        logger.info(f"Cleared {deleted_rows} existing records for {companies_to_sync}")

        base_path = Path(__file__).resolve().parent.parent / "data" / "xml"
        all_data = []

        # 2. Extract Data
        
        # IBERIA
        iberia_path = base_path / "iberia.xml"
        if iberia_path.exists():
            logger.info("Extracting Iberia...")
            try:
                data = extract_iberia_salaries(iberia_path)
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Iberia: {e}")
        
        # GROUNDFORCE
        gf_path = base_path / "groundforce.xml"
        if gf_path.exists():
            logger.info("Extracting Groundforce...")
            try:
                data = extract_groundforce_salaries(gf_path)
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Groundforce: {e}")

        # MENZIES
        menzies_path = base_path / "menzies.xml"
        if menzies_path.exists():
            logger.info("Extracting Menzies...")
            try:
                data = extract_boe_salaries(menzies_path, "menzies")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Menzies: {e}")

        # SWISSPORT
        swiss_path = base_path / "swissport.xml"
        if swiss_path.exists():
            logger.info("Extracting Swissport...")
            try:
                data = extract_boe_salaries(swiss_path, "swissport")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Swissport: {e}")

        # 3. Insert Extracted Salary Data
        if all_data:
            logger.info(f"Inserting {len(all_data)} extracted records into SalaryTable...")
            db_objects = [SalaryTable(**row) for row in all_data]
            db.bulk_save_objects(db_objects)
        else:
            logger.warning("No data extracted!")

        # 4. Seed Essential Concepts (Metadata)
        # Creating GARANTIA_PERSONAL as a manual input concept
        
        special_concepts = [
            {
                "company_slug": "global", # Applies to all
                "name": "Garantía Personal (Ad Personam)",
                "code": "GARANTIA_PERSONAL",
                "description": "Complemento personal consolidado y no absorbible.",
                "input_type": "currency", # manual entry in Euros
                "default_price": 0.0,
                "is_active": True
            },
            # We can add others here if needed
        ]

        for concept_data in special_concepts:
            # Check if exists
            exists = db.query(SalaryConceptDefinition).filter_by(code=concept_data["code"]).first()
            if not exists:
                logger.info(f"Creating concept: {concept_data['code']}")
                new_concept = SalaryConceptDefinition(**concept_data)
                db.add(new_concept)
            else:
                logger.info(f"Concept {concept_data['code']} already exists.")

        db.commit()
        logger.info("Seeding process completed successfully.")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_salaries()
