#!/usr/bin/env python3
"""
Seed Convenio Sector (General) from canonical template
"""
import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryTable, SalaryConceptDefinition

COMPANY_SLUG = "convenio-sector"
TEMPLATE_PATH = os.path.join(os.getcwd(), "backend", "data", "structure_templates", "convenio_sector.json")

def seed_sector():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print(f"🧹 Cleaning existing data for {COMPANY_SLUG}...")
        db.query(SalaryConceptDefinition).filter(SalaryConceptDefinition.company_slug == COMPANY_SLUG).delete()
        db.query(SalaryTable).filter(SalaryTable.company_id == COMPANY_SLUG).delete()
        db.commit()
        
        # Load template
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"📖 Loading template from {TEMPLATE_PATH}...")
        
        # Seed Salary Tables (Base Salary)
        print("💰 Seeding Salary Tables...")
        base_concept = next((c for c in data["concepts"]["fixed"] if c["id"] == "SALARIO_BASE_ANUAL"), None)
        if base_concept and "level_values" in base_concept:
            for group, levels in base_concept["level_values"].items():
                for level, amount in levels.items():
                    entry = SalaryTable(
                        company_id=COMPANY_SLUG,
                        year=2025,
                        group=group,
                        level=level,
                        concept="SALARIO_BASE_ANUAL",
                        amount=amount
                    )
                    db.add(entry)
            db.commit()
            print(f"   ✅ Seeded {len(base_concept['level_values'])} groups with levels")
        
        # Seed Concept Definitions
        print("🔧 Seeding Concept Definitions...")
        concepts_added = 0
        
        for concept in data["concepts"]["fixed"] + data["concepts"]["variable"]:
            code = concept["id"]
            
            # Handle tiered concepts (e.g., PLUS_TURNICIDAD)
            if concept.get("has_tiers") and "tiers" in concept:
                for tier_key, tier_value in concept["tiers"].items():
                    tier_code = f"{code}_{tier_key}"
                    tier_name = f"{concept['name']} ({tier_key.replace('_', ' ').title()})"
                    
                    definition = SalaryConceptDefinition(
                        company_slug=COMPANY_SLUG,
                        code=tier_code,
                        name=tier_name,
                        description=concept.get("description", ""),
                        input_type="checkbox",
                        default_price=tier_value,
                        level_values=None
                    )
                    db.add(definition)
                    concepts_added += 1
            else:
                # Regular concept
                # Determine input_type based on unit
                if concept.get("unit") == "euro":
                    input_type = "currency"  # Input IS the amount (e.g., Garantía Personal)
                elif concept.get("unit"):
                    input_type = "number"  # Input is a quantity (hours, days)
                else:
                    input_type = "checkbox"  # Boolean flag
                
                definition = SalaryConceptDefinition(
                    company_slug=COMPANY_SLUG,
                    code=code,
                    name=concept["name"],
                    description=concept.get("description", ""),
                    input_type=input_type,
                    default_price=concept.get("base_value_2025", 0.0),
                    level_values=concept.get("level_values")
                )
                db.add(definition)
                concepts_added += 1
        
        db.commit()
        print(f"   ✅ Seeded {concepts_added} concept definitions")
        
        print(f"\n✅ Successfully seeded {COMPANY_SLUG}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sector()
