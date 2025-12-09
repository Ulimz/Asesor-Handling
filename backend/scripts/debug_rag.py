import sys
import os

# Set up path to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine

def debug_search(query, company_slug):
    db = SessionLocal()
    from sqlalchemy import text
    try:
        # Check tables
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"📊 Tables in DB: {tables}")
        
        if 'legal_documents' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM legal_documents")).scalar()
            print(f"📄 Total Legal Documents: {count}")
            
            # Check for Estatuto
            estatuto = db.execute(text("SELECT title, category FROM legal_documents WHERE category = 'Estatuto' OR category = 'Jurisprudencia'")).fetchall()
            print(f"📜 Estatuto/Jurisprudence entries: {estatuto}")
            
        else:
            print("❌ CRITICAL: legal_documents table does not exist!")
            return

    except Exception as e:
        print(f"❌ DB Error: {e}")
        return

    print(f"🔎 DEBUG SEARCH: '{query}' for Company: '{company_slug}'")
    
    # Run the exact search logic
    results = rag_engine.search(query, company_slug=company_slug, db=db, limit=15)
    
    print(f"📊 Found {len(results)} chunks:")
    for i, res in enumerate(results):
        print(f"[{i+1}] Score: {res.get('score', 'N/A')} | DocID: {res.get('document_id')} | Ref: {res.get('article_ref')}")
        print(f"    Content Preview: {res['content'][:150]}...")
        print("-" * 50)
    
    db.close()

if __name__ == "__main__":
    # Test with a common company and the problematic query
    debug_search("Cuál es el descanso mínimo entre turnos", "iberia")
