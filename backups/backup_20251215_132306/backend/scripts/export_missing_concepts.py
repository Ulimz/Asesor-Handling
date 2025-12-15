import os
import sys
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 1. SETUP LOCAL CONNECTION
# Skip load_dotenv to avoid encoding issues with files
# load_dotenv()

# Hardcoded local connection using retrieved credentials
# User: usuario, Pass: 12345, Port: 5440 (Alternate process check)
db_url = "postgresql://usuario:12345@localhost:5440/asistentehandling"

# Clean simple print
print(f"Stdout Encoding: {sys.stdout.encoding}")
print("Connecting to LOCAL DB...")

# Enforce UTF8 client encoding
engine = create_engine(
    db_url, 
    connect_args={'client_encoding': 'utf8'}
)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def export_custom_concepts():
    print("Starting Query...")
    try:
        # Search for RCO, ARCO, or Fixed concepts
        # Use simple select first to avoid complex decoding if query fails
        query = text("""
            SELECT company_slug, name, code, description, input_type, default_price 
            FROM salary_concept_definitions 
            WHERE code ILIKE '%RCO%' 
               OR code ILIKE '%ARCO%' 
               OR code ILIKE '%FIJO%'
               OR name ILIKE '%RCO%'
               OR name ILIKE '%ARCO%'
        """)
        
        results = session.execute(query).fetchall()
        print(f"Query returned {len(results)} rows.")
        
        exported_data = []
        for r in results:
            try:
                row_dict = {
                    "company_slug": r[0],
                    "name": r[1],
                    "variable_code": r[2],
                    "description": r[3],
                    "type": r[4],
                    "default_price": float(r[5]) if r[5] else 0.0
                }
                exported_data.append(row_dict)
            except Exception as row_error:
                print(f"Skipping row due to error: {row_error}")
            
        print(f"📦 Found {len(exported_data)} custom concepts.")
        
        output_file = "backend/data/concepts/manual_migration.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(exported_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Exported to {output_file}")
        
    except Exception as e:
        print(f"❌ Critical Error in Export: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    export_custom_concepts()
