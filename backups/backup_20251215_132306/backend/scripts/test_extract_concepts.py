import json
import os
import sys
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Setup Environment
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
root_dir = backend_dir.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

def load_data():
    file_path = backend_dir / "data" / "xml_parsed" / "iberia.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def extract_concepts(data):
    # Pre-filter text to avoid sending 1MB of text (Context window optimization)
    # We look for Articles containing keywords
    keywords = ["plus", "complemento", "retribución", "paga", "variable", "hora", "turnicidad", "quebranto"]
    
    relevant_text = []
    
    # Assuming 'data' is a list of articles or structured dict?
    # Based on iberia.json structure (usually list of objects or dict with 'children')
    # Let's blindly dump text if it's not too big, or iterate.
    # From previous view_file, iberia.json size is ~840KB. Gemini Flash context is 1M tokens? 
    # Actually Gemini 1.5 Pro/Flash has huge context. 
    # 840KB is roughly ~200k tokens max. We can send the WHOLE THING if structured as text strings.
    
    # Converting JSON structure to a simpler text representation
    full_text = json.dumps(data, ensure_ascii=False)
    
    if len(full_text) > 3000000: # Safety cap characters
         full_text = full_text[:3000000]
         print("Warning: Truncated text")

    print(f"Sending {len(full_text)} characters to Gemini...")

    prompt = """
    Analiza el siguiente Convenio Colectivo (en formato JSON) y extrae una lista estructurada de TODOS los Conceptos Retributivos Variables.
    Ignora el Salario Base fijo. Busca Pluses, Complementos, Pagas Extras, Horas, etc.

    Para cada concepto, devuelve un objeto JSON con:
    - name: Nombre del concepto (ej: "Plus Nocturnidad")
    - variable_code: Código corto único (ej: "PLUS_NOCT")
    - description: Breve descripción de cuándo aplica.
    - type: "variable_monthly" (cada mes varía, ej. horas) o "fixed_recurring" (fijo si cumples condición, ej. antiguedad) o "annual" (pagas extras)
    
    Devuelve SOLAMENTE un array JSON válido, sin markdown ni explicaciones adicionales.
    
    Ejemplo de salida:
    [
        {"name": "Plus Transporte", "variable_code": "PLUS_TRANS", "description": "Se abona por día efectivo de trabajo", "type": "variable_monthly"}
    ]

    Documento JSON:
    """ + full_text

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("Loading Iberia Data...")
    data = load_data()
    print("Extracting Concepts with AI...")
    result = extract_concepts(data)
    
    output_path = backend_dir / "data" / "extracted_concepts_iberia.json"
    print(f"Saving result to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print("Done!")
