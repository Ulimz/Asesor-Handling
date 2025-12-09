
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from sqlalchemy import func

def verify():
    db = SessionLocal()
    try:
        total_docs = db.query(func.count(LegalDocument.id)).scalar()
        total_chunks = db.query(func.count(DocumentChunk.id)).scalar()
        
        print(f"Total Documents: {total_docs}")
        print(f"Total Chunks: {total_chunks}")
        
        # Check by category
        categories = db.query(LegalDocument.category, func.count(LegalDocument.id)).group_by(LegalDocument.category).all()
        print("\nDocuments by Category:")
        for cat, count in categories:
            print(f" - {cat}: {count}")
            
        # Check specific companies/slugs
        companies = db.query(LegalDocument.company, func.count(LegalDocument.id)).group_by(LegalDocument.company).all()
        print("\nDocuments by Company:")
        for comp, count in companies:
            print(f" - {comp}: {count}")

        # Check Jurisprudencia specifically
        juris = db.query(LegalDocument).filter(LegalDocument.category == "Jurisprudencia").all()
        if juris:
            print(f"\n✅ Jurisprudencia found: {len(juris)} docs")
            for j in juris:
                print(f"   - {j.title}")
        else:
            print("\n❌ No Jurisprudencia found in RAG system")

    finally:
        db.close()

if __name__ == "__main__":
    verify()
