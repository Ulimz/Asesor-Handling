import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_path)
load_dotenv(os.path.join(backend_path, '.env'))

# Ensure DATABASE_URL is set
if os.getenv("CLOUD_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.getenv("CLOUD_DATABASE_URL")
if os.getenv("DATABASE_URL", "").startswith("postgres://"):
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)

from app.services.rag_engine import rag_engine
from app.db.database import SessionLocal

print(f"✅ Loaded Environment. Target DB: {os.getenv('DATABASE_URL')[:30]}...")

def test_search():
    try:
        db = SessionLocal()
        query = "¿Cuál es el descanso mínimo entre turnos?"
        company = "iberia" 
        
        print(f"🔎 Searching for: '{query}' (Company: {company})")
        
        results = rag_engine.search(query, company_slug=company, db=db, limit=3)
        
        print(f"📊 Found {len(results)} results.")
        for r in results:
            print(f"   - [{r['score']:.4f}] {r['article_ref']} ({r['document_title']}): {r['content'][:50]}...")
            
        if len(results) > 0:
            print("✅ RAG Search SUCCESS")
        else:
            print("❌ RAG Search FAILED (No results)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
