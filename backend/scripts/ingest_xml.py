import os
import json
import re
import sys
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning

# Suppress XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Add script directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from boe_config import BOE_DOCUMENTS

def parse_boe_xml(doc_config):
    slug = doc_config['slug']
    boe_id = doc_config['boe_id']
    title = doc_config['title']
    
    # Docker path
    if os.path.exists("/app/data"):
        base_dir = "/app/data"
    else:
        # Local fallback
        base_dir = os.path.join(os.getcwd(), "backend", "data")
    
    xml_path = os.path.join(base_dir, "xml", f"{slug}.xml")
    
    # Ensure parsed directory exists
    parsed_dir = os.path.join(base_dir, "xml_parsed")
    os.makedirs(parsed_dir, exist_ok=True)
    output_path = os.path.join(parsed_dir, f"{slug}.json")
    
    if not os.path.exists(xml_path):
        print(f"⚠️ XML not found for {slug}: {xml_path}")
        return

    print(f"📖 Parsing {slug} ({boe_id})...")
    
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use html.parser which is robust for BOE's HTML-like XML
    soup = BeautifulSoup(content, 'html.parser')
    
    articles = []
    
    # Iterate over all tags in order to preserve flow
    # We look for H5 (headers), P (paragraphs/tables preamble), TABLE (tables)
    all_tags = soup.find_all(['h5', 'p', 'table'])
    
    current_article = {
        "article": "Preámbulo/Inicio",
        "content": ""
    }
    
    for element in all_tags:
        # Get clean text
        text = element.get_text(strip=True)
        
        # 1. Explicit Headers (h5)
        # BOE uses <h5 class="articulo">Artículo X. Title</h5>
        # But sometimes just <h5> without class or different class
        if element.name == 'h5':
            # Identify if it's a new section
            # Heuristic: <h5 class="articulo"> OR text starts with "Artículo", "ANEXO", "CAPÍTULO", "DISPOSICIÓN"
            is_new_section = False
            if 'articulo' in element.get('class', []):
                is_new_section = True
            elif any(x in text.upper() for x in ["ARTÍCULO", "ANEXO", "DISPOSICIÓN", "CAPÍTULO", "PREÁMBULO", "TÍTULO"]):
                is_new_section = True
            
            if is_new_section:
                if current_article["content"].strip():
                    articles.append(current_article)
                
                current_article = {
                    "article": text,
                    "content": text + "\n"
                }
                continue
        
        # 2. Paragraphs (p) - Check if they are actually Headers disguised as P
        if element.name == 'p':
            # Some XMLs put "ANEXO I" in a <p class="centro_negrita">
            is_header_p = False
            # Check length to avoid long paragraphs being treated as headers
            if len(text) < 150:
                upper_text = text.upper()
                # Must start with known keywords
                if upper_text.startswith("ARTÍCULO") or upper_text.startswith("ANEXO") or \
                   upper_text.startswith("DISPOSICIÓN") or upper_text.startswith("CAPÍTULO") or \
                   upper_text.startswith("TÍTULO"):
                    is_header_p = True
            
            if is_header_p:
                if current_article["content"].strip():
                    articles.append(current_article)
                
                current_article = {
                    "article": text,
                    "content": text + "\n"
                }
            else:
                # Normal paragraph content
                current_article["content"] += text + "\n"

        # 3. Tables
        if element.name == 'table':
            rows = element.find_all('tr')
            if len(rows) > 0:
                print(f"   [DEBUG] Found table with {len(rows)} rows in '{current_article['article'][:30]}...'")
            
            md_table = ""
            for row in rows:
                cols = row.find_all(['td', 'th'])
                # Simple markdown table: | col1 | col2 |
                row_text = "| " + " | ".join([c.get_text(strip=True) for c in cols]) + " |"
                md_table += row_text + "\n"
            
            # Add to content
            current_article["content"] += "\n" + md_table + "\n"

    # Append last article
    if current_article["content"].strip():
        articles.append(current_article)
    
    # Save JSON
    final_data = {
        "title": title,
        "company_slug": slug,
        "url": f"https://www.boe.es/buscar/doc.php?id={boe_id}",
        "articles": articles
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Parsed {len(articles)} sections for {slug}")

def batch_process():
    for doc in BOE_DOCUMENTS:
        try:
            parse_boe_xml(doc)
        except Exception as e:
            print(f"❌ Error parsing {doc['slug']}: {e}")

if __name__ == "__main__":
    batch_process()
