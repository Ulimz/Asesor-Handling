
import os
import sys
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- STANDALONE DATABASE SETUP ---
# Allow overriding via env var for Production Seeding
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/asistente_handling")
# Fix postgres:// legacy protocol for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SalaryTable(Base):
    __tablename__ = "salary_tables"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True)
    group = Column(String)
    level = Column(String)
    concept = Column(String)
    amount = Column(Float)
    variable_type = Column(String, nullable=True)
    year = Column(Integer, default=2024)
    # Metadata columns (if not in DB yet, script might struggle, but basic cols assume present)
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- XML EXTRACTION LOGIC (Simplified Import) ---
# We still need extract_boe_salaries. 
# We'll import it by adding backend/scripts to path explicitly.
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_scripts_path = os.path.join(current_dir, 'backend', 'scripts')
sys.path.append(backend_scripts_path)

try:
    from extract_salary_tables import extract_boe_salaries
except ImportError:
    # Fallback if path structure is weird
    logger.error("Could not import extract_salary_tables. Make sure backend/scripts is accessible.")
    def extract_boe_salaries(xml, cid): return []

def seed_from_template(template_path, companies_to_seed):
    """
    Seeds database using a Master Template JSON + Dynamic XML Data.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
    except UnicodeDecodeError:
        # Fallback for Windows-1252 if UTF-8 fails
        logger.warning("UTF-8 decode failed for template, trying latin-1")
        with open(template_path, 'r', encoding='latin-1') as f:
            template = json.load(f)
        
    session = SessionLocal()
    
    try:
        logger.info(f"Clearing old data for companies: {companies_to_seed}")
        # Note: In production we might not want to delete EVERYTHING if we are just patching, 
        # but for initial consistency we usually do.
        session.query(SalaryTable).filter(SalaryTable.company_id.in_(companies_to_seed)).delete(synchronize_session=False)
        session.commit()
        
        extracted_data = []
        if template['meta']['company_id'] == 'convenio-sector':
            xml_path = os.path.join('backend', 'data', 'xml', 'general.xml')
            if os.path.exists(xml_path):
                logger.info("Extracting dynamic values from general.xml...")
                extracted_data = extract_boe_salaries(xml_path, 'convenio-sector')
            else:
                logger.warning(f"general.xml not found at {xml_path}!")

            # --- MANUAL OVERRIDE: 2025 DATA INJECTION ---
            # User provided updated tables for 2025 (Base Annual, Extra Hour, Perentory Hour)
            # We inject them as if they were extracted from XML
            
            manual_2025 = [
                # --- BASE SALARY (Annual) ---
                # Administrativos
                {"group": "Administrativos", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18632.39, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 22065.51, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22728.97, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 23183.55, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23638.13, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24583.65, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25567.00, "year": 2025},
                # Servicios Auxiliares
                {"group": "Servicios Auxiliares", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18450.87, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 21850.75, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22507.75, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 22957.90, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23408.06, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24344.38, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25318.15, "year": 2025},
                # Técnicos Gestores
                {"group": "Técnicos Gestores", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 28460.70, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 28516.35, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 29367.68, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 29955.04, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 30542.39, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 31764.09, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 33034.65, "year": 2025},

                # --- HORA EXTRA (2025) ---
                # Admin
                {"group": "Administrativos", "level": "Nivel 1", "concept": "HORA_EXTRA", "amount": 16.33, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 2", "concept": "HORA_EXTRA", "amount": 19.33, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 3", "concept": "HORA_EXTRA", "amount": 19.91, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 4", "concept": "HORA_EXTRA", "amount": 20.31, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 5", "concept": "HORA_EXTRA", "amount": 20.71, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 6", "concept": "HORA_EXTRA", "amount": 21.54, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 7", "concept": "HORA_EXTRA", "amount": 22.40, "year": 2025},
                # Aux
                {"group": "Servicios Auxiliares", "level": "Nivel 1", "concept": "HORA_EXTRA", "amount": 16.17, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 2", "concept": "HORA_EXTRA", "amount": 19.14, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 3", "concept": "HORA_EXTRA", "amount": 19.72, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 4", "concept": "HORA_EXTRA", "amount": 20.11, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 5", "concept": "HORA_EXTRA", "amount": 20.51, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 6", "concept": "HORA_EXTRA", "amount": 21.33, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 7", "concept": "HORA_EXTRA", "amount": 22.18, "year": 2025},
                # TG
                {"group": "Técnicos Gestores", "level": "Nivel 1", "concept": "HORA_EXTRA", "amount": 24.94, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 2", "concept": "HORA_EXTRA", "amount": 24.99, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 3", "concept": "HORA_EXTRA", "amount": 25.73, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 4", "concept": "HORA_EXTRA", "amount": 26.25, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 5", "concept": "HORA_EXTRA", "amount": 26.76, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 6", "concept": "HORA_EXTRA", "amount": 27.83, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 7", "concept": "HORA_EXTRA", "amount": 28.94, "year": 2025},

                # --- HORA PERENTORIA (2025) ---
                # Admin
                {"group": "Administrativos", "level": "Nivel 1", "concept": "HORA_PERENTORIA", "amount": 19.05, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 2", "concept": "HORA_PERENTORIA", "amount": 22.56, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 3", "concept": "HORA_PERENTORIA", "amount": 23.23, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 4", "concept": "HORA_PERENTORIA", "amount": 23.70, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 5", "concept": "HORA_PERENTORIA", "amount": 24.16, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 6", "concept": "HORA_PERENTORIA", "amount": 25.13, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 7", "concept": "HORA_PERENTORIA", "amount": 26.13, "year": 2025},
                # Aux
                {"group": "Servicios Auxiliares", "level": "Nivel 1", "concept": "HORA_PERENTORIA", "amount": 18.86, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 2", "concept": "HORA_PERENTORIA", "amount": 22.34, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 3", "concept": "HORA_PERENTORIA", "amount": 23.01, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 4", "concept": "HORA_PERENTORIA", "amount": 23.47, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 5", "concept": "HORA_PERENTORIA", "amount": 23.93, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 6", "concept": "HORA_PERENTORIA", "amount": 24.88, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 7", "concept": "HORA_PERENTORIA", "amount": 25.88, "year": 2025},
                # TG
                {"group": "Técnicos Gestores", "level": "Nivel 1", "concept": "HORA_PERENTORIA", "amount": 29.09, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 2", "concept": "HORA_PERENTORIA", "amount": 29.15, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 3", "concept": "HORA_PERENTORIA", "amount": 30.02, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 4", "concept": "HORA_PERENTORIA", "amount": 30.62, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 5", "concept": "HORA_PERENTORIA", "amount": 31.22, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 6", "concept": "HORA_PERENTORIA", "amount": 32.47, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 7", "concept": "HORA_PERENTORIA", "amount": 33.77, "year": 2025},
            ]
            extracted_data.extend(manual_2025)

        def find_extracted_value(group_name, level_name, concept_key, year=2025):
            for r in extracted_data:
                if r['year'] == year and r['concept'] == concept_key:
                    if r['group'] == group_name and r['level'] == level_name:
                        return r['amount']
            return None

        records_to_insert = []
        
        for company_id in companies_to_seed:
            logger.info(f"Seeding structure for: {company_id}")
            
            for group in template['groups']:
                group_name = group['name']
                
                for level in group['levels']:
                    
                    # 3.1 Fixed Concepts
                    for concept_def in template['concepts']['fixed']:
                         if 'applicable_concepts' in group and concept_def['id'] not in group['applicable_concepts']:
                             continue
                             
                         amount = concept_def.get('base_value_2022', 0.0)
                         
                         if 'tiers' in concept_def:
                             for tier_name, tier_val in concept_def['tiers'].items():
                                 concept_id = f"{concept_def['id']}_{tier_name}"
                                 records_to_insert.append(SalaryTable(
                                     company_id=company_id,
                                     group=group_name,
                                     level=level,
                                     concept=concept_id,
                                     amount=tier_val,
                                     year=2025 
                                 ))
                         else:
                             records_to_insert.append(SalaryTable(
                                 company_id=company_id,
                                 group=group_name,
                                 level=level,
                                 concept=concept_def['id'],
                                 amount=amount,
                                 year=2025
                             ))

                    # 3.2 Variable Concepts
                    for concept_def in template['concepts']['variable']:
                         if 'applicable_concepts' in group and concept_def['id'] not in group['applicable_concepts']:
                             continue

                         val = concept_def.get('base_value_2022', 0.0)
                         
                         if concept_def.get('source') == 'xml_table':
                             dynamic_val = find_extracted_value(group_name, level, concept_def['id'], 2025)
                             if dynamic_val:
                                 val = dynamic_val
                             else:
                                 dynamic_val = find_extracted_value(group_name, level, concept_def['id'], 2024)
                                 if dynamic_val: val = dynamic_val
                        
                         records_to_insert.append(SalaryTable(
                             company_id=company_id,
                             group=group_name,
                             level=level,
                             concept=concept_def['id'],
                             amount=val,
                             year=2025
                         ))
            
            # 3.3 Explicitly Inject Extracted SALARIO_BASE
            if template['meta']['company_id'] == 'convenio-sector':
                 for r in extracted_data:
                     if r['concept'] == 'SALARIO_BASE' and r['year'] >= 2024:
                          records_to_insert.append(SalaryTable(
                             company_id=company_id,
                             group=r['group'],
                             level=r['level'],
                             concept='SALARIO_BASE',
                             amount=r['amount'],
                             year=r['year']
                         ))

        logger.info(f"Inserting {len(records_to_insert)} records...")
        session.bulk_save_objects(records_to_insert)
        session.commit()
        logger.info("Done.")
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    template_file = os.path.join('backend', 'data', 'structure_templates', 'convenio_sector.json')
    # Use companies logic
    companies = ["convenio-sector", "jet2", "norwegian", "south", "azul-handling"] 
    seed_from_template(template_file, companies)
