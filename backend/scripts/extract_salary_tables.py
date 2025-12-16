
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_spanish_number(text):
    """
    Parses a Spanish formatted number (e.g., '1.021,46') into a float (1021.46).
    """
    if not text or text.strip() == "":
        return 0.0
    clean_text = text.strip().replace(".", "").replace(",", ".")
    # Remove any non-numeric chars except dot
    clean_text = re.sub(r'[^\d.]', '', clean_text)
    try:
        return float(clean_text)
    except ValueError:
        return 0.0

def clean_group_name(raw_name):
    """
    Cleans dirty group names extracted from PDF/XML text.
    Removes amounts, trailing dots, and standardizes known variations.
    Example: "Serv. Auxiliares. 17.500,00" -> "Servicios Auxiliares"
    """
    if not raw_name: return "General"
    
    # 1. Remove numbers and currency-like patterns (17.500,00)
    # This regex looks for digits possibly followed by dots/commas and more digits
    # Also explicitly remove Euro symbol
    text = re.sub(r'[€]', '', raw_name)
    text = re.sub(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?', '', text)
    
    # 2. Cleanup whitespace and punctuation
    text = text.replace(":", "").replace(".", "").strip()
    
    # 3. Canonical Mappings for known abbreviations/variants
    text_lower = text.lower()
    
    if "serv" in text_lower and "aux" in text_lower:
        return "Servicios Auxiliares"
    if "admin" in text_lower:
        return "Administrativos"
    if "gestores" in text_lower and "servicio" in text_lower:
        return "Gestores de Servicios"
    if "agentes" in text_lower and "jefes" in text_lower:
        return "Agentes Jefes"
    if "supervisores" in text_lower:
        return "Supervisores"
    if "téc" in text_lower and "mant" in text_lower and "aeron" in text_lower:
        return "Técnicos Mantenimiento Aeronaves"
    if "téc" in text_lower and "mant" in text_lower: # Catch-all for other maintenance
        return text # Keep full name but cleaned
        
    # If empty after clean (e.g. it was just a number), return Original or General
    if not text:
        return "General"
        
    return text

def extract_iberia_salaries(xml_path):
    """
    Extracts salary data from Iberia's XML.
    Targeting the 'Tabla salarial' with 'Efectividad 1 de enero de 2023'.
    """
    logger.info(f"Parsing {xml_path}...")
    
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    soup = BeautifulSoup(content, "xml") # Using XML parser but BS4 handles HTML inside fine
    
    # Strategy: Find the paragraph mentioning "Efectividad 1 de enero de 2023" AND "Tabla salarial"
    # Then find the next table.
    
    # Identifying the target table
    # We look for the specific table that contains "Sueldo base" and "Prima Productividad" in headers
    
    tables = soup.find_all("table")
    target_table = None
    
    for i, table in enumerate(tables):
        # Check headers
        th_tags = table.find_all("th")
        if not th_tags:
            continue
            
        headers = [th.get_text(strip=True).lower() for th in th_tags]
        logger.debug(f"Table {i} headers: {headers}")
        
        # Relaxed checks
        # "sueldo base" should be there
        # "prima productividad" should be there
        # "remun" might be "remunerac. anual *"
        
        has_sueldo = any("sueldo base" in h for h in headers)
        has_prod = any("prima productividad" in h for h in headers)
        has_anual = any("remunerac" in h and "anual" in h for h in headers)
        
        if has_sueldo and has_prod and has_anual:
             target_table = table
             break
    
    if not target_table:
        logger.error("Could not find Iberia Salary Table.")
        return []

    logger.info("Found candidate Salary Table.")
    
    # 1. Identify Groups
    # Search for patterns like "Cuantías máximas por categoría X" or specifically known groups
    # We can perform a quick scan or regex on the text content
    
    known_groups = set()
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if "Cuantías máximas por categoría" in text:
            # Extract group name
            raw = text.replace("Cuantías máximas por categoría", "").strip()
            group_name = clean_group_name(raw)
            if group_name:
                known_groups.add(group_name)
    
    if not known_groups:
        # Fallback if detection fails, though we saw "Servicios Auxiliares", "Administrativos"
        known_groups = {"General"}
        logger.warning("No specific groups found, defaulting to 'General'")
    else:
        logger.info(f"Found groups: {known_groups}")

    # Parse rows
    results = []
    
    tbody = target_table.find("tbody")
    rows = tbody.find_all("tr")
    
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 6:
            continue
            
        nivel = cells[0].get_text(strip=True)
        sueldo_base = parse_spanish_number(cells[1].get_text(strip=True))
        prima_prod = parse_spanish_number(cells[2].get_text(strip=True))
        plus_transitorio = parse_spanish_number(cells[3].get_text(strip=True))
        # total_monthly = parse_spanish_number(cells[4].get_text(strip=True))
        annual_remuneration = parse_spanish_number(cells[5].get_text(strip=True))
        
        # Broadcast to all found groups
        for group in known_groups:
            # 1. Base Annual
            results.append({
                "company_id": "iberia",
                "year": 2023,
                "group": group,
                "level": nivel,
                "concept": "BASE_ANNUAL",
                "amount": annual_remuneration
            })
            
            # 2. Base Monthly (Sueldo Base)
            results.append({
                "company_id": "iberia",
                "year": 2023,
                "group": group,
                "level": nivel,
                "concept": "SALARIO_BASE",
                "amount": sueldo_base
            })
            
            # 3. Prima Productividad
            results.append({
                "company_id": "iberia",
                "year": 2023,
                "group": group,
                "level": nivel,
                "concept": "PRIMA_PROD",
                "amount": prima_prod
            })
    
            # 4. Complemento Transitorio
            results.append({
                "company_id": "iberia",
                "year": 2023,
                "group": group,
                "level": nivel,
                "concept": "PLUS_TRANSITORIO",
                "amount": plus_transitorio
            })
        
    # --- Secondary Tables Extraction ---

    # 2. Extract Trienios (Antigüedad)
    trienios_data = []
    trienios_table = None
    for table in tables:
        if table.find("th", string=re.compile("Incremento por cada trienio", re.IGNORECASE)):
            trienios_table = table
            break
            
    if trienios_table:
        rows = trienios_table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 2: continue
            lbl = cells[0].get_text(strip=True)
            val = parse_spanish_number(cells[1].get_text(strip=True))
            
            # Broadcast to all groups as Trienios usually apply generally or we lack mapping
            # Assuming General application for now
            for g in known_groups:
                trienios_data.append({
                    "company_id": "iberia",
                    "year": 2023,
                    "group": g,
                    "level": lbl,
                    "concept": "TRIENIO",
                    "amount": val
                })
    results.extend(trienios_data)

    # 3. Extract Horas Perentorias
    perentorias_data = []
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        # Look for "Horas perentorias" and "2023"
        if "Horas perentorias" in txt and "2023" in txt:
            # Heuristic Group Identification
            target_group = "General"
            if "Administrativos" in txt: target_group = "Administrativos"
            elif "Servicios Auxiliares" in txt: target_group = "Servicios Auxiliares"
            elif "Técnicos" in txt: target_group = "Técnicos Mantenimiento Aeronaves" 
            
            # Find next table
            nxt = p.find_next_sibling()
            while nxt and nxt.name != "table":
                nxt = nxt.find_next_sibling()
                
            if nxt and nxt.name == "table":
                p_rows = nxt.find_all("tr")
                for pr in p_rows:
                    p_cells = pr.find_all("td")
                    # We need a cell with a price
                    found_price = False
                    for pc in p_cells:
                        ptxt = pc.get_text(strip=True)
                        if "€" in ptxt:
                            price = parse_spanish_number(ptxt)
                            if price > 0:
                                # Found a price, use it
                                # Level is likely in a previous cell
                                lvl_txt = "Standard" # Default
                                # Try to find level text in row
                                for pcl in p_cells:
                                    if "Nivel" in pcl.get_text():
                                        lvl_txt = pcl.get_text(strip=True)
                                        break
                                
                                perentorias_data.append({
                                    "company_id": "iberia",
                                    "year": 2023,
                                    "group": target_group,
                                    "level": lvl_txt,
                                    "concept": "HORA_PERENTORIA",
                                    "amount": price
                                })
                                found_price = True
                                break # Take first price (usually "Opción Cobrar")

    results.extend(perentorias_data)

    # 4. Extract "Cuantías Máximas" (Variables)
    pluses_data = []
    for p in soup.find_all("p"):
        txt = p.get_text(strip=True)
        if "Cuantías máximas por categoría" in txt:
            raw = txt.replace("Cuantías máximas por categoría", "").strip()
            g_name = clean_group_name(raw)
            # Find table
            nxt = p.find_next_sibling()
            while nxt and nxt.name != "table":
                nxt = nxt.find_next_sibling()
            
            if nxt and nxt.name == "table":
                v_rows = nxt.find_all("tr")
                for vr in v_rows:
                    v_cells = vr.find_all("td")
                    if not v_cells: continue
                    
                    # Extract Name and Value
                    # Name is text, Value is number
                    concept_parts = []
                    val = 0.0
                    for vc in v_cells:
                        vt = vc.get_text(strip=True)
                        if any(c.isdigit() for c in vt) and "," in vt:
                            if val == 0.0: val = parse_spanish_number(vt)
                        else:
                            if len(vt) > 2: concept_parts.append(vt)
                            
                    concept_name = " ".join(concept_parts).strip()
                    if val > 0 and concept_name:
                         # Normalize Slug
                        slug = "PLUS_VARIABLE"
                        if "Peligrosidad" in concept_name or "Sala Blanca" in concept_name: slug = "PLUS_PELIGROSIDAD"
                        elif "Toxicidad" in concept_name: slug = "PLUS_TOXICIDAD"
                        elif "Residencia" in concept_name: slug = "PLUS_RESIDENCIA"
                        elif "Jornada" in concept_name: slug = "PLUS_JORNADA_ESPECIAL"
                        elif "Turnos" in concept_name: slug = "PLUS_TURNICIDAD"
                        
                        pluses_data.append({
                            "company_id": "iberia",
                            "year": 2023,
                            "group": g_name,
                            "level": "All",
                            "concept": slug,
                            "amount": val
                        })
    results.extend(pluses_data)

    # 5. Regex Text Mining
    # Look for "Dieta ... : X,XX"
    regex_concepts = []
    text_content = soup.get_text()
    
    # Patterns
    patterns = [
        (r"(?:Dieta|Manutención)\s*(?:Nacional|Internacional)?.*?:?\s*(\d{1,3}(?:[.,]\d{3})*(?:,\d{2}))", "DIETA"),
        (r"(?:Comida|Cena).*?:?\s*(\d{1,3}(?:[.,]\d{3})*(?:,\d{2}))", "COMIDA"),
    ]
    
    for pat, slug in patterns:
        for match in re.finditer(pat, text_content, re.IGNORECASE):
            val_str = match.group(1)
            val = parse_spanish_number(val_str)
            if val > 0:
                regex_concepts.append({
                    "company_id": "iberia",
                    "year": 2023,
                    "group": "General",
                    "level": "All",
                    "concept": slug,
                    "amount": val
                })
    results.extend(regex_concepts)

    return results


def extract_groundforce_salaries(xml_path):
    """
    Extracts salary data from Groundforce's XML.
    Targeting 'Tabla salarial 2024 Groundforce'.
    """
    logger.info(f"Parsing {xml_path}...")
    
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    soup = BeautifulSoup(content, "xml")
    
    # 1. Find the 2024 Table
    target_table = None
    # We look for the paragraph "Tabla salarial 2024 Groundforce"
    # The table is usually immediately after
    
    # Try finding the node text first
    year = 2024
    header_node = soup.find(string=re.compile(r"Tabla salarial\s+2024\s+Groundforce", re.IGNORECASE))
    
    if not header_node:
        # Fallback to 2023 if 2024 not found
        header_node = soup.find(string=re.compile(r"Tabla salarial\s+2023\s+Groundforce", re.IGNORECASE))
        year = 2023
    
    if header_node:
        # Navigate to parent p, then next sibling table
        # Structure in view_file: <p class="centro_negrita">Tabla ...</p> ... <table ...>
        # There might be an intermediate P element "2 por 100" (percentage increase)
        current = header_node.parent
        while current:
            current = current.find_next_sibling()
            if current and current.name == "table":
                target_table = current
                break
    
    if not target_table:
        logger.error("Could not find Groundforce Salary Table.")
        return []

    logger.info(f"Found Groundforce Salary Table for {year}")
    
    results = []
    tbody = target_table.find("tbody")
    rows = tbody.find_all("tr")
    
    current_group = "General"
    
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
            
        # Logic for rowspan in first column (Group)
        # Full row: Group, Category, T.Anual, S.Base, Plus Transp, Comp Puesto, ...
        # Standard full row has 10 columns (checked in analysis)
        # Continuation row has 9 columns (Group omitted)
        
        # NOTE: We need to be careful with hidden columns or colspan, but assuming standard BOE structure
        
        text_values = [c.get_text(strip=True) for c in cells]
        
        if len(text_values) >= 10:
            current_group = clean_group_name(text_values[0]) # Clean it!
            category = text_values[1].strip(".").strip()
            # Indices for data
            idx_annual = 2
            idx_base = 3
            idx_transp = 4
            idx_puesto = 5
            idx_extra = 6
        elif len(text_values) >= 9:
            # Group is implicit from previous
            category = text_values[0].strip(".").strip()
            idx_annual = 1
            idx_base = 2
            idx_transp = 3
            idx_puesto = 4
            idx_extra = 5
        else:
            continue
            
        # Extract values
        t_anual = parse_spanish_number(text_values[idx_annual])
        s_base_14 = parse_spanish_number(text_values[idx_base])
        # s_base_monthly = s_base_14 / 14.0 # Or just store what is there? 
        # The table header says "S. base (x 14)". The VALUE in the cell is likely the Annual Base? 
        # Wait. "S. base (x 14)" -> 1.996,76. "T. anual" -> 35.774,86.
        # 1996 * 14 = 27,954. No.
        # Maybe 1996 IS the monthly base? 1996 * 14 = 27k.
        # T.Anual 35k includes Pluses.
        # Let's assume the column "S. base (x 14)" contains the MONTHLY value.
        # Checking logic: 1996.76 * 14 = 27,954.64
        # T.Anual = 35,774.86.
        # Diff = ~8k.
        # Plus Transp (105.97 * 12) = 1271.
        # Comp Puesto (545.71 * 12) = 6548.
        # 27954 + 1271 + 6548 = 35773. -> MATCH!
        # So "S. base (x 14)" column contains the MONTHLY base salary.
        
        s_base_monthly = parse_spanish_number(text_values[idx_base])
        plus_transp_monthly = parse_spanish_number(text_values[idx_transp])
        comp_puesto_monthly = parse_spanish_number(text_values[idx_puesto])
        hora_extra = parse_spanish_number(text_values[idx_extra])
        
        # Generate entries
        # Base Annual = T.Anual from table? Or calculated? 
        # Using T.Anual from table is safer as it matches the "Total" concept.
        # But we also want components.
        
        # 1. Base Annual (Total Remuneration)
        results.append({
            "company_id": "groundforce",
            "year": year,
            "group": current_group,
            "level": category, # Using Category Name as level/category
            "concept": "BASE_ANNUAL",
            "amount": t_anual
        })
        
        # 2. Base Monthly
        results.append({
            "company_id": "groundforce",
            "year": year,
            "group": current_group,
            "level": category,
            "concept": "SALARIO_BASE",
            "amount": s_base_monthly
        })
        
        # 3. Plus Transporte
        results.append({
            "company_id": "groundforce",
            "year": year,
            "group": current_group,
            "level": category,
            "concept": "PLUS_TRANSPORTE",
            "amount": plus_transp_monthly
        })
        
        # 4. Comp Puesto
        results.append({
            "company_id": "groundforce",
            "year": year,
            "group": current_group,
            "level": category,
            "concept": "PLUS_PUESTO", # Need to verify this concept
            "amount": comp_puesto_monthly
        })

         # 5. Hora Extra
        results.append({
            "company_id": "groundforce",
            "year": year,
            "group": current_group,
            "level": category,
            "concept": "HORA_EXTRA",
            "amount": hora_extra
        })
        
    return results

def extract_boe_salaries(xml_path, company_id):
    """
    Generic extractor for BOE-style XML files (Menzies, Swissport, etc.)
    that contain embedded HTML tables in the <texto> tag.
    
    Handlers two main types of tables:
    1. Concept-Column: Rows are Categories, Cols are Concepts (Base, Plus, etc.)
    2. Level-Matrix: Rows are Categories, Cols are Levels (Nivel 1, Nivel 2...)
    """
    logger.info(f"extract_boe_salaries: Parsing {xml_path} for {company_id}...")
    
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Use html.parser to be more lenient with mixed content and namespaces
    soup = BeautifulSoup(content, "html.parser")
    
    # BOE XMLs usually have a <texto> tag containing the HTML body
    # But sometimes parsers fail to find it or it's named differently.
    # robust approach: Search ALL tables in the document.
    tables = soup.find_all("table")
    logger.info(f"Found {len(tables)} tables (global search) in {company_id}")
    
    results = []
    
    # Context state
    current_year = 2025 # Default to latest, or extract from text
    
    for i, table in enumerate(tables):
        # 1. Identify Context (Title/Preceding Text)
        prev_p = table.find_previous(["p", "h1", "h2", "h3"])
        title_text = prev_p.get_text(strip=True) if prev_p else ""
        
        # Determine Year from title if possible
        if "2023" in title_text: current_year = 2023
        elif "2024" in title_text: current_year = 2024
        elif "2025" in title_text: current_year = 2025
        
        # Determine Table Logic
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        header_text = " ".join(headers).lower()
        
        # Skip non-salary tables (like Vacation Points in Menzies)
        if "enero" in header_text and "febrero" in header_text:
            continue
        if "puntos" in header_text:
            continue

        logger.info(f"Processing Table {i}: '{title_text}'")

        # --- Detection Strategy ---
        is_level_matrix = any(f"nivel {n}" in header_text for n in range(1, 4))
        is_concept_cols = "s. base" in header_text or "salario base" in header_text or "conceptos fijos" in header_text

        if is_level_matrix:
            results.extend(_parse_level_matrix_table(table, company_id, current_year, title_text))
        elif is_concept_cols:
            results.extend(_parse_concept_columns_table(table, company_id, current_year))
        else:
            logger.debug(f"Skipping undefined table structure: {title_text}")
            
    return results

def _parse_level_matrix_table(table, company_id, year, title_text):
    """
    Parses tables where Columns = Levels (Nivel 1, Nivel 2...)
    and the Table Title defines the concept (e.g. "Precio Hora Perentoria").
    """
    results = []
    
    # Map Headers to Levels
    # Typical Header: [Grupo, Categoría, Nivel 1, Nivel 2, ...]
    headers = []
    level_map = {} # col_index -> level_value (int or str)
    
    # Find the header row (thead)
    thead = table.find("thead")
    if not thead: return []
    
    # If multiple header rows, flatten or take the last one with "Nivel"
    header_rows = thead.find_all("tr")
    # Usually the last row has the specific levels
    target_header_row = header_rows[-1]
    
    for idx, th in enumerate(target_header_row.find_all("th")):
        text = th.get_text(strip=True).lower()
        headers.append(text)
        if "nivel" in text:
            if "entrada" in text or "base" in text:
                level_map[idx] = 1
            else:
                # Extract number
                level_match = re.search(r'nivel\s*(\d+)', text)
                if level_match:
                    level_map[idx] = level_match.group(1)
    
    if not level_map:
        return []

    # Determine Concept from Title
    concept = "UNKNOWN"
    title_upper = title_text.upper()
    if "HORA PERENTORIA" in title_upper: concept = "HORA_PERENTORIA"
    elif "PLUS PROGRESI" in title_upper or "PLUS PROGRESIÓN" in title_upper: concept = "PLUS_PROGRESION"
    elif "HORA EXTRA" in title_upper: concept = "HORA_EXTRA"
    elif "NOCTURNA" in title_upper: concept = "HORA_NOCTURNA"
    elif "FESTIVA" in title_upper: concept = "HORA_FESTIVA"
    
    # Parse Rows
    tbody = table.find("tbody")
    if not tbody: return []
    
    current_group = "General"

    # Sort level_map keys to ensure we access data cells in correct order 
    # (though typically they are sequential)
    sorted_level_idxs = sorted(level_map.keys())
    num_levels = len(sorted_level_idxs)
    
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if not cells: continue
        
        num_cells = len(cells)
        # Determine how many label columns exist in this specific row
        # by checking how many cells are EXTRA compared to the expected data columns
        # However, be careful if the row is missing some data cells.
        # Stronger heuristic: The Last N columns are data. The rest are labels.
        
        label_cols_count = num_cells - num_levels
        if label_cols_count < 0: label_cols_count = 0 # Should check malformed

        # Extract Group and Category
        row_group = None
        row_category = "Unknown"
        
        if label_cols_count >= 2:
            # Full row: [Group, Category, Data...]
            t0 = cells[0].get_text(strip=True)
            t1 = cells[1].get_text(strip=True)
            row_group = clean_group_name(t0)
            row_category = t1
            current_group = row_group
        elif label_cols_count == 1:
            # Short row or Single Label: [Category|Group, Data...]
            t0 = cells[0].get_text(strip=True)
            t0_clean = clean_group_name(t0) # Clean potential group name
            
            # CRITICAL LOGIC FOR AVIAPARTNER / WFS / AZUL (Type 1 Matrix)
            # If we are in a matrix table (multiple salary levels in columns)
            # AND existing logic implies General/Inherit.
            # We assume this single label IS the Group Name.
            if num_levels > 1: # Matrix Table
                 # Case 1: Sub-row of a previously defined group (EasyJet style)
                 # Usually indented or implicit, but for Aviapartner each row is a new Group.
                 # Heuristic: If t0 looks like a major group name?
                 
                 # Since Aviapartner has "Técnicos Gestores" in Col 0 and Level 1..7 in Col 1..7
                 # We should treat t0 as the Group.
                 
                 # NOTE: For EasyJet, we used rowspans to populate 'current_group'.
                 # If 'current_group' is set from a rowspan in a previous row (label_cols=2),
                 # and this row only has 1 label col (label_cols=1), 
                 # then this row is likely a Category under that Group.
                 
                 # But for Aviapartner, every row has 1 label col. 'current_group' starts as 'General'.
                 if current_group == "General":
                     row_group = t0_clean
                     row_category = "Base" # Levels will handle differentiation
                 else:
                     # We are inside a group (e.g. Menzies/EasyJet subrow)
                     row_category = t0
                     row_group = current_group
            else:
                # Not a matrix table? Or just 1 level? 
                # Fallback: Treat as Category, Group=General
                if current_group != "General":
                    row_category = t0
                    row_group = current_group
                else:
                    row_category = t0
                    row_group = "General"
        else:
            # No labels? Inherit everything?
            row_group = current_group
            row_category = "Base"

        row_category = row_category.strip(".").strip()
        
        # Iterate Data Cells (Right-Aligned)
        data_cells = cells[-num_levels:]
        
        for i, cell in enumerate(data_cells):
            header_idx = sorted_level_idxs[i]
            level_val = level_map[header_idx]
            
            val_text = cell.get_text(strip=True)
            if val_text in ["N/A", "-"]: continue
            
            amount = parse_spanish_number(val_text)
            
            # Construct Level String if needed to disambiguate or just use raw level
            # If concept is Level Matrix, the LEVEL is distinct from Category.
            # E.g. Category="Jefe Area", Level="Nivel 1"
            # So DB Level field should probably combine them?
            # Or use "Level 1" as level and "Jefe Area" as... ? 
            # In DB: Group="Tecnicos", Level="Jefe Area - Nivel 1" is best for selector.
            
            # Clean up Level String
            if row_category == "Base" or row_category == "":
                 final_level_str = f"Nivel {level_val}"
            else:
                 final_level_str = f"{row_category} - Nivel {level_val}"
            
            if amount > 0:
                results.append({
                    "company_id": company_id,
                    "year": year,
                    "group": row_group,
                    "level": final_level_str,
                    "concept": concept,
                    "amount": amount
                })
    return results

def _parse_concept_columns_table(table, company_id, year):
    """
    Parses tables where Columns = Concepts (S. Base, Plus X, Plus Y)
    Rows = Categories.
    """
    results = []
    
    header_map = {} # col_index -> concept_key
    
    # Strategy: Find LAST header row for specific concepts
    thead = table.find("thead")
    if not thead: return []
    
    rows = thead.find_all("tr")
    last_row = rows[-1]
    cols = last_row.find_all("th")
    
    for idx, th in enumerate(cols):
        text = th.get_text(strip=True).lower()
        
        if "base" in text: header_map[idx] = "SALARIO_BASE"
        elif "función" in text or "funcion" in text: header_map[idx] = "PLUS_FUNCION"
        elif "extra" in text and "hora" not in text: header_map[idx] = "PAGA_EXTRA" # P. Extra (x2)
        elif "transporte" in text: header_map[idx] = "PLUS_TRANSPORTE"
        elif "manutencion" in text or "manutención" in text: header_map[idx] = "PLUS_MANUTENCION"
        elif "madrugue" in text: header_map[idx] = "PLUS_MADRUGUE"
        elif "nocturn" in text and "hora" in text: header_map[idx] = "HORA_NOCTURNA"
        elif "festiv" in text and "hora" in text: header_map[idx] = "HORA_FESTIVA"
        elif "domingo" in text and "hora" in text: header_map[idx] = "HORA_DOMINGO"
        elif "jornada" in text and ("fraccionada" in text or "partida" in text): header_map[idx] = "PLUS_JORNADA_FRACCIONADA"
        elif "perentoria" in text and "hora" in text: header_map[idx] = "HORA_PERENTORIA"
        
    tbody = table.find("tbody")
    if not tbody: return []
    
    current_group = "General"
    
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if not cells: continue
        
        # Heuristic to align data with headers.
        num_headers = len(cols)
        num_cells = len(cells)
        
        offset = num_cells - num_headers
        if offset < 0: offset = 0 
        
        # Identify Label Columns
        # 1. Columns strictly BEFORE the headers begin (Offset columns)
        # 2. Columns aligned with Headers that are NOT Concept Headers (Unmapped)
        
        label_texts = []
        
        # 1. Offset Cols
        for i in range(offset):
            txt = cells[i].get_text(strip=True)
            if txt: label_texts.append(txt)
            
        # 2. Unmapped Header Cols (e.g. if Header Row includes "Category")
        # Check columns from 'offset' onwards
        for i in range(offset, num_cells):
            header_idx = i - offset
            if header_idx < num_headers:
                if header_idx not in header_map:
                    # This column has a header but it's not a known concept. Treat as Label.
                    txt = cells[i].get_text(strip=True)
                    if txt: label_texts.append(txt)
            else:
                # cell index exceeds headers?? Should not happen if start at 0
                pass

        # Determine Group and Category from labels
        row_group = "General" 
        row_category = "Base"
        
        # Logic for EasyJet (Offset based) vs others
        # EasyJet: Offset 2 [Group, Cat] or Offset 1 [Cat]
        
        if len(label_texts) >= 2:
            # First is Group, Second is Category
            t0 = label_texts[0]
            t1 = label_texts[1]
            row_group = clean_group_name(t0)
            row_category = t1
            current_group = row_group
            
        elif len(label_texts) == 1:
            # Single Label
            t0 = label_texts[0]
            if current_group != "General":
                # Inherit Group
                row_group = current_group
                row_category = t0
            else:
                # No prior group context. Treating single label as Category (and Group=General)
                # This aligns with the "Level" logic.
                row_group = "General"
                row_category = t0
                
        else:
             # No labels found?
             row_group = current_group
             
        # Normalize
        row_category = row_category.strip(".").strip()
        
        for header_idx, concept in header_map.items():
            data_idx = header_idx + offset
            if data_idx < num_cells:
                val_text = cells[data_idx].get_text(strip=True)
                
                # Check for "Tabla s. 3" or similar refs -> Ignore
                if "tabla" in val_text.lower():
                    continue
                    
                amount = parse_spanish_number(val_text)
                
                if amount > 0:
                    results.append({
                        "company_id": company_id,
                        "year": year,
                        "group": row_group,
                        "level": row_category,
                        "concept": concept,
                        "amount": amount
                    })
    
    return results

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent / "data" / "xml"
    
    # 1. Iberia
    iberia_file = base_path / "iberia.xml"
    if iberia_file.exists():
        print("--- EXTRACTING IBERIA ---")
        try:
            iberia_data = extract_iberia_salaries(iberia_file)
            print(f"Iberia Records: {len(iberia_data)}")
        except Exception as e:
            logger.error(f"Error extracting Iberia: {e}")

    # 2. Groundforce
    groundforce_file = base_path / "groundforce.xml"
    if groundforce_file.exists():
        print("\n--- EXTRACTING GROUNDFORCE ---")
        try:
            gf_data = extract_groundforce_salaries(groundforce_file)
            print(f"Groundforce Records: {len(gf_data)}")
        except Exception as e:
            logger.error(f"Error extracting Groundforce: {e}")
            
    # 3. Menzies (Generic BOE)
    menzies_file = base_path / "menzies.xml"
    if menzies_file.exists():
        print("\n--- EXTRACTING MENZIES ---")
        try:
            menzies_data = extract_boe_salaries(menzies_file, "menzies")
            print(f"Menzies Records: {len(menzies_data)}")
            if len(menzies_data) > 0:
                print("Sample Menzies record:")
                print(json.dumps(menzies_data[0], indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error extracting Menzies: {e}")

    # 4. Swissport (Generic BOE)
    swiss_file = base_path / "swissport.xml"
    if swiss_file.exists():
        print("\n--- EXTRACTING SWISSPORT ---")
        try:
            swiss_data = extract_boe_salaries(swiss_file, "swissport")
            print(f"Swissport Records: {len(swiss_data)}")
            if len(swiss_data) > 0:
                print("Sample Swissport record:")
                print(json.dumps(swiss_data[0], indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error extracting Swissport: {e}")
            # traceback.print_exc()

    print(f"\nExtraction complete.")
