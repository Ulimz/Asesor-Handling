
import os
import json
import re
from pypdf import PdfReader

DATA_DIR = "/app/data/real"
OUTPUT_DIR = "/app/data"

def extract_articles(text):
    # This regex attempts to find "Artículo X." patterns
    # It identifies the start of an article and captures until the next one starts
    # Adjust regex based on specific PDF formatting if needed
    # Improved regex to catch "Artículo", "ARTICULO", "Art.", "Articulo" with numbers
    # Matches "Artículo 1", "Articulo 1.", "ARTÍCULO 1º", "Art. 1"
    pattern = r"((?:Art[íi]culo|Art\.)\s+\d+.*?)(?=(?:Art[íi]culo|Art\.)\s+\d+|$)"
    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
    
    articles = []
    for match in matches:
        full_text = match.group(1).strip()
        # Clean up whitespace
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # Extract title (e.g., "Artículo 1. Ámbito.")
        title_match = re.match(r"((?:Art[íi]culo|Art\.)\s+\d+.*?)(?=\s)", full_text, re.IGNORECASE)
        article_title = title_match.group(0) if title_match else "Artículo Desconocido"
        
        articles.append({
            "article": article_title,
            "content": full_text
        })
    return articles

def parse_pdf(filename, company_name, url):
    pdf_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Processing {filename}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Pre-cleaning
    text = text.replace("BOLETÍN OFICIAL DEL ESTADO", "")
    
    articles = extract_articles(text)
    
    output_data = {
        "title": f"Convenio Colectivo {company_name}",
        "url": url,
        "articles": articles
    }
    
    output_filename = filename.replace(".pdf", ".json").lower()
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(articles)} articles to {output_filename}")

if __name__ == "__main__":
    # Ensure raw data dir exists
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} does not exist inside container.")
        exit(1)

    # Specific configurations
    # Dynamic discovery of PDFs
    import glob
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {DATA_DIR}")
        exit(0)

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        company = filename.replace(".pdf", "").replace("_Convenio", "")
        # Dummy URL - Real URL would require a map
        url = "https://www.boe.es/" 
        parse_pdf(filename, company, url)
