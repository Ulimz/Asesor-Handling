#!/usr/bin/env python3
"""
Seed EasyJet 2025 from canonical template (compatible with current DB models)
"""
import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import SalaryTable, SalaryConceptDefinition

COMPANY_SLUG = "easyjet"
TEMPLATE_PATH = os.path.join(os.getcwd(), "backend", "data", "structure_templates", "easyjet.json")

def seed_easyjet():
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
        
        # Seed Salary Tables (Base Salary + automatic concepts)
        print("💰 Seeding Salary Tables...")
        tables_added = 0
        
        for group in data['structure']['groups']:
            group_name = group['name']
            for category in group['categories']:
                category_name = category['name']
                base_salary_annual = category['base_salary_2025']
                
                # For each level in this category
                for level in category.get('levels', []):
                    level_name = level['level']
                    
                    # Base Salary
                    entry = SalaryTable(
                        company_id=COMPANY_SLUG,
                        year=2025,
                        group=group_name,
                        level=f"{category_name} - {level_name}",
                        concept="SALARIO_BASE_ANUAL",
                        amount=base_salary_annual
                    )
                    db.add(entry)
                    tables_added += 1
                    
                    # Plus Progresión (if > 0)
                    if 'progression_plus' in level and level['progression_plus'] > 0:
                        entry = SalaryTable(
                            company_id=COMPANY_SLUG,
                            year=2025,
                            group=group_name,
                            level=f"{category_name} - {level_name}",
                            concept="PLUS_PROGRESION",
                            amount=level['progression_plus']
                        )
                        db.add(entry)
                        tables_added += 1
                    
                    # Ad Personam (if > 0)
                    if 'ad_personam' in category and category['ad_personam'] > 0:
                        entry = SalaryTable(
                            company_id=COMPANY_SLUG,
                            year=2025,
                            group=group_name,
                            level=f"{category_name} - {level_name}",
                            concept="AD_PERSONAM",
                            amount=category['ad_personam']
                        )
                        db.add(entry)
                        tables_added += 1
                    
                    # Plus Función Fixed (if > 0, only for Jefes de Área)
                    if 'plus_funcion_fixed' in category and category['plus_funcion_fixed'] > 0:
                        entry = SalaryTable(
                            company_id=COMPANY_SLUG,
                            year=2025,
                            group=group_name,
                            level=f"{category_name} - {level_name}",
                            concept="PLUS_FUNCION_CATEGORIA",
                            amount=category['plus_funcion_fixed']
                        )
                        db.add(entry)
                        tables_added += 1
        
        db.commit()
        print(f"   ✅ Seeded {tables_added} salary table entries")
        
        # Seed Concept Definitions (Tabla 2 - Variable concepts)
        print("🔧 Seeding Concept Definitions...")
        concepts_added = 0
        
        # Load concepts from JSON
        if 'concepts' in data:
            for code, info in data['concepts'].items():
                # Determine input_type based on unit
                if info.get('unit') == 'mes':
                    input_type = "checkbox"  # Monthly fixed amount
                elif info.get('unit') in ['hora', 'dia', 'asistencia']:
                    input_type = "number"  # Quantity-based
                else:
                    input_type = "checkbox"
                
                definition = SalaryConceptDefinition(
                    company_slug=COMPANY_SLUG,
                    code=code,
                    name=info['description'],
                    description=info.get('description', ''),
                    input_type=input_type,
                    default_price=info.get('value_2025', 0.0),
                    level_values=None  # EasyJet doesn't use level_values for Tabla 2
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
    seed_easyjet()
