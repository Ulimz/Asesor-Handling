
import os
import sys
import logging
from bs4 import BeautifulSoup

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.extract_salary_tables import extract_boe_salaries

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_sector_extraction():
    xml_path = os.path.join(os.path.dirname(__file__), '../data/xml/general.xml')
    
    if not os.path.exists(xml_path):
        logging.error(f"File not found: {xml_path}")
        return

    logging.info(f"Parsing {xml_path} using REAL extract_boe_salaries...")
    
    results = extract_boe_salaries(xml_path, "convenio-sector")
    
    logging.info(f"Extracted {len(results)} records.")
    
    # Analyze Concepts found
    unique_concepts = set()
    concepts_by_group = {}
    
    for r in results:
        g = r.get('group')
        c = r.get('concept')
        unique_concepts.add(c)
        
        if g not in concepts_by_group:
            concepts_by_group[g] = set()
        concepts_by_group[g].add(c)
        
    logging.info("--- UNIQUE CONCEPTS FOUND ---")
    for c in sorted(unique_concepts):
        logging.info(f"CONCEPT: '{c}'")
        
    logging.info("\n--- CONCEPTS BY GROUP ---")
    for g in sorted(concepts_by_group.keys()):
        logging.info(f"GROUP: '{g}' -> {sorted(list(concepts_by_group[g]))}")

if __name__ == "__main__":
    test_sector_extraction()
