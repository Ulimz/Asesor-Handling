import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from sqlalchemy import select

def cleanup_pdf_documents():
    """Remove all PDF-sourced documents to avoid conflicts with XML data."""
    print("🧹 Cleaning up old PDF-sourced documents...")
    db = SessionLocal()
    
    try:
        # Get all documents
        all_docs = db.query(LegalDocument).all()
        
        print(f"\n📊 Current database state:")
        print(f"   Total documents: {len(all_docs)}")
        
        # Identify PDF documents (those without "XML" in title or from old ingestion)
        # We'll keep only documents that were created by seed_xml.py
        # These should have titles from boe_config.py
        
        xml_titles = [
            "V Convenio Colectivo General Sector Handling",
            "Estatuto de los Trabajadores (Texto Refundido)",
            "I Convenio Azul Handling",
            "XXII Convenio Iberia Tierra (South)",
            "V Convenio Groundforce",
            "Convenio Swissport Handling 2024",
            "I Convenio Menzies Aviation",
            "I Convenio WFS Ground Handling",
            "I Convenio Aviapartner",
            "V Convenio EasyJet Handling"
        ]
        
        docs_to_delete = []
        docs_to_keep = []
        
        for doc in all_docs:
            # Keep if title matches XML titles
            if any(xml_title in doc.title for xml_title in xml_titles):
                docs_to_keep.append(doc)
            else:
                docs_to_delete.append(doc)
        
        print(f"\n📋 Analysis:")
        print(f"   Documents to KEEP (XML): {len(docs_to_keep)}")
        for doc in docs_to_keep:
            chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            print(f"      - {doc.title} ({doc.company or 'Global'}) - {chunk_count} chunks")
        
        print(f"\n   Documents to DELETE (PDF): {len(docs_to_delete)}")
        for doc in docs_to_delete:
            chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            print(f"      - {doc.title} ({doc.company or 'Global'}) - {chunk_count} chunks")
        
        if docs_to_delete:
            print(f"\n🗑️ Deleting {len(docs_to_delete)} PDF documents...")
            for doc in docs_to_delete:
                # Delete chunks first
                db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
                # Delete document
                db.delete(doc)
            
            db.commit()
            print("✅ Cleanup complete!")
        else:
            print("\n✅ No PDF documents to delete. Database is clean!")
        
        # Final summary
        remaining = db.query(LegalDocument).count()
        total_chunks = db.query(DocumentChunk).count()
        print(f"\n📊 Final state:")
        print(f"   Documents: {remaining}")
        print(f"   Total chunks: {total_chunks}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_pdf_documents()
