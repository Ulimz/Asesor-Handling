"""
Seed script for legal documents with vector embeddings.
Uses local sentence-transformers model (FREE).
"""
import json
from pathlib import Path
from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from app.services.rag_engine import rag_engine

def seed_documents():
    db = SessionLocal()
    
    # Path to JSON files
    data_dir = Path(__file__).parent.parent / "data"
    
    # Example: Load Iberia convention
    iberia_file = data_dir / "iberia_convenio.json"
    
    if not iberia_file.exists():
        print(f"⚠️  File not found: {iberia_file}")
        print("Skipping seed. Add JSON files to backend/data/ directory.")
        return
    
    with open(iberia_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create parent document
    doc = LegalDocument(
        title=data.get("title", "V Convenio Iberia"),
        category="Convenio",
        company="iberia",
        url_source=data.get("url")
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Create chunks with embeddings
    articles = data.get("articles", [])
    for article in articles:
        content = article.get("content", "")
        article_ref = article.get("article", "")
        
        # Generate embedding using local model
        embedding = rag_engine.generate_embedding(content)
        
        chunk = DocumentChunk(
            document_id=doc.id,
            content=content,
            embedding=embedding,
            article_ref=article_ref
        )
        db.add(chunk)
    
    db.commit()
    print(f"✅ Seeded {len(articles)} articles for {doc.title}")
    db.close()

if __name__ == "__main__":
    seed_documents()
