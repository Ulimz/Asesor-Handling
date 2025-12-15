import json
import os
import time
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Setup Environment
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Try finding it in the docker env if running locally didn't work (though we will run this in docker)
    print("Error: GOOGLE_API_KEY not found in .env")
    # continue anyway, might be set in env vars

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

SOURCE_DIR = backend_dir / "data" / "xml_parsed"
OUTPUT_DIR = backend_dir / "data" / "concepts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_concepts_for_file(file_path):
    company_slug = file_path.stem # e.g., "easyjet"
    print(f"--- Processing {company_slug} ---")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to text string
    full_text = json.dumps(data, ensure_ascii=False)
    
    # Cap size to avoid errors (Gemini Flash has ~1M tokens, 3MB chars is roughly safe)
    if len(full_text) > 3000000:
         full_text = full_text[:3000000]
         print(f"Warning: Truncated {company_slug} text to 3MB chars")

    prompt = f"""
    Analiza el siguiente Convenio Colectivo de la empresa '{company_slug}' (en formato JSON) y extrae una lista estructurada de TODOS los Conceptos Retributivos Variables y Pluses Fijos Recurrentes.
    Ignora ÚNICAMENTE el "Salario Base" o "Percepción Mínima Fija".
    DEBES oscultar y extraer todos los complementos:
    - Pluses de Turnicidad / Disponibilidad (busca desgloses como "2 Turnos", "3 Turnos", etc. Si hay varios niveles, crea un concepto para cada uno o uno genérico si es más claro).
    - Plus de Jornada Irregular (a veces llamado "Fiji" o similar).
    - Plus FTP (Fijo Tiempo Parcial).
    - Pluses de "Ad Personam" o consolidables NO (ignóralos).
    - Horas Complementarias Especiales (Art. 19).
    - Cualquier otro complemento salarial (Nocturnidad, Festivos, Idiomas, Responsabilidad, Jefatura, etc.).

    IMPORTANTE:
    1. Presta ATENCIÓN ESPECIAL a conceptos de "Horas Complementarias" (e.g. "Horas Complementarias Especiales"), "Horas Perentorias" y similares.
    2. Si el texto menciona explícitamente cómo "se reflejará en la nómina" (ej: "se reflejará en la nómina como «HC Especial»"), USA ESE NOMBRE o abreviatura.
    3. Para "Plus Turnicidad" o similar, si hay niveles (2 turnos, 3 turnos, 4 turnos...), es preferible crear un concepto por cada nivel para que el usuario pueda seleccionarlo fácilmente, o indicar en la descripción los valores. MEJOR: Crea conceptos separados si tienen precios distintos (ej: "Plus Turnicidad (2 Turnos)", "Plus Turnicidad (3 Turnos)").

    Para cada concepto, devuelve un objeto JSON con:
    - name: Nombre del concepto (ej: "Plus Nocturnidad", "Plus Turnicidad 2 Turnos", "Plus FTP")
    - variable_code: Código corto único (ej: "PLUS_NOCT", "PLUS_TURNOS_2", "PLUS_FTP").
    - description: Breve descripción.
    - type: "variable_monthly" (cada mes varía, ej. horas) o "fixed_recurring" (fijo si cumples condición, ej. antiguedad) o "annual" (pagas extras)
    
    Devuelve SOLAMENTE un array JSON válido, sin markdown ni explicaciones adicionales, empezando por [ y terminando por ].
    
    Documento JSON:
    """ + full_text

    try:
        response = model.generate_content(prompt)
        result_text = response.text
        
        # Clean Markdown
        if "```" in result_text:
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
        # Validate JSON
        json.loads(result_text) # Will raise error if invalid
        
        # Save
        output_path = OUTPUT_DIR / f"{company_slug}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result_text)
            
        print(f"✅ Saved concepts for {company_slug}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {company_slug}: {e}")
        return False

def main():
    if not SOURCE_DIR.exists():
        print(f"Source directory {SOURCE_DIR} does not exist.")
        return

    files = list(SOURCE_DIR.glob("*.json"))
    print(f"Found {len(files)} files to process.")
    
    for file_path in files:
        if file_path.name == "estatuto.json":
            continue # Skip estatuto
            
        extract_concepts_for_file(file_path)
        time.sleep(2) # Avoid rate limits just in case

if __name__ == "__main__":
    main()
