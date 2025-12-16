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
        companies_to_sync = [
            "iberia", "groundforce", "menzies", "swissport", 
            "aviapartner", "wfs", "easyjet", "azul-handling", "convenio-sector",
            "jet2", "norwegian", "south"
        ]
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

        # AVIAPARTNER
        aviapartner_path = base_path / "aviapartner.xml"
        if aviapartner_path.exists():
            logger.info("Extracting Aviapartner...")
            try:
                data = extract_boe_salaries(aviapartner_path, "aviapartner")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Aviapartner: {e}")

        # WFS
        wfs_path = base_path / "wfs.xml"
        if wfs_path.exists():
            logger.info("Extracting WFS...")
            try:
                data = extract_boe_salaries(wfs_path, "wfs")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract WFS: {e}")

        # EASYJET
        easyjet_path = base_path / "easyjet.xml"
        if easyjet_path.exists():
            logger.info("Extracting EasyJet...")
            try:
                data = extract_boe_salaries(easyjet_path, "easyjet")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract EasyJet: {e}")

        # AZUL HANDLING
        azul_path = base_path / "azul.xml"
        if azul_path.exists():
            logger.info("Extracting Azul Handling...")
            try:
                data = extract_boe_salaries(azul_path, "azul-handling")
                all_data.extend(data)
            except Exception as e:
                logger.error(f"Failed to extract Azul: {e}")

        # CONVENIO SECTOR (GENERAL) & EMPRESAS ADHERIDAS
        # Jet2, Norwegian, South, etc. usan el convenio sectorial.
        # Creamos una entrada para cada una con los mismos datos.
        sector_path = base_path / "general.xml"
        if sector_path.exists():
            logger.info("Extracting Sector Handling (General)...")
            try:
                sector_data = extract_boe_salaries(sector_path, "convenio-sector")
                
                # 1. Insertar el genérico
                all_data.extend(sector_data)
                
                # 2. Replicar para empresas adheridas
                sector_companies = ["jet2", "norwegian", "south"]
                for company_alias in sector_companies:
                    logger.info(f"Mapping Sector Data to: {company_alias}")
                    # Copiamos los datos cambiando solo el company_id
                    for row in sector_data:
                        # Usamos dict() para crear una copia limpia del diccionario
                        new_row = row.copy() 
                        new_row["company_id"] = company_alias
                        all_data.append(new_row)
                        
            except Exception as e:
                logger.error(f"Failed to extract Sector: {e}")

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
