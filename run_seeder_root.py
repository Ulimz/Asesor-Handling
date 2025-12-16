
import os
import sys
import json
import logging

# Add backend directory to path explicitly so we can import 'database', 'models', etc directly
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
sys.path.append(backend_path)

# Import directly assuming 'backend' is in path
try:
    from database import SessionLocal, engine
    from models import SalaryTable, Company
    from scripts.extract_salary_tables import extract_boe_salaries
except ImportError:
    # Fallback: maybe running from backend dir?
    sys.path.append(os.getcwd())
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
        extracted_data = []
        if template['meta']['company_id'] == 'convenio-sector':
            xml_path = os.path.join('backend', 'data', 'xml', 'general.xml')
            if os.path.exists(xml_path):
                logger.info("Extracting dynamic values from general.xml...")
                extracted_data = extract_boe_salaries(xml_path, 'convenio-sector')
            else:
                logger.warning(f"general.xml not found at {xml_path}! Using template base values only.")

        # Helper to find value in extracted data
        def find_extracted_value(group_name, level_name, concept_key, year=2025):
            for r in extracted_data:
                if r['year'] == year and r['concept'] == concept_key:
                    if r['group'] == group_name and r['level'] == level_name:
                        return r['amount']
            return None

        # 3. Iterate Template and Insert
        records_to_insert = []
        
        for company_id in companies_to_seed:
            logger.info(f"Seeding structure for: {company_id}")
            
            for group in template['groups']:
                group_name = group['name']
                
                for level in group['levels']:
                    
                    # 3.1 Insert Fixed Concepts
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

                    # 3.2 Insert Variable Concepts
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
            
            # 3.3 Explicitly Inject Extracted SALARIO_BASE if not in template
            if template['meta']['company_id'] == 'convenio-sector':
                 for r in extracted_data:
                     # Only insert base salary, effectively merging extraction + template
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
    companies = ["convenio-sector", "jet2", "norwegian", "south"] 
    seed_from_template(template_file, companies)
