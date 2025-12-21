import sys
import os
from dotenv import load_dotenv

# Load env
root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

sys.path.append(os.path.join(root_dir, 'backend'))

try:
    from app.services.rag_engine import rag_engine
    from app.prompts import IntentType
    from app.db.database import SessionLocal
except ImportError as e:
    with open("scripts/verify_result.txt", "w", encoding="utf-8") as f:
        f.write(f"IMPORT ERROR: {e}")
    sys.exit(1)

def run_verify():
    db = SessionLocal()
    query = "Resúmeme lo que dice el Artículo 999 del Convenio de Iberia sobre teletransporte." # Should fail
    
    try:
        results = rag_engine.search(query, company_slug="iberia", db=db, limit=1)
        answer = rag_engine.generate_answer(
            query=query,
            context_chunks=results,
            intent=IntentType.GENERAL,
            user_context={},
            structured_data="",
            db=db
        )
        
        with open("scripts/verify_result.txt", "w", encoding="utf-8") as f:
            f.write(f"QUERY: {query}\n")
            f.write(f"ANSWER: {answer}\n")
            if "No he encontrado esa información" in answer:
                f.write("RESULT: PASS\n")
            else:
                f.write("RESULT: FAIL (Fallback mismatch)\n")
                
    except Exception as e:
         with open("scripts/verify_result.txt", "w", encoding="utf-8") as f:
            f.write(f"EXECUTION ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_verify()
