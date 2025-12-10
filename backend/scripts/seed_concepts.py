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
    user = os.getenv('POSTGRES_USER', 'usuario')
    password = os.getenv('POSTGRES_PASSWORD', 'password') # Fallback to standard dev password
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'asistentehandling')
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Models (Need to append path to find 'app')
sys.path.append(str(backend_dir))
from app.db.models import Base, SalaryConceptDefinition

def seed_concepts():
    db = SessionLocal()
    
    # 1. Create Tables if not exist (quick fix for dev)
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Iterate JSONs in /data/concepts
    concepts_dir = backend_dir / "data" / "concepts"
    if not concepts_dir.exists():
        print(f"Error: {concepts_dir} not found. Run batch extraction script first.")
        return

    json_files = list(concepts_dir.glob("*.json"))
    print(f"Found {len(json_files)} concept files to seed.")

    total_added = 0
    for json_path in json_files:
        company_slug = json_path.stem # aviapartner, iberia, etc.
        print(f"Seeding {company_slug}...")

        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                concepts_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {json_path.name} (invalid JSON)")
                continue
        
        for item in concepts_data:
            # Check if exists
            exists = db.query(SalaryConceptDefinition).filter_by(
                company_slug=company_slug, 
                code=item['variable_code']
            ).first()
            
            if not exists:
                # Use default price logic or random for mock
                default_price = 0.0
                code_lower = item['variable_code'].lower()
                
                if "noct" in code_lower: default_price = 12.0
                elif "extra" in code_lower: default_price = 20.0
                elif "fest" in code_lower: default_price = 30.0
                elif "dieta" in code_lower: default_price = 45.0
                elif "transp" in code_lower: default_price = 5.0
                
                concept = SalaryConceptDefinition(
                    company_slug=company_slug,
                    name=item['name'],
                    code=item['variable_code'],
                    description=item['description'],
                    input_type=item.get('type', 'variable_monthly'),
                    default_price=default_price
                )
                db.add(concept)
                total_added += 1
        
        db.commit()

    print(f"✅ Successfully seeded a total of {total_added} new concepts across all companies.")
    db.close()

if __name__ == "__main__":
    seed_concepts()
