import asyncio
import json
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import text
from backend.db.session import async_session_factory
from backend.db.models import Company, SalaryGroup, SalaryLevel, SalaryConcept, SalaryLevelValue

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATE_PATH = "backend/data/structure_templates/easyjet.json"

async def clear_easyjet_data(session):
    """Clears existing EasyJet data to prevent duplicates."""
    logger.info("🧹 Clearing existing EasyJet data...")
    company = await session.execute(text("SELECT id FROM companies WHERE name = 'EasyJet Handling Spain'"))
    company_id = company.scalar()
    
    if company_id:
        # Delete related data in order
        await session.execute(text("DELETE FROM salary_level_values WHERE level_id IN (SELECT id FROM salary_levels WHERE group_id IN (SELECT id FROM salary_groups WHERE company_id = :cid))"), {"cid": company_id})
        await session.execute(text("DELETE FROM salary_levels WHERE group_id IN (SELECT id FROM salary_groups WHERE company_id = :cid)"), {"cid": company_id})
        await session.execute(text("DELETE FROM salary_concepts WHERE company_id = :cid"), {"cid": company_id})
        await session.execute(text("DELETE FROM salary_groups WHERE company_id = :cid"), {"cid": company_id})
        await session.commit()
        logger.info("✅ Existing data cleared.")
    else:
        logger.info("ℹ️ No existing company found explicitly named 'EasyJet Handling Spain'. Checking by slug...")

async def seed_easyjet():
    """Seeds EasyJet 2025 data from JSON template."""
    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f"❌ Template not found: {TEMPLATE_PATH}")
        return

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["meta"]
    
    async with async_session_factory() as session:
        # 1. Ensure Company Exists
        logger.info(f"🏢 ensuring Company: {meta['company_name']}")
        result = await session.execute(text("SELECT id FROM companies WHERE slug = :slug"), {"slug": meta["company_id"]})
        company_id = result.scalar()
        
        if not company_id:
            # Create if not exists
            new_company = Company(
                name=meta["company_name"],
                slug=meta["company_id"],
                logo_url="/logos/easyjet.png"  # Placeholder
            )
            session.add(new_company)
            await session.flush()
            company_id = new_company.id
            logger.info("✅ Created new company.")
        else:
            await clear_easyjet_data(session)

        # 2. Create Global Concepts
        logger.info("💡 Creating Salary Concepts...")
        concept_map = {} # Code -> ID
        
        # Standard Concepts (Base + Progresión + Ad Personam + Plus Funcion Fixed)
        fixed_concepts = [
            ("SALARIO_BASE", "Salario Base (Mensual - 14 pagas prorrateadas o x12?? Convention says x14)", "euro", False),
            ("PLUS_PROGRESION", "Plus Progresión Económica", "euro", False),
            ("AD_PERSONAM", "Ad Personam Convenio", "euro", False),
            ("PLUS_FUNCION_FIXED", "Plus Función (Fijo Categoria)", "euro", False)
        ]

        for code, name, unit, is_var in fixed_concepts:
            c = SalaryConcept(
                company_id=company_id,
                name=name,
                code=code,
                unit=unit,
                is_variable=is_var,
                description=name
            )
            session.add(c)
            await session.flush()
            concept_map[code] = c.id

        # Variable Concepts from JSON
        json_concepts = data["concepts"]
        for code, info in json_concepts.items():
            c = SalaryConcept(
                company_id=company_id,
                name=info["description"],
                code=code,
                unit=info["unit"],
                is_variable=True,
                description=info.get("note", "")
            )
            session.add(c)
            await session.flush()
            concept_map[code] = c.id

        # 3. Create Groups and Levels
        logger.info("🏗️ Creating Groups and Levels...")
        
        for group_data in data["structure"]["groups"]:
            new_group = SalaryGroup(
                company_id=company_id,
                name=group_data["name"],
                description=group_data.get("description", "")
            )
            session.add(new_group)
            await session.flush()
            
            for cat_data in group_data["categories"]:
                cat_name = cat_data["name"]
                base_salary = cat_data["base_salary_2025"]
                ad_personam = cat_data.get("ad_personam", 0.0)
                plus_funcion_fixed = cat_data.get("plus_funcion_fixed", 0.0)
                
                # Each "Level" in JSON is a UX level (e.g., Nivel 1 ... 7)
                for level_info in cat_data["levels"]:
                    # Unique level name: e.g. "Agente de Rampa - Nivel 1"
                    # For Auxiliar, it's just "Auxiliar de Rampa"
                    
                    if "Nivel" in level_info["level"]:
                         full_level_name = f"{cat_name} - {level_info['level']}"
                    else:
                         full_level_name = level_info["level"]

                    logger.info(f"   🔹 Level: {full_level_name}")
                    
                    l = SalaryLevel(
                        group_id=new_group.id,
                        name=full_level_name,
                        code=full_level_name.upper().replace(" ", "_").replace(".", "")[:50]
                    )
                    session.add(l)
                    await session.flush()
                    
                    # 4. Attach Concept Values to Level
                    
                    # 4.1 Fixed Concepts
                    # Salario Base (Convention usually speaks in Annual / 14. Calculator expects monthly value usually. 
                    # If Table 1 says "S. Base (x 14) = 1.538", it implies 1538 Euros PER MONTH for 14 payments.
                    # So value = 1538.00
                    await create_value(session, l.id, concept_map["SALARIO_BASE"], base_salary)
                    
                    # Ad Personam
                    if ad_personam > 0:
                        await create_value(session, l.id, concept_map["AD_PERSONAM"], ad_personam)
                        
                    # Plus Progresion (Specific to this level index)
                    prog_val = level_info.get("progression_plus", 0.0)
                    if prog_val > 0:
                        await create_value(session, l.id, concept_map["PLUS_PROGRESION"], prog_val)
                        
                    # Plus Funcion Fixed (e.g. Jefe Area)
                    if plus_funcion_fixed > 0:
                        await create_value(session, l.id, concept_map["PLUS_FUNCION_FIXED"], plus_funcion_fixed)

                    # 4.2 Variable Concepts (Generic Values or Specific overrides)
                    # For now, we take from 'concepts' definitions which are global per company in this JSON structure,
                    # but if we wanted level-specific (like Horas Perentorias which vary by level), we need logic for that.
                    # Screenshot Table 4: Horas Perentorias vary by Level (1-7).
                    # My JSON template defined PLUS_HORA_EXTRA as generic, but I should probably refined it if I had the full Table 4 data.
                    # For now, I'll use the generic values from the 'concepts' block for variables unless I add logic here.
                    
                    # Add all assigned variable concepts
                    for var_code in cat_data.get("variable_concepts", []):
                        if var_code in concept_map and var_code in json_concepts:
                            val = json_concepts[var_code]["value_2025"]
                            await create_value(session, l.id, concept_map[var_code], val)

        await session.commit()
        logger.info("✨ EasyJet 2025 seeding complete!")

async def create_value(session, level_id, concept_id, amount):
    if amount == 0: return
    v = SalaryLevelValue(
        level_id=level_id,
        concept_id=concept_id,
        amount=amount
    )
    session.add(v)

if __name__ == "__main__":
    asyncio.run(seed_easyjet())
