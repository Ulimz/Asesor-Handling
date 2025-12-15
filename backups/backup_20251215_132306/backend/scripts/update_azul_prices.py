import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup Environment
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Database Setup
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("DATABASE_URL not found")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Models
sys.path.append(str(backend_dir))
from app.db.models import SalaryConceptDefinition

def update_azul_prices():
    db = SessionLocal()
    
    json_path = backend_dir / "data" / "concepts" / "azul.json"
    if not json_path.exists():
        print("azul.json not found")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        concepts_data = json.load(f)
    
    updated_count = 0
    
    for item in concepts_data:
        if 'default_price' in item:
            concept = db.query(SalaryConceptDefinition).filter_by(
                company_slug="azul", 
                code=item['variable_code']
            ).first()
            
            if concept:
                print(f"Updating {concept.name} price to {item['default_price']}")
                concept.default_price = item['default_price']
                concept.name = item['name'] # Also update name (e.g. for Fraccionada details)
                updated_count += 1
            else:
                 print(f"Concept {item['variable_code']} not found in DB")

    db.commit()
    db.close()
    print(f"Updated {updated_count} prices.")

if __name__ == "__main__":
    update_azul_prices()
