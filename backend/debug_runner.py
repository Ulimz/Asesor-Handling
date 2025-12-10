import sys
import os

# Ensure we are in the root
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app.services.rag_engine import RagEngine
from sqlalchemy import text

def debug_search():
    db = SessionLocal()
    rag = RagEngine()
    
    query = "Cuál es el descanso mínimo entre turnos?"
    company_slug = "azul"
    
    print(f"🔎 DEBUGGING SEARCH")
    print(f"Query: {query}")
    print(f"Company: {company_slug}")
    print("-" * 50)
    
    # Check Estatuto
    print("\n[DB CHECK] Verifying 'Estatuto' document:")
    docs = db.execute(text("SELECT id, title, company FROM legal_documents WHERE title ILIKE '%Estatuto%'")).fetchall()
    for d in docs:
        print(f"  - ID: {d[0]}, Title: {d[1]}, Company: {d[2]}")

    # Search
    print(f"\n[SEARCH] Running rag_engine.search(limit=15)...")
    try:
        results = rag.search(query, company_slug=company_slug, db=db, limit=15)
        
        print(f"\nFound {len(results)} chunks:")
        found_estatuto = False
        for i, chunk in enumerate(results):
            doc_title = chunk.document.title
            company = chunk.document.company
            print(f"[{i+1}] {doc_title} ({company}) - {chunk.article_ref}")
            if "estatuto" in doc_title.lower() or "general" in str(company).lower():
                found_estatuto = True
                print("     ✅ MATCHES ESTATUTO/GENERAL")
                
        if not found_estatuto:
            print("\n❌ ISSUE: No Statute/General documents found in top 15!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    debug_search()
