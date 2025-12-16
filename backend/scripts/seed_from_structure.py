import os
import sys
import json
import logging
from sqlalchemy.orm import Session
# Add project root directory to path (parent of backend)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database import SessionLocal, engine
from backend.models import SalaryTable, Company
from backend.scripts.extract_salary_tables import extract_boe_salaries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_from_template(template_path, companies_to_seed):
    """
    Seeds database using a Master Template JSON + Dynamic XML Data.
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)
        
    session = SessionLocal()
    
    try:
        # 1. Clear existing data for these companies
        logger.info(f"Clearing old data for companies: {companies_to_seed}")
        session.query(SalaryTable).filter(SalaryTable.company_id.in_(companies_to_seed)).delete(synchronize_session=False)
        session.commit()
        
        # 2. Extract Dynamic Data from XML if available
        # Ideally, we map the template 'company_id' (e.g. convenio-sector) to an XML file.
        # For now, hardcoded for Sector logic.
        extracted_data = []
        if template['meta']['company_id'] == 'convenio-sector':
            xml_path = os.path.join(os.path.dirname(__file__), '../backend/data/xml/general.xml')
            if os.path.exists(xml_path):
                logger.info("Extracting dynamic values from general.xml...")
                extracted_data = extract_boe_salaries(xml_path, 'convenio-sector')
            else:
                logger.warning("general.xml not found! Using template base values only.")

        # Helper to find value in extracted data
        def find_extracted_value(group_name, level_name, concept_key, year=2025):
            # Normalize group name to canonical
            # (Assuming extracted_data is already normalized by our previous fixes)
            for r in extracted_data:
                if r['year'] == year and r['concept'] == concept_key:
                    # Fuzzy match group/level? Or require exact?
                    # Our extractor uses canonical groups now.
                    if r['group'] == group_name and r['level'] == level_name:
                        return r['amount']
            return None

        # 3. Iterate Template and Insert
        records_to_insert = []
        
        for company_id in companies_to_seed:
            logger.info(f"Seeding structure for: {company_id}")
            
            # Iterate Canonical Groups
            for group in template['groups']:
                group_name = group['name']
                
                # Iterate Canonical Levels
                for level in group['levels']:
                    
                    # 3.1 Insert Fixed Concepts
                    for concept_def in template['concepts']['fixed']:
                         # Check if concept applies to this group (if applicable_concepts is restrictive)
                         if 'applicable_concepts' in group and concept_def['id'] not in group['applicable_concepts']:
                             continue # Skip if not applicable
                             
                         amount = concept_def.get('base_value_2022', 0.0)
                         
                         # Handle Tiers (Turnicidad) - Insert multiple rows or handling logic?
                         # For database simplicity, maybe insert base value and handle tiers in frontend?
                         # OR insert one row per tier? Let's check DB schema. 
                         # Schema is Simple: Group | Level | Concept | Amount.
                         # If tiers exist, we might need multiple rows with distinct concept names or suffixes?
                         # For now, let's insert the BASE value or the first Tier.
                         # BETTER: Insert distinct concepts for tiers if needed (e.g. PLUS_TURNICIDAD_2)
                         # The template defines tiers in 'tiers' object.
                         
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

                    # 3.2 Insert Variable Concepts
                    for concept_def in template['concepts']['variable']:
                         if 'applicable_concepts' in group and concept_def['id'] not in group['applicable_concepts']:
                             continue

                         val = concept_def.get('base_value_2022', 0.0)
                         
                         # Try to fetch dynamic value
                         if concept_def.get('source') == 'xml_table':
                             dynamic_val = find_extracted_value(group_name, level, concept_def['id'], 2025)
                             if dynamic_val:
                                 val = dynamic_val
                                 logger.debug(f"Found dynamic value for {concept_def['id']} {group_name} {level}: {val}")
                             else:
                                 # Fallback to 2024 or 2023? Or stay 0?
                                 # Try 2024
                                 dynamic_val = find_extracted_value(group_name, level, concept_def['id'], 2024)
                                 if dynamic_val: val = dynamic_val
                        
                         # Special Case: SALARIO_BASE is not in 'concepts' list of template but is implicit?
                         # Actually usually Salario Base is strictly extracted.
                         # Make sure to include it.
                         
                         records_to_insert.append(SalaryTable(
                             company_id=company_id,
                             group=group_name,
                             level=level,
                             concept=concept_def['id'],
                             amount=val,
                             year=2025
                         ))
            
            # 3.3 Explicitly Inject Extracted SALARIO_BASE if not in template
            # (The template listed Variable/Fixed pluses but maybe forgot Base)
            # Let's iterate all extracted Base Salaries for this group and insert them.
            if template['meta']['company_id'] == 'convenio-sector':
                 for r in extracted_data:
                     if r['concept'] == 'SALARIO_BASE' and r['year'] >= 2024:
                          # Only insert if it matches one of our canonical groups (which it should)
                          records_to_insert.append(SalaryTable(
                             company_id=company_id,
                             group=r['group'],
                             level=r['level'],
                             concept='SALARIO_BASE',
                             amount=r['amount'],
                             year=r['year']
                         ))

        # Batch Insert
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
    template_file = os.path.join(os.path.dirname(__file__), '../backend/data/structure_templates/convenio_sector.json')
    companies = ["convenio-sector", "jet2", "norwegian", "south"] 
    seed_from_template(template_file, companies)

