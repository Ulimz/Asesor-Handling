
import os
import json
import re
from pypdf import PdfReader

# Handle paths relative to project root (where script is executed from)
# If running in Docker, /app is the root (which is backend). If running locally from root, it might be ./backend
if os.path.exists(os.path.join(os.getcwd(), "backend")):
    DATA_DIR = os.path.join(os.getcwd(), "backend", "data", "real")
    OUTPUT_DIR = os.path.join(os.getcwd(), "backend", "data")
else:
    # Docker environment (or running from inside backend)
    DATA_DIR = os.path.join(os.getcwd(), "data", "real")
    OUTPUT_DIR = os.path.join(os.getcwd(), "data")

def extract_articles(text):
    # This regex attempts to find "Artículo X." patterns
    # It identifies the start of an article and captures until the next one starts
    # Adjust regex based on specific PDF formatting if needed
    # Improved regex to catch "Artículo", "ARTICULO", "Art.", "Articulo", "ANEXO", "DISPOSICIÓN", "PREÁMBULO", "CAPÍTULO"
    # Matches "Artículo 1", "ANEXO I", "Disposición Adicional", etc.
    pattern = r"((?:Art[íi]culo|Art\.|ANEXO|DISPOSICI[ÓO]N|PREÁMBULO|CAP[ÍI]TULO)\s+.*?(?=\s|$))(?=(?:Art[íi]culo|Art\.|ANEXO|DISPOSICI[ÓO]N|PREÁMBULO|CAP[ÍI]TULO)\s+.*?(?=\s|$)|$)"
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
    
    # Initialize variables for article extraction
    articles = []
    current_article = None
    current_content = []
    
    # Define the article pattern for line-by-line processing
    article_pattern = re.compile(r"(Art[íi]culo|Art\.|ANEXO|DISPOSICI[ÓO]N|PREÁMBULO|CAP[ÍI]TULO)\s+.*", re.IGNORECASE)

    full_text_buffer = [] # Buffer to store all processed lines for potential later use or debugging

    for page in reader.pages:
        page_text = page.extract_text()
        if not page_text:
            continue
            
        lines = page_text.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Pre-cleaning for each line
            stripped = stripped.replace("BOLETÍN OFICIAL DEL ESTADO", "").strip()

            if not stripped: # Skip empty lines after stripping
                continue

            # Skip TOC lines (ending in dots and number, e.g. "..... 33")
            if "....." in stripped and stripped[-1].isdigit():
                continue
                
            match = article_pattern.match(stripped)
            if match:
                # Save previous article if it exists
                if current_article:
                    articles.append({
                        "article": current_article,
                        "content": "\n".join(current_content).strip()
                    })
                current_article = match.group(0) # e.g. "Artículo 1."
                current_content = [stripped]
            elif current_article:
                current_content.append(stripped)
            
            full_text_buffer.append(stripped) # Keep track of all processed lines

    # Save the last article after the loop finishes
    if current_article:
        articles.append({
            "article": current_article,
            "content": "\n".join(current_content).strip()
        })

    # If no articles were found using the line-by-line method,
    # fall back to the original `extract_articles` function on the full text.
    # This ensures compatibility and robustness.
    if not articles:
        print("No articles found with line-by-line parsing. Attempting full text extraction.")
        # Reconstruct full text from buffer for the original extract_articles function
        full_text_for_fallback = "\n".join(full_text_buffer)
        articles = extract_articles(full_text_for_fallback)
    
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
