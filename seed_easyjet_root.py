import os
import sys
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker

# --- CONFIG ---
TEMPLATE_PATH = "backend/data/structure_templates/easyjet.json"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/asistente_handling")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_easyjet")

# --- DB SETUP ---
Base = declarative_base()

class SalaryTable(Base):
    __tablename__ = "salary_tables"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True) # Slug
    group = Column(String)
    level = Column(String)
    concept = Column(String)
    amount = Column(Float)
    variable_type = Column(String, nullable=True) # 'hour', 'day', 'month', etc.
    year = Column(Integer, default=2025)

# --- SEEDING LOGIC ---
def seed_easyjet():
    if not os.path.exists(TEMPLATE_PATH):
        logger.error(f"❌ Template not found: {TEMPLATE_PATH}")
        return

    logger.info(f"🔌 Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        company_slug = data["meta"]["company_id"]
        target_year = data["meta"]["convenio_year"]

        # 1. Clear Existing Data for Company + Year
        logger.info(f"🧹 Clearing data for {company_slug} ({target_year})...")
        session.query(SalaryTable).filter(
            SalaryTable.company_id == company_slug,
            SalaryTable.year == target_year
        ).delete()
        session.commit()

        # 2. Process Template
        logger.info("🌱 Seeding new data...")
        
        row_count = 0
        concepts_def = data["concepts"]

        for group in data["structure"]["groups"]:
            group_name = group["name"]
            
            for category in group["categories"]:
                cat_name = category["name"]
                base_salary = category["base_salary_2025"]
                ad_personam = category.get("ad_personam", 0.0)
                plus_funcion_fixed = category.get("plus_funcion_fixed", 0.0)
                
                # variable_concepts is now a Dict {Code: OverrideValue}
                variable_concepts_map = category.get("variable_concepts", {})

                for level_info in category["levels"]:
                    # Construct Level Name
                    raw_level = level_info["level"]
                    if "Nivel" in raw_level:
                        full_level_name = f"{cat_name} - {raw_level}"
                    else:
                        full_level_name = raw_level # e.g. "Auxiliar de Rampa"

                    # 2.1 Fixed Concepts
                    # SALARIO_BASE - ALWAYS ANNUALIZED (x14) for CalculatorService compatibility
                    add_row(session, company_slug, group_name, full_level_name, "SALARIO_BASE", base_salary * 14.0, None, target_year)
                    row_count += 1
                    
                    # AD_PERSONAM
                    if ad_personam > 0:
                        add_row(session, company_slug, group_name, full_level_name, "AD_PERSONAM", ad_personam, None, target_year)
                        row_count += 1
                        
                    # PLUS_PROGRESION
                    prog_val = level_info.get("progression_plus", 0.0)
                    if prog_val > 0:
                        add_row(session, company_slug, group_name, full_level_name, "PLUS_PROGRESION", prog_val, None, target_year)
                        row_count += 1

                    # PLUS_FUNCION_FIXED
                    if plus_funcion_fixed > 0:
                        add_row(session, company_slug, group_name, full_level_name, "PLUS_FUNCION_FIXED", plus_funcion_fixed, None, target_year)
                        row_count += 1
                        
                    # PLUS_HORA_PERENTORIA (Specific Level Price)
                    perentoria_val = level_info.get("perentoria", 0.0)
                    if perentoria_val > 0:
                         # Use unit from definition if available, else 'hora'
                         unit = concepts_def.get("PLUS_HORA_PERENTORIA", {}).get("unit", "hora")
                         v_type = map_unit(unit)
                         add_row(session, company_slug, group_name, full_level_name, "PLUS_HORA_PERENTORIA", perentoria_val, v_type, target_year)
                         row_count += 1

                    # 2.2 Variable Concepts (With Overrides)
                    for var_code, override_val in variable_concepts_map.items():
                        if var_code in concepts_def:
                            c_def = concepts_def[var_code]
                            unit = c_def["unit"]
                            v_type = map_unit(unit)
                            
                            # Use Override if present, else Default
                            val = override_val if override_val is not None else c_def["value_2025"]
                            
                            if val > 0:
                                add_row(session, company_slug, group_name, full_level_name, var_code, val, v_type, target_year)
                                row_count += 1

        session.commit()
        logger.info(f"✅ Successfully seeded {row_count} rows for EasyJet 2025.")

    except Exception as e:
        logger.error(f"💥 Error seeding: {e}")
        session.rollback()
    finally:
        session.close()

def map_unit(unit):
    if unit == "hora": return "hour"
    if unit == "dia": return "day"
    if unit == "mes": return "month"
    return "unit"

def add_row(session, cid, group, level, concept, amount, v_type, year):
    r = SalaryTable(
        company_id=cid,
        group=group,
        level=level,
        concept=concept,
        amount=amount,
        variable_type=v_type,
        year=year
    )
    session.add(r)

if __name__ == "__main__":
    seed_easyjet()
