import sys
import os
import asyncio

# FORCE PATH
sys.path.insert(0, '/app')
print(f"DEBUG PATH: {sys.path}")
import os
print(f"DEBUG CWD: {os.getcwd()}")
print(f"DEBUG LS /app: {os.listdir('/app')}")

from app.db.database import SessionLocal, engine
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
    
    # 1. Check if Estatuto exists in DB
    print("\n[DB CHECK] Verifying 'Estatuto' document:")
    docs = db.execute(text("SELECT id, title, company FROM legal_documents WHERE title ILIKE '%Estatuto%'")).fetchall()
    for d in docs:
        print(f"  - ID: {d[0]}, Title: {d[1]}, Company: {d[2]}")

    # 2. Run actual search
    print(f"\n[SEARCH] Running rag_engine.search(limit=15)...")
    try:
        results = rag.search(query, company_slug=company_slug, db=db, limit=15)
        
        print(f"\nFound {len(results)} chunks:")
        found_estatuto = False
        for i, chunk in enumerate(results):
            doc_title = chunk.get('document_title', 'Unknown')
            company = chunk.get('company', 'Unknown')
            print(f"[{i+1}] {doc_title} ({company}) - {chunk.get('article_ref', '')}")
            print(f"     Preview: {chunk.get('content', '')[:100]}...")
            
            if "estatuto" in doc_title.lower() or "general" in str(company).lower():
                found_estatuto = True
                print("     ✅ MATCHES ESTATUTO/GENERAL")
                
        if not found_estatuto:
            print("\n❌ ISSUE: No Statute/General documents found in top 15!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    # 3. Inspect Postgres Chunk Count
    print(f"\n[PGVECTOR] Inspecting Chunks...")
    try:
         chunk_count = db.execute(text("SELECT count(*) FROM document_chunks")).scalar()
         print(f"Total chunks in 'document_chunks': {chunk_count}")
         
         # Check per company
         print("\nChunks per company:")
         company_counts = db.execute(text("""
            SELECT ld.company, count(dc.id) 
            FROM document_chunks dc 
            JOIN legal_documents ld ON dc.document_id = ld.id 
            GROUP BY ld.company
         """)).fetchall()
         for c, val in company_counts:
             print(f"  - {c}: {val}")
             
    except Exception as e:
        print(f"Error inspecting DB: {e}")

if __name__ == "__main__":
    debug_search()
