
import os
import sys
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- STANDALONE DATABASE SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/asistente_handling")
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- XML EXTRACTION LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_scripts_path = os.path.join(current_dir, 'backend', 'scripts')
sys.path.append(backend_scripts_path)

try:
    from extract_salary_tables import extract_boe_salaries
except ImportError:
    def extract_boe_salaries(xml, cid): return []

def extract_azul_salaries(xml_path):
    """
    Extracts Base Salary, Hora Extra, Hora Perentoria, Hora Compl Especial from Azul XML.
    Returns list of dicts compatible with salary_tables.
    """
    import xml.etree.ElementTree as ET
    data = []
    
    # Pre-defined Base Salary (Canon 2025) - Fallback
    manual_base_2025 = [
        # Técnicos Gestores
        {"group": "Técnicos Gestores", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 29955.04, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 30542.39, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 31764.09, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 33034.65, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 33681.35, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 35031.31, "year": 2025},
        {"group": "Técnicos Gestores", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 36435.01, "year": 2025},
        # Administrativos
        {"group": "Administrativos", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18632.39, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 22065.51, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22728.97, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 23183.55, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23638.13, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24583.65, "year": 2025},
        {"group": "Administrativos", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25567.00, "year": 2025},
        # Auxiliares
        {"group": "Servicios Auxiliares", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18450.87, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 21850.75, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22507.75, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 22957.90, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23408.06, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24344.38, "year": 2025},
        {"group": "Servicios Auxiliares", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25318.15, "year": 2025},
    ]

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # MAPPINGS
        row_map = {
            "técnicos gestores": "Técnicos Gestores",
            "administrativos": "Administrativos",
            "serv. auxiliares": "Servicios Auxiliares"
        }
        
        col_map = {
             0: "Nivel 1", 
             1: "Nivel 2",
             2: "Nivel 3",
             3: "Nivel 4",
             4: "Nivel 5",
             5: "Nivel 6",
             6: "Nivel 7"
        }
        
        def parse_table(table_elem, concept_name):
            extracted = []
            tbody = table_elem.find(".//{*}tbody")
            if not tbody: return []
            
            for row in tbody.findall(".//{*}tr"):
                cells = row.findall(".//{*}td")
                if not cells: continue
                
                group_text = (cells[0].text or "").strip().lower().replace(".", "")
                group_name = None
                for k, v in row_map.items():
                    if k in group_text:
                        group_name = v
                        break
                
                if not group_name: continue
                
                value_cells = cells[1:]
                for i, cell in enumerate(value_cells):
                    if i in col_map:
                        val_str = (cell.text or "0").replace(".", "").replace(",", ".")
                        try:
                            val = float(val_str)
                            extracted.append({
                                "group": group_name,
                                "level": col_map[i],
                                "concept": concept_name,
                                "amount": val,
                                "year": 2025
                            })
                        except:
                            pass
            return extracted

        # Locate Tables by Text Preceding them
        all_content = root.findall(".//{*}texto/*")
        
        def find_table_by_title(title_fragment):
            found_title = False
            for elem in all_content:
                if elem.tag.endswith('p') and title_fragment.lower() in (elem.text or "").lower():
                    found_title = True
                    continue
                if found_title and elem.tag.endswith('table'):
                    return elem
            return None
        
        # Extracted list
        extracted_from_xml = []
        
        # NOTE: Skipping Base Salary XML Extraction to avoid duplicates/incorrect values. 
        # We rely 100% on manual_base_2025 for SALARIO_BASE.
        
        t_extra = find_table_by_title("Tabla horas extraordinarias")
        if t_extra: extracted_from_xml.extend(parse_table(t_extra, "HORA_EXTRA"))
        
        t_perentoria = find_table_by_title("Tabla horas perentorias")
        if t_perentoria: extracted_from_xml.extend(parse_table(t_perentoria, "HORA_PERENTORIA"))
        
        t_compl = find_table_by_title("Tabla horas complementarias especiales")
        if t_compl: extracted_from_xml.extend(parse_table(t_compl, "HORA_COMPLEMENTARIA_ESP"))
        
        # Merge: Manual Base + Extracted Variable
        data.extend(manual_base_2025)
        data.extend(extracted_from_xml)

    except Exception as e:
        logger.error(f"Error extracting Azul XML: {e}, falling back to manual base.")
        data.extend(manual_base_2025)
        
    return data

def seed_from_template(template_path, companies_to_seed):
    """
    Seeds database using a Master Template JSON + Dynamic XML Data.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
    except:
        with open(template_path, 'r', encoding='latin-1') as f:
            template = json.load(f)
        
    session = SessionLocal()
    
    try:
        logger.info(f"Clearing old data for companies: {companies_to_seed}")
        session.query(SalaryTable).filter(SalaryTable.company_id.in_(companies_to_seed)).delete(synchronize_session=False)
        session.commit()
        
        extracted_data = []
        if template['meta']['company_id'] == 'convenio-sector':
            xml_path = os.path.join('backend', 'data', 'xml', 'general.xml')
            if os.path.exists(xml_path):
                logger.info("Extracting dynamic values from general.xml...")
                extracted_data = extract_boe_salaries(xml_path, 'convenio-sector')
            
            # Manual 2025 Sector Data
            manual_2025 = [
                {"group": "Administrativos", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18632.39, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 22065.51, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22728.97, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 23183.55, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23638.13, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24583.65, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25567.00, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 18450.87, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 21850.75, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 22507.75, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 22957.90, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 23408.06, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 24344.38, "year": 2025},
                {"group": "Servicios Auxiliares", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 25318.15, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 1", "concept": "SALARIO_BASE", "amount": 28460.70, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 2", "concept": "SALARIO_BASE", "amount": 28516.35, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 3", "concept": "SALARIO_BASE", "amount": 29367.68, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 4", "concept": "SALARIO_BASE", "amount": 29955.04, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 5", "concept": "SALARIO_BASE", "amount": 30542.39, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 6", "concept": "SALARIO_BASE", "amount": 31764.09, "year": 2025},
                {"group": "Técnicos Gestores", "level": "Nivel 7", "concept": "SALARIO_BASE", "amount": 33034.65, "year": 2025},
                {"group": "Administrativos", "level": "Nivel 4", "concept": "HORA_EXTRA", "amount": 20.31, "year": 2025}
            ]
            extracted_data.extend(manual_2025)
            
        elif template['meta']['company_id'] == 'azul-handling':
            xml_path = os.path.join('backend', 'data', 'xml', 'azul.xml')
            extracted_data = extract_azul_salaries(xml_path) 

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
                                 records_to_insert.append(SalaryTable(company_id=company_id, group=group_name, level=level, concept=concept_id, amount=tier_val, year=2025))
                         else:
                             records_to_insert.append(SalaryTable(company_id=company_id, group=group_name, level=level, concept=concept_def['id'], amount=amount, year=2025))

                    # 3.2 Variable Concepts
                    for concept_def in template['concepts']['variable']:
                         if 'applicable_concepts' in group and concept_def['id'] not in group['applicable_concepts']:
                             continue

                         val = concept_def.get('base_value_2022', 0.0)
                         if concept_def.get('source') == 'xml_table':
                             dynamic_val = find_extracted_value(group_name, level, concept_def['id'], 2025)
                             if dynamic_val: val = dynamic_val
                        
                         records_to_insert.append(SalaryTable(company_id=company_id, group=group_name, level=level, concept=concept_def['id'], amount=val, year=2025))
            
            # 3.3 Explicitly Inject Extracted SALARIO_BASE for ANY company
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
    # SEED SECTOR
    template_file = os.path.join('backend', 'data', 'structure_templates', 'convenio_sector.json')
    if os.path.exists(template_file):
        companies = ["convenio-sector", "jet2", "norwegian", "south"] 
        seed_from_template(template_file, companies)

    # SEED AZUL
    template_file_azul = os.path.join('backend', 'data', 'structure_templates', 'azul_handling.json')
    if os.path.exists(template_file_azul):
        seed_from_template(template_file_azul, ["azul-handling"])
