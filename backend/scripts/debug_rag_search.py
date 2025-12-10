import asyncio
import os
import sys

sys.path.append("/app")

from app.services.rag_engine import RagEngine
from app.db.database import SessionLocal

async def debug():
    db = SessionLocal()
    try:
        engine = RagEngine()
        company_slug = "azul" 
        query = "Cuál es el descanso mínimo entre turnos?"
        
        print(f"Querying for: {query} (Company: {company_slug}) (Using DB Session)")
        
        # Pass db session to force PgVector path
        results = engine.search(query, company_slug, db=db, limit=5)
        
        # RagEngine.search is synchronous or async? 
        # Looking at code 'def search(...)', it seems synchronous unless it has 'async def'. 
        # Previous view showed 'def search'.
        
        print(f"Found {len(results)} chunks.")
        for r in results:
            print(f"--- Score: {r['score']} ---")
            print(r['content'][:200] + "...")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # If search is sync, we don't need asyncio.run for the search call itself, 
    # but let's keep it simple.
    debug_task = debug()
    if asyncio.iscoroutine(debug_task):
        asyncio.run(debug_task)
    else:
        # It seems I unwrapped it in main
        pass
