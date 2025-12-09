import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine

def verify():
    print("🧠 Testing XML Verification...")
    db = SessionLocal()
    
    # query = "sueldo base agente administrativo"
    # print(f"🔎 Searching for: '{query}'")
    # results = rag_engine.search(query, db=db, limit=5)
    
    # for r in results:
    #     print(f"   - Match: {r['article_ref']} (ID: {r.get('id')})")
    #     print(f"     Content Length: {len(r['content'])}")
    #     if "|" in r['content']:
    #         print(f"     ✅ TABLE DETECTED. Preview:\n{r['content'][r['content'].find('|'):][:200]}...")
    #         found_table = True
    #     else:
    #         print(f"     ❌ No '|' found. Preview start:\n{r['content'][:200]}...")

    print("\n🔎 Checking DB directly for tables...", flush=True)
    from app.db.models import DocumentChunk
    
    chunks = db.query(DocumentChunk).filter(DocumentChunk.content.like('%|%')).limit(1).all()
    if chunks:
        print(f"✅ FOUND {len(chunks)} chunk(s) with '|' in DB directly.", flush=True)
        print(f"   Preview beginning: {chunks[0].content[:50]}...", flush=True)
        print(f"   Preview pipe section: {chunks[0].content[chunks[0].content.find('|'):][:50]}...", flush=True)
    else:
        print("❌ NO chunks with '|' found in DB directly.", flush=True)
    
    db.close()

if __name__ == "__main__":
    verify()
