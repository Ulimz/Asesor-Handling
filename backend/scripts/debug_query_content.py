
import sys
import os
import asyncio
from dotenv import load_dotenv

# Load env vars from backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_engine import rag_engine
from app.db.database import SessionLocal

def test_query():
    query = "Cuál es el descanso mínimo entre turnos?"
    # Try with a specific company if known, otherwise None (General)
    # The user might be using a specific company, let's try 'azul' as per previous context, and 'iberia'
    companies = ['azul', 'iberia', None] 
    
    db = SessionLocal()
    try:
        for company in companies:
            print(f"\n\n{'='*50}")
            print(f"TESTING COMPANY: {company}")
            print(f"{'='*50}")
            
            # 1. Search
            print(f"[SEARCH] Rewriting query...")
            rewritten_query = rag_engine.rewrite_query(query, [])
            print(f"[SEARCH] Query rewritten to: {rewritten_query}")

            print(f"[SEARCH] Running rag_engine.search(limit=25)...")
            results = rag_engine.search(rewritten_query, company_slug=company, db=db, limit=25)
            print(f"Found {len(results)} chunks.")
            
            for i, res in enumerate(results):
                print(f"\n--- Result {i+1} ---", flush=True)
                title = res.get('document_title', 'Unknown')
                ref = res.get('article_ref', 'Unknown')
                print(f"Source: {title} ({ref})", flush=True)
                
                content = res.get('content', '')
                print(f"Content (repr): {repr(content[:100])}...", flush=True)
                
                # Check key terms
                if "12" in content or "doce" in content or "descanso" in content.lower():
                     print("   [POTENTIAL ANSWER FOUND IN TEXT]", flush=True)

                # SPECIFIC DEBUG: Check if this is the correct Estatuto article
                if "estatuto" in title.lower() and "34" in ref:
                    print(f"   ⭐⭐⭐ FOUND ESTATUTO ART 34 at Rank {i+1} ⭐⭐⭐", flush=True)

            
            # 2. Generate Answer (Mocking the call if needed, or calling real if possible)
            # Since generating answer requires calling Gemini and we want to see the CONTEXT passed, 
            # we can infer what the LLM sees from the search results above.
            
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
