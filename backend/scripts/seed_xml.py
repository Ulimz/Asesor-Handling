import json
import glob
from pathlib import Path
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from app.services.rag_engine import rag_engine
from app.constants import EMBEDDING_DIMENSION, SALARY_KEYWORDS
from app.utils.paths import get_xml_parsed_dir
from app.utils.logging_config import setup_logging, get_logger
from sqlalchemy import select
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

# Setup logging
setup_logging()
logger = get_logger(__name__)

def seed_from_json(json_file: Path, db: Session) -> Optional[int]:
    """Seed a single JSON file into the database."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data.get("title", "Unknown")
    company_slug = data.get("company_slug", "general")
    url = data.get("url", "")
    
    print(f"\n📄 Processing: {title} ({company_slug})")
    
    # Map slug to company name for DB
    # "general" and "estatuto" are global (company=None or 'general')
    # Others use their slug as company identifier
    if company_slug in ["general", "estatuto"]:
        company_name = None  # Global documents
    else:
        company_name = company_slug
    
    # 1. Check if document already exists
    stmt = select(LegalDocument).where(
        LegalDocument.title == title
    )
    existing = db.execute(stmt).scalars().first()
    
    if existing:
        print(f"   🗑️ Removing existing document (ID {existing.id})...")
        db.query(DocumentChunk).filter(DocumentChunk.document_id == existing.id).delete()
        db.delete(existing)
        db.commit()
    
    # 2. Create Parent Document
    doc = LegalDocument(
        title=title,
        category="Convenio" if company_slug != "estatuto" else "Legislación",
        company=company_name,
        url_source=url
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 3. Insert Chunks
    articles = data.get("articles", [])
    print(f"   Propagating {len(articles)} articles...")
    
    count = 0
    for article in articles:
        content = article.get("content", "")
        article_ref = article.get("article", "")
        
        # Enrich content for Annexes (Phase 1 semantic enrichment)
        if "ANEXO" in article_ref.upper() or "TABLA" in article_ref.upper():
            content += f"\n\n(Palabras clave: {SALARY_KEYWORDS})"
        
        # Generate embedding with error handling
        try:
            embedding = rag_engine.generate_embedding(content)
        except Exception as e:
            print(f"      ⚠️ Embedding failed for '{article_ref[:50]}...': {e}")
            # Fallback: zero vector (will have low similarity but won't crash)
            embedding = [0.0] * EMBEDDING_DIMENSION
        
        chunk = DocumentChunk(
            document_id=doc.id,
            content=content,
            embedding=embedding,
            article_ref=article_ref
        )
        db.add(chunk)
        count += 1
        if count % 50 == 0:
            print(f"      Processed {count}...")
    
    db.commit()
    print(f"   ✅ Seeded {count} chunks for {company_slug}")

def batch_process():
    """Batch process all JSON files in xml_parsed directory."""
    logger.info("🌱 Batch Seeding XML-derived Documents...")
    
    parsed_dir = get_xml_parsed_dir()
    
    if not parsed_dir.exists():
        logger.error(f"Directory not found: {parsed_dir}")
        return
    
    json_files = list(parsed_dir.glob("*.json"))
    
    if not json_files:
        logger.warning(f"No JSON files found in {parsed_dir}")
        return
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    db = SessionLocal()
    total_seeded = 0
    
    try:
        for json_file in json_files:
            result = seed_from_json(json_file, db)
            if result:
                total_seeded += result
        
        logger.info(f"✅ Batch seeding complete! Total articles: {total_seeded}")
    finally:
        db.close()

if __name__ == "__main__":
    batch_process()
