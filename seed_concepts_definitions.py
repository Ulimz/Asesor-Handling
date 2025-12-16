
import sys
import os
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.stdout.reconfigure(encoding='utf-8')

# --- STANDALONE DATABASE SETUP ---
# Allow overriding via env var for Production Seeding
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/asistente_handling")
# Fix postgres:// legacy protocol for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SalaryConceptDefinition(Base):
    __tablename__ = "salary_concept_definitions"
    id = Column(Integer, primary_key=True, index=True)
    company_slug = Column(String, index=True)
    name = Column(String)
    code = Column(String, index=True)
    description = Column(String, nullable=True)
    input_type = Column(String, default="number") # number, checkbox, select
    is_active = Column(Boolean, default=True)
    default_price = Column(Float, default=0.0)
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_concepts(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)
        
    session = SessionLocal()
    company_id = "convenio-sector"
    
    try:
        logger.info(f"Seeding Concept Definitions for: {company_id}")
        
        # 1. Clear existing definitions for this company
        session.query(SalaryConceptDefinition).filter(SalaryConceptDefinition.company_slug == company_id).delete()
        
        concepts_to_add = []
        
        # 2. Fixed Concepts (Checkboxes usually, or auto-calc)
        # For frontend purposes, we expose those that act as flags (is_proportional, etc) or have specific UI logic
        # Ideally we expose ALL, and let Frontend decide how to render based on code.
        
        for c in template['concepts']['fixed']:
            code = c['id']
            # Determine input type
            # If it has tiers or is a flag like Supervision, it might be checkbox or select
            # BUT: Frontend logic (SalaryCalculator) now handles specific codes. 
            # We just need to ensure they EXIST in this list so they are returned by API.
            
            # Map known checkboxes/selects
            inp_type = "number" 
            if code in ['PLUS_SUPERVISION', 'PLUS_JEFATURA', 'PLUS_JORNADA_IRREGULAR', 'PLUS_FTP', 'PLUS_FIJI']:
                # These are strictly 1/0 flags or mutually exclusive selects -> Proportional fixed amounts
                inp_type = "select" if code in ['PLUS_FTP', 'PLUS_FIJI', 'PLUS_JORNADA_IRREGULAR'] else "checkbox"
            
            concepts_to_add.append(SalaryConceptDefinition(
                company_slug=company_id,
                name=c['name'],
                code=code,
                description=f"Concepto Fijo: {c['name']}",
                input_type=inp_type,
                default_price=c.get('base_value_2022', 0.0),
                is_active=True
            ))
            
            # If it has tiers, we might need to expose them?
            # Creating specific concepts for tiers if needed by frontend logic?
            # SalaryCalculator logic: `c.code.startsWith('PLUS_TURNICIDAD_')`
            # So we DO need to exist entries for `PLUS_TURNICIDAD_2_TURNOS`, etc?
            # The calculator iterates: `concepts.filter(...)`
            # So YES, we need entries for every specific option if we want them in the lists.
            if 'tiers' in c:
                for tier_key, tier_val in c['tiers'].items():
                    tier_code = f"{code}_{tier_key}" # e.g. PLUS_TURNICIDAD_2_TURNOS
                    concepts_to_add.append(SalaryConceptDefinition(
                       company_slug=company_id,
                       name=f"{c['name']} ({tier_key})",
                       code=tier_code,
                       description=f"Tier: {tier_key}",
                       input_type="checkbox" if "TURNOS" in code else "number",
                       default_price=tier_val,
                       is_active=True
                   ))

        # 3. Variable Concepts
        for c in template['concepts']['variable']:
            inp_type = "number"
            if c['id'] == 'PLUS_AD_PERSONAM' or c.get('unit') == 'euro':
                 inp_type = "manual"

            concepts_to_add.append(SalaryConceptDefinition(
                company_slug=company_id,
                name=c['name'],
                code=c['id'],
                description=f"Variable: {c['name']}",
                input_type=inp_type,
                default_price=c.get('base_value_2022', 0.0), # Will be overridden by dynamic values in calculation, but good for reference
                is_active=True
            ))

        session.bulk_save_objects(concepts_to_add)
        session.commit()
        logger.info(f"Inserted {len(concepts_to_add)} concepts.")
        
    except Exception as e:
        logger.error(f"Error seeding concepts: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    template = os.path.join('backend', 'data', 'structure_templates', 'convenio_sector.json')
    seed_concepts(template)
