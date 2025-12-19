
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("No DATABASE_URL set.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def migrate_slugs():
    with engine.connect() as conn:
        print("Starting Slug Migration...")
        
        # 1. Azul -> Azul Handling
        print("Fixing Azul...")
        conn.execute(text("UPDATE salary_concept_definitions SET company_slug = 'azul-handling' WHERE company_slug = 'azul'"))
        
        # 2. General -> Convenio Sector
        print("Fixing General -> Convenio Sector...")
        conn.execute(text("UPDATE salary_concept_definitions SET company_slug = 'convenio-sector' WHERE company_slug = 'general'"))
        
        # 3. Duplicate Convenio Sector -> Jet2, Norwegian, South, Clece
        # If they don't exist, we copy definitions from 'convenio-sector'
        # Listing target generic companies
        targets = ['jet2', 'norwegian', 'south', 'clece']
        
        # Check if we have 'convenio-sector' concepts (we just renamed them)
        res = conn.execute(text("SELECT * FROM salary_concept_definitions WHERE company_slug = 'convenio-sector'"))
        concepts = res.fetchall()
        
        if not concepts:
            print("Warning: No 'convenio-sector' concepts found!")
        else:
            print(f"Found {len(concepts)} Convenio Sector concepts. Copying to targets: {targets}")
            
            # Get columns to insert dynamically or explicitly
            # Explicit is safer.
            # id ignored (auto), company_slug changed, others copied.
            
            for target in targets:
                # Check if target already has concepts
                count = conn.execute(text(f"SELECT COUNT(*) FROM salary_concept_definitions WHERE company_slug = '{target}'")).scalar()
                if count > 0:
                    print(f"Skipping {target} (Already has {count} concepts)")
                    continue
                    
                print(f"Copying to {target}...")
                conn.execute(text(f"""
                    INSERT INTO salary_concept_definitions 
                    (company_slug, code, name, description, input_type, default_price, level_values, is_active)
                    SELECT 
                        '{target}', code, name, description, input_type, default_price, level_values, is_active
                    FROM salary_concept_definitions
                    WHERE company_slug = 'convenio-sector'
                """))
        
        conn.commit()
        print("✅ Migration Complete.")

if __name__ == "__main__":
    migrate_slugs()
