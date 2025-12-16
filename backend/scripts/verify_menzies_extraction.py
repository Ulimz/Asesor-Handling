
import sys
import os
import logging
from pathlib import Path
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.extract_salary_tables import _parse_level_matrix_table, _parse_concept_columns_table, clean_group_name

def debug_menzies():
    xml_path = os.path.join(os.path.dirname(__file__), '../data/xml/menzies.xml')
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'lxml-xml')
    company_id = "menzies"
    
    # Simulate the main loop logic for detection
    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables.")
    
    for i, table in enumerate(tables):
        # determine previous node for title
        prev_node = table.find_previous_sibling()
        prev_p = None
        while prev_node:
            if prev_node.name == "p":
                prev_p = prev_node
                break
            prev_node = prev_node.find_previous_sibling()
            
        title_text = prev_p.get_text(strip=True) if prev_p else "Unknown Title"
        
        # Headers
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        header_text = " ".join(headers).lower()

        # Skip logic
        if "enero" in header_text and "febrero" in header_text: continue
        if "puntos" in header_text: continue
        
        if "tabla salarial" not in title_text.lower(): continue
        
        # Detection
        is_level_matrix = any(f"nivel {n}" in header_text for n in range(1, 4))
        is_concept_cols = "s. base" in header_text or "salario base" in header_text or "conceptos fijos" in header_text
        
        if not is_concept_cols: continue # ONLY DEBUG CONCEPTS
        
        print(f"\nTable {i}: '{title_text}'")
        print(f"  Matrix={is_level_matrix}, Concept={is_concept_cols}")
        
        results = []
        if is_level_matrix:
            print("  --> Parsing as Level Matrix")
            results = _parse_level_matrix_table(table, company_id, 2024, title_text)
        elif is_concept_cols:
            print("  --> Parsing as Concept Columns")
            results = _parse_concept_columns_table(table, company_id, 2024)
            
        # Inspect All Unique Groups
        if results:
            groups = set(r['group'] for r in results)
            print(f"  Unique Groups Found: {sorted(list(groups))}")
            
            # Print sample garbage if found
            for r in results:
                if "Agente" in r['group'] or "nivel" in r['group'].lower() or "," in r['group']:
                     print(f"    WARNING: Suspicious Group='{r['group']}' | L='{r['level']}'")
                     break # Just show one example
        else:
            print("  No records extracted.")

if __name__ == "__main__":
    debug_menzies()
