import sys
import os
import json
from dotenv import load_dotenv

# Force UTF-8 stdout
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load env
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

sys.path.append(os.path.join(root_dir, 'backend'))

try:
    from app.services.auditor_service import auditor_service
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)

def run_auditor_tests():
    print("🕵️ TESTING AUDITOR SERVICE")
    print("=========================")

    # CASE 1: GOOD RESPONSE
    query = "Cuantos dias de vacaciones tengo?"
    context = "Art. 20 Convenio: El trabajador tendrá derecho a 22 días laborables de vacaciones."
    response = "Según el Artículo 20 del Convenio, tienes derecho a 22 días laborables de vacaciones."
    
    print("\nTEST 1: Valid Content -> Should PASS")
    result = auditor_service.audit_response(query, response, context)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result.get("aprobado"):
        print("✅ PASSED")
    else:
        print("❌ FAILED (False Alarm)")

    # CASE 2: BAD RESPONSE (HALLUCINATION)
    query = "Tengo derecho a prima de Navidad?"
    context = "El convenio no establece primas extraordinarias salvo las pagas de Junio y Diciembre."
    response = "Sí, el Artículo 50 establece una Prima de Navidad de 500 euros para todos."
    
    print("\nTEST 2: Hallucination -> Should FAIL")
    result = auditor_service.audit_response(query, response, context)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if not result.get("aprobado"):
        print("✅ PASSED (Caught Hallucination)")
    else:
        print("❌ FAILED (Missed Hallucination)")

if __name__ == "__main__":
    run_auditor_tests()
