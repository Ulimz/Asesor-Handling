
import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

from app.db.models import LegalDocument, DocumentChunk
from app.services.rag_engine import RagEngine

# Constants
COMPANY_SLUG = "azul-handling"
JSON_PATH = os.path.join(os.getcwd(), "backend", "data", "azulhandling.json")

def reingest():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ No DATABASE_URL")
        return
        
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    engine_db = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine_db)
    db = SessionLocal()
    
    rag = RagEngine()

    try:
        print(f"🧹 Clearing existing documents for {COMPANY_SLUG}...")
        # Get Doc IDs
        docs = db.query(LegalDocument).filter(LegalDocument.company == COMPANY_SLUG).all()
        doc_ids = [d.id for d in docs]
        
        if doc_ids:
            db.query(DocumentChunk).filter(DocumentChunk.document_id.in_(doc_ids)).delete(synchronize_session=False)
            db.query(LegalDocument).filter(LegalDocument.company == COMPANY_SLUG).delete(synchronize_session=False)
            db.commit()
            print(f"Deleted {len(docs)} documents and their chunks.")
        
        # Load JSON
        if not os.path.exists(JSON_PATH):
            print(f"❌ JSON not found: {JSON_PATH}")
            return
            
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        articles = data.get("articles", [])
        print(f"📖 Found {len(articles)} articles in JSON.")
        
        # Create Parent Document
        doc = LegalDocument(
            title="Convenio Azul Handling",
            company=COMPANY_SLUG,
            category="convenio",
            url_source=data.get("url", "")
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        print("🧠 Generando Embeddings e Insertando Chunks...")
        chunks_to_add = []
        
        for art in articles:
            content = art.get("content", "")
            ref = art.get("article", "Referencia")
            
            if not content.strip():
                continue
                
            embedding = rag.generate_embedding(content)
            
            chunk = DocumentChunk(
                document_id=doc.id,
                article_ref=ref,
                content=content,
                embedding=embedding
            )
            chunks_to_add.append(chunk)

        db.add_all(chunks_to_add)
        db.commit()
        print(f"✅ Successfully ingested {len(chunks_to_add)} chunks for {COMPANY_SLUG}.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reingest()
