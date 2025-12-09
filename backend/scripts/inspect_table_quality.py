import sys
import os
from sqlalchemy import text

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import DocumentChunk
from sqlalchemy import select

def inspect_anexo():
    db = SessionLocal()
    try:
        print("🔍 Inspecting 'ANEXO I' content...")
        # Try to find a chunk that looks like a salary table
        stmt = select(DocumentChunk).where(DocumentChunk.article_ref.ilike("%ANEXO I%")).limit(1)
        chunk = db.execute(stmt).scalars().first()
        
        if chunk:
            print(f"--- CONTENT START (ID: {chunk.id}) ---")
            print(chunk.content[:2000]) # First 2000 chars
            print("--- CONTENT END ---")
        else:
            print("❌ No 'ANEXO I' found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_anexo()
