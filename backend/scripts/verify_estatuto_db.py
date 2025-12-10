import sys
import os
# Add parent dir to path so we can import 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from sqlalchemy import select

def check_estatuto_art34():
    db = SessionLocal()
    try:
        # Find Estatuto document
        doc = db.execute(select(LegalDocument).filter(
            (LegalDocument.title.ilike('%Estatuto%'))
        )).scalars().first()
        
        if not doc:
            print("❌ Estatuto document NOT found in LegalDocument table!")
            return

        print(f"✅ Found Document: {doc.title} (ID: {doc.id}, Company: {doc.company}, Category: {doc.category})")
        
        # SEARCH BY EXACT ARTICLE REF
        # The JSON has "Artículo 34. Jornada."
        # The chunk article_ref might be "Artículo 34. Jornada."
        
        print("Searching for Article 34 chunks...")
        chunks = db.execute(select(DocumentChunk).filter(
            DocumentChunk.document_id == doc.id,
            DocumentChunk.article_ref.ilike('%Artículo 34%')
        )).scalars().all()
        
        if not chunks:
             print("❌ No chunks found for Article 34 in this document.")
        else:
             print(f"✅ Found {len(chunks)} chunks for Article 34:")
             for c in chunks:
                 print(f"   - Ref: {c.article_ref}")
                 print(f"   - Content Preview: {c.content[:100]}...")
                 
    finally:
        db.close()

if __name__ == "__main__":
    check_estatuto_art34()
