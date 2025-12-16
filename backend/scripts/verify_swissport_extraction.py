
import os
import sys
import logging
from bs4 import BeautifulSoup

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.extract_salary_tables import extract_boe_salaries

def test_swissport_extraction():
    xml_path = os.path.join(os.path.dirname(__file__), '../data/xml/swissport.xml')
    
    if not os.path.exists(xml_path):
        logging.error(f"File not found: {xml_path}")
        return

    logging.info(f"Parsing {xml_path} using REAL extract_boe_salaries...")
    
    results = extract_boe_salaries(xml_path, "swissport")
    
    logging.info(f"Extracted {len(results)} records.")
    
    # Analyze unique groups and levels
    unique_groups = set()
    levels_by_group = {}
    
    for r in results:
        g = r.get('group')
        l = r.get('level')
        unique_groups.add(g)
        if g not in levels_by_group:
            levels_by_group[g] = set()
        levels_by_group[g].add(l)
        
    logging.info("--- UNIQUE GROUPS FOUND ---")
    for g in sorted(unique_groups):
        logging.info(f"GROUP: '{g}'")
        levels = sorted(list(levels_by_group[g]))[:5] # Show first 5 levels
        logging.info(f"  Levels (sample): {levels}")

if __name__ == "__main__":
    test_swissport_extraction()
