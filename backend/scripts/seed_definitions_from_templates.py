
import json
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, Column, Integer, String, Float, Text, Boolean, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# Add backend to path to import models if needed, but we'll use inline for robustness
# against environment issues.
# Copying schema from seed_easyjet_root.py exactly.

Base = declarative_base()

class SalaryConceptDefinition(Base):
    __tablename__ = "salary_concept_definitions"
    id = Column(Integer, primary_key=True, index=True)
    company_slug = Column(String, index=True)
    code = Column(String, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    input_type = Column(String, default="number") # number, checkbox, select
    default_price = Column(Float, default=0.0)
    level_values = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

# Config
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("No DATABASE_URL set.")
    exit(1)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

TEMPLATES_DIR = Path("backend/data/structure_templates")

def derive_input_type(c_def):
    # logic to map template entry to frontend input_type
    if c_def.get("has_tiers"):
        return "select"
    if c_def.get("is_monthly") and not c_def.get("unit") in ["hora", "dia"]:
        return "checkbox"
    # Unit based
    unit = c_def.get("unit", "").lower()
    if unit in ["hora", "dia", "euro"]:
        return "number"
    
    # Fallback
    if c_def.get("input_type"):
        return c_def["input_type"]
        
    return "number"

def seed_definitions():
    if not TEMPLATES_DIR.exists():
        print(f"Templates dir not found: {TEMPLATES_DIR}")
        return

    session = SessionLocal()
    
    # Files to process
    files = list(TEMPLATES_DIR.glob("*.json"))
    print(f"Found {len(files)} templates.")
    
    for json_file in files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Identify Company Slug
            company_slug = data.get("meta", {}).get("company_id")
            if not company_slug:
                print(f"Skipping {json_file.name}: No company_id in meta")
                continue
                
            print(f"Processing {company_slug} from {json_file.name}...")
            
            # DELETE existing definitions for this company (Isolation Strategy!)
            deleted = session.query(SalaryConceptDefinition).filter(
                SalaryConceptDefinition.company_slug == company_slug
            ).delete()
            print(f"  - Cleared {deleted} existing concepts.")
            
            # Collect Concepts
            concepts = []
            if "concepts" in data:
                c_data = data["concepts"]
                
                # Case A: structured { fixed: [], variable: [] } (Azul, Sector)
                if isinstance(c_data, dict) and ("fixed" in c_data or "variable" in c_data):
                    for c in c_data.get("fixed", []):
                        c["_category"] = "fixed"
                        concepts.append(c)
                    for c in c_data.get("variable", []):
                        c["_category"] = "variable"
                        concepts.append(c)
                
                # Case B: pure dict { CODE: {}, CODE2: {} } (EasyJet)
                elif isinstance(c_data, dict):
                    for code, val in c_data.items():
                        val["id"] = code
                        # val["name"] might be missing -> usage description
                        if "name" not in val and "description" in val:
                            val["name"] = val["description"]
                        concepts.append(val)
                        
                # Case C: List (Legacy concepts.json) - Unlikely in templates but possible
                elif isinstance(c_data, list):
                    concepts = c_data
            
            # Insert
            for c in concepts:
                # Handle Tiers Expansion (e.g. Turnicidad -> Turnicidad_2, Turnicidad_3)
                if c.get("has_tiers") and c.get("tiers"):
                    for tier_key, tier_val in c["tiers"].items():
                        # Create suffix-based code
                        tier_code = f"{c['id']}_{tier_key}"
                        tier_name = f"{c['name']} ({tier_key.replace('_', ' ')})"
                        
                        input_type = "checkbox" # Tiers act as flags
                        
                        new_def = SalaryConceptDefinition(
                            company_slug=company_slug,
                            code=tier_code,
                            name=tier_name,
                            description=c.get("description", ""),
                            input_type=input_type,
                            default_price=float(tier_val),
                            level_values=None,
                            is_active=True
                        )
                        session.add(new_def)
                    # Skip adding the parent shell concept if it's purely a container
                    continue

                code = c["id"]
                name = c["name"]
                desc = c.get("description", "")
                inp_type = derive_input_type(c)
                
                # Default Price logic
                def_price = c.get("base_value_2025", 0.0)
                if c.get("level_values"):
                    # If we have level values, default price might be 0 or base
                    pass
                
                # Level Values directly from JSON
                lvl_vals = c.get("level_values")
                # Also store tiers in level_values or abuse it?
                # Ideally tiers go elsewhere, but for "select" input, frontend needs options.
                # If input_type=select, we assume tiers are standardized or hardcoded in frontend?
                # Or we put them in level_values?
                # Let's put tiers in level_values if present for 'select' types?
                if c.get("has_tiers") and c.get("tiers"):
                    lvl_vals = c["tiers"]
                
                new_def = SalaryConceptDefinition(
                    company_slug=company_slug,
                    code=code,
                    name=name,
                    description=desc,
                    input_type=inp_type,
                    default_price=def_price,
                    level_values=lvl_vals,
                    is_active=True
                )
                session.add(new_def)
            
            session.commit()
            print(f"  - Inserted {len(concepts)} concepts.")
            
            # Handle Derived Companies (Jet2, South, Norwegian, Clece, Groundforce?)
            # If this is 'convenio-sector', we verify if we need to propagate.
            # But earlier strict isolation says: Only touch MY company.
            # However, Jet2/South/etc don't have templates. They rely on Sector.
            # So I should copy explicitly here if I am processing convenio-sector.
            
            if company_slug == "convenio-sector":
                derived = ["jet2", "norwegian", "south", "clece"] 
                # Note: Groundforce might have its own template? Check.
                # Checking list of files: groundforce.json exists.
                
                for der in derived:
                    print(f"  -> Propagating to derived company: {der}")
                    # Clear derived
                    session.query(SalaryConceptDefinition).filter(
                        SalaryConceptDefinition.company_slug == der
                    ).delete()
                    
                    # Copy
                    for c in concepts:
                         # Same logic
                         code = c["id"]
                         name = c["name"]
                         desc = c.get("description", "")
                         inp_type = derive_input_type(c)
                         def_price = c.get("base_value_2025", 0.0)
                         lvl_vals = c.get("level_values")
                         if c.get("has_tiers") and c.get("tiers"):
                             lvl_vals = c["tiers"]

                         session.add(SalaryConceptDefinition(
                            company_slug=der,
                            code=code,
                            name=name,
                            description=desc,
                            input_type=inp_type,
                            default_price=def_price,
                            level_values=lvl_vals,
                            is_active=True
                        ))
                session.commit()

        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
            session.rollback()

    session.close()
    print("Done.")

if __name__ == "__main__":
    seed_definitions()
