
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

load_dotenv()

from app.services.rag_engine import RagEngine

def test_search():
    try:
        # DB Setup
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ No DATABASE_URL in .env")
            return
            
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
            
        engine_db = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine_db)
        db = SessionLocal()

        rag = RagEngine()
        query = "vacaciones rotacion 6x3"
        company_slug = "azul-handling"
        
        print(f"Searching for '{query}' in '{company_slug}' (pgvector)...")
        results = rag.search(query, company_slug=company_slug, db=db, limit=10)
        
        print(f"Found {len(results)} chunks.")
        found = False
        for i, res in enumerate(results):
            content = res.get("content", "")
            snippet = content[:100].replace("\n", " ")
            print(f"\n--- Chunk {i+1} ---")
            print(f"Doc: {res.get('document_title')} | Ref: {res.get('article_ref')}")
            print(f"Text: {snippet}...")
            
            if "6x3" in content or "4x4" in content:
                print(">> ✅ MATCH '6x3'/'4x4' FOUND IN TEXT <<")
                found = True
        
        if not found:
            print("\n❌ '6x3' NOT found in any retrieved chunk.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
