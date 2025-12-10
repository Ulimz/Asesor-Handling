
import sys
import os
from pathlib import Path
import json

# Add backend directory to path so we can import from scripts
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

# We need to set the env var for the imported script if it loads dotenv at module level, 
# although the script does load it.
from scripts.extract_all_concepts import extract_concepts_for_file

def test_azul():
    azul_path = backend_dir / "data" / "xml_parsed" / "azul.json"
    print(f"Testing extraction for: {azul_path}")
    
    if not azul_path.exists():
        print("Error: azul.json not found")
        return

    success = extract_concepts_for_file(azul_path)
    
    if success:
        output_path = backend_dir / "data" / "concepts" / "azul.json"
        
        # Open and check content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\nExtraction Result:")
            print(content)
            
            # Check for key missing concepts
            missing = []
            if "HC_ESPECIAL" not in content and "Complementarias" not in content:
                missing.append("HC_ESPECIAL")
            if "PLUS_FTP" not in content and "FTP" not in content:
                missing.append("PLUS_FTP")
            if "PLUS_TURNICIDAD" not in content and "Turnos" not in content:
                missing.append("Turnicidad")
            if "FIJI" not in content and "Irregular" not in content:
                missing.append("Irregular")

            if not missing:
                print("\n✅ SUCCESS: All key concepts (HC, FTP, Turnos, Irregular) FOUND!")
            else:
                print(f"\n❌ Partia Failure. Missing: {missing}")
    else:
        print("Extraction failed function execution.")

if __name__ == "__main__":
    test_azul()
