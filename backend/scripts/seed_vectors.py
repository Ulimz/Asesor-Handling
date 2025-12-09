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
    
    # Iterate over all JSON files in data dir
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        print("⚠️  No JSON files found in backend/data/")
        return

    for json_file in json_files:
        print(f"Propagating {json_file.name}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine company from filename or content
            filename_lower = json_file.name.lower()
            if "iberia" in filename_lower:
                company = "iberia"
            elif "groundforce" in filename_lower:
                company = "groundforce"
            elif "swissport" in filename_lower:
                company = "swissport"
            elif "aviapartner" in filename_lower:
                company = "aviapartner"
            elif "azul" in filename_lower:
                company = "azul"
            elif "easyjet" in filename_lower:
                company = "easyjet"
            elif "menzies" in filename_lower:
                company = "menzies"
            elif "wfs" in filename_lower:
                company = "wfs"
            elif "general" in filename_lower:
                company = "general" # Might treated as 'sectorial'
            elif "clece" in filename_lower or "talher" in filename_lower:
                company = "clece"
            elif "acciona" in filename_lower:
                company = "acciona"
            else:
                company = "general"

            # Check if doc exists to avoid duplicates (naive check)
            existing = db.query(LegalDocument).filter(LegalDocument.title == data.get("title")).first()
            if existing:
                print(f"Skipping {data.get('title')}: Already exists.")
                continue

            # Create parent document
            doc = LegalDocument(
                title=data.get("title", json_file.stem),
                category="Convenio",
                company=company,
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
            
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            
    db.close()

if __name__ == "__main__":
    seed_documents()
