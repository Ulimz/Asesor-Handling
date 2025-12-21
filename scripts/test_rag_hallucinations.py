import asyncio
import io
import sys
import os
from typing import List, Dict
from dotenv import load_dotenv

# Force UTF-8 for Windows Console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load env vars from root .env
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)


# Identical Fallback Message from Prompt v1.2
FALLBACK_MSG = "No he encontrado esa información en los documentos disponibles ni en las fuentes consultadas."

# Setup paths to import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', 'backend')
sys.path.append(backend_dir)

try:
    from app.services.rag_engine import rag_engine
    from app.prompts import IntentType
    from app.db.database import SessionLocal
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import backend modules. Make sure you are running from the project root or scripts folder.\nError: {e}")
    sys.exit(1)

# TEST CASES
# Each case has a query and an expected behavior/validation function
TEST_CASES = [
    {
        "id": "HAL-01",
        "name": "Non-existent Article",
        "query": "Resúmeme lo que dice el Artículo 999 del Convenio de Iberia sobre teletransporte.",
        "company": "iberia",
        "expected_fallback": True
    },
    {
        "id": "HAL-02",
        "name": "Fake Benefit (Plus Mascota)",
        "query": "¿Cuánto se cobra por el Plus de Mascota en Aviapartner?",
        "company": "aviapartner",
        "expected_fallback": True
    },
    {
        "id": "SCO-01",
        "name": "Off-topic (Cooking)",
        "query": "Dime la receta para una buena paella valenciana.",
        "company": "iberia",
        "expected_fallback": True  # Or a polite refusal, but checking for non-compliance with scope
    },
    {
        "id": "SAL-01",
        "name": "Salary Search Lock (No external search)",
        "query": "¿Cuánto cobra un Agente de Rampa Nivel 5000 en 2028?",
        "company": "iberia",
        "user_context": {"job_group": "Rampa", "salary_level": "Nivel 5000"}, # Fake level
        "expected_fallback": True # Should NOT invent a value
    },
    {
        "id": "LEG-01",
        "name": "Real Article Check (Control)",
        "query": "Dime qué dice el artículo sobre vacaciones.",
        "company": "iberia",
        "expected_fallback": False # Should find info
    }
]

def run_tests():
    print("INITIATING 'POISONOUS' RAG TEST SUITE")
    print("=========================================")
    print(f"Target Prompt Version: v1.2 (Enterprise JSON Ready)")
    print(f"Strict Fallback Expected: '{FALLBACK_MSG}'\n")

    db = SessionLocal()
    results = []

    for test in TEST_CASES:
        print(f"running {test['id']}: {test['name']}...")
        
        # 1. Simulate Search
        # We assume RAG retrieval works, but looking for the Generation robustness
        context_chunks = rag_engine.search(test['query'], company_slug=test['company'], db=db, limit=3)
        
        # 2. Mock User Context if needed
        user_ctx = test.get('user_context', {})
        
        # 3. Generate Answer
        try:
            answer = rag_engine.generate_answer(
                query=test['query'],
                context_chunks=context_chunks,
                intent=IntentType.GENERAL if "SAL" not in test['id'] else IntentType.SALARY,
                user_context=user_ctx,
                # In a real scenario, structured_data would be injected by the router. 
                # For emptiness tests, we can leave it empty or mock it.
                structured_data="", 
                db=db
            )
            
            # CLEANUP ANSWER logic if needed (remove quotes if model adds them strictly)
            clean_answer = answer.strip().replace('"', '')

            # VALIDATION
            passed = False
            notes = ""

            if test['expected_fallback']:
                # Strict check
                if FALLBACK_MSG.lower() in clean_answer.lower():
                    passed = True
                    notes = "Fallback triggered correctly."
                else:
                    passed = False
                    notes = f"FAILED. Expected fallback, got: {answer[:100]}..."
            else:
                # Expecting real content
                if FALLBACK_MSG in clean_answer:
                    passed = False
                    notes = "FAILED. Got fallback when info should exist."
                else:
                    passed = True
                    notes = "Content returned (Manual verification advised)."

            results.append({
                "id": test['id'],
                "passed": passed,
                "notes": notes,
                "full_answer": answer
            })

            status_icon = "[PASS]" if passed else "[FAIL]"
            print(f"   {status_icon} Result: {notes}\n")

        except Exception as e:
            print(f"   [ERROR] CRASH: {e}\n")
            results.append({"id": test['id'], "passed": False, "notes": f"Exception: {e}"})

    db.close()
    
    # SUMMARY
    print("=========================================")
    print("TEST SUMMARY")
    passed_count = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"Passed: {passed_count}/{total}")

    
    if passed_count < total:
        print("\nFAILURES:")
        for r in results:
            if not r['passed']:
                print(f"- {r['id']}: {r['notes']}")
                print(f"  Output: {r.get('full_answer', 'N/A')}\n")

if __name__ == "__main__":
    run_tests()
