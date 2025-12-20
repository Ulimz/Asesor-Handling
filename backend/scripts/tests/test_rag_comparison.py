
import sys
import os
import logging
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.db.database import SessionLocal
from app.services.calculator_service import CalculatorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_salary_table():
    db = SessionLocal()
    service = CalculatorService(db)
    
    company_slug = "azul-handling"
    group = "Servicios Auxiliares"
    
    print(f"Testing Salary Table Generation for: {company_slug} - {group}")
    
    try:
        # Check if we can get the markdown table
        # Note: The method name in CalculatorService might need verification if I haven't created it yet.
        # But based on the plan, it should be `get_group_salary_table_markdown`
        
        # Let's check if the method exists in the service class first?
        # Or just try to call it.
        
        if not hasattr(service, 'get_group_salary_table_markdown'):
             print("❌ Method 'get_group_salary_table_markdown' not found in CalculatorService!")
             return

        markdown_table = service.get_group_salary_table_markdown(company_slug, group)
        
        print("\n--- Generated Markdown Table ---\n")
        print(markdown_table)
        print("\n--------------------------------\n")
        
        # Validation
        if "Nivel 1" in markdown_table and "Nivel 3" in markdown_table:
             print("✅ Success: Table contains multiple levels.")
        else:
             print("❌ Failure: Table seems to miss levels.")
             
        if "SALARIO_BASE" in markdown_table or "Salario Base" in markdown_table:
             print("✅ Success: Table contains Salario Base.")
        else:
             print("❌ Failure: Table misses Salario Base.")

    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_rag_salary_table()
