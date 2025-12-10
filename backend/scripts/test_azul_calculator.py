import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add backend directory to path
# Inside docker, app is at /app
# This script is at /app/scripts/test_azul_calculator.py
# So parent is /app/scripts, grandparent is /app.
# Python path should already include /app in docker but let's be safe.
sys.path.append("/app")

# Load Env (optional in docker as env vars are injected, but harmless)
# load_dotenv("/app/.env") 

from app.db.database import SessionLocal
from app.services.calculator_service import CalculatorService
from app.schemas.salary import CalculationRequest
from app.db.models import SalaryConceptDefinition

def test_azul_calculation():
    db = SessionLocal()
    service = CalculatorService(db)

    print("--- Testing Azul Handling Calculator (2025 Tables) ---\n")

    # TEST CASE: Serv. Auxiliares, Nivel 2
    # Table 2025 Data:
    # Base Annual: 21,850.75 -> Monthly (14 pagas) = 1560.767...
    # Hora Extra: 19.14
    # Hora Perentoria: 22.34
    
    req = CalculationRequest(
        company_slug="azul",
        user_group="Serv. Auxiliares",
        user_level="Nivel 2",
        contract_percentage=100.0,
        payments=14,
        contract_type="indefinido",
        dynamic_variables={
            "HORA_EXTRA": 10.0,          # 191.40
            "HORA_PERENT": 5.0,          # 111.70
            "PLUS_TURNOS_3": 1.0,        # Fixed
            "HC_ESPECIAL": 0.0
        }
    )

    try:
        response = service.calculate_smart_salary(req)
        
        print(f"Profile: {req.user_group} - {req.user_level}")
        print(f"Base Monthly (Expected ~1560.77): {response.base_salary_monthly:.2f}")
        print(f"Total Variable: {response.variable_salary:.2f}")
        print(f"Gross Monthly: {response.gross_monthly_total:.2f}")
        print("\n--- Breakdown ---")
        for item in response.breakdown:
            print(f"- {item.name}: {item.amount:.2f} ({item.type})")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_azul_calculation()
