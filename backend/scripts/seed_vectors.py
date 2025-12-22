"""
Seed script for legal documents with vector embeddings.
Uses local sentence-transformers model (FREE).

Improvements:
- Uses company_detector utility (no code duplication)
- Proper logging instead of print statements
- Type hints added
- Context manager for DB session
- Bulk inserts for better performance
- Data validation
"""
import json
from pathlib import Path
import sys
import os
from typing import List, Optional
from sqlalchemy.orm import Session

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk
from app.services.rag_engine import rag_engine
from app.utils.company_detector import detect_company_from_filename, detect_category_from_filename
from app.utils.paths import get_data_dir
from app.utils.logging_config import setup_logging, get_logger
from app.constants import EMBEDDING_DIMENSION

# Setup logging
setup_logging()
logger = get_logger(__name__)

def seed_single_document(json_file: Path, db: Session) -> Optional[int]:
    """
    Seed a single JSON document into the database.
    
    Args:
        json_file: Path to JSON file
        db: Database session
        
    Returns:
        Number of articles seeded, or None if skipped/failed
    """
    logger.info(f"Processing {json_file.name}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Detect company and category using utilities
        company = detect_company_from_filename(json_file.name)
        category = detect_category_from_filename(json_file.name)
        
        # Check for duplicates
        title = data.get("title", json_file.stem)
        existing = db.query(LegalDocument).filter(LegalDocument.title == title).first()
        if existing:
            logger.info(f"Skipping {title}: Already exists")
            return None
        
        # Create parent document
        doc = LegalDocument(
            title=title,
            category=category,
            company=company,
            url_source=data.get("url")
        )
        db.add(doc)
        db.flush()  # Get doc.id without committing
        
        # Prepare chunks for bulk insert
        articles = data.get("articles", [])
        chunks: List[DocumentChunk] = []
        
        for article in articles:
            content = article.get("content", "").strip()
            article_ref = article.get("article", "")
            
            # Validate content
            if not content:
                logger.warning(f"Skipping article {article_ref}: empty content")
                continue
            
            # Generate embedding with error handling
            try:
                embedding = rag_engine.generate_embedding(content)
            except Exception as e:
                logger.error(f"Failed to generate embedding for {article_ref}: {e}")
                # Use zero vector as fallback
                embedding = [0.0] * EMBEDDING_DIMENSION
            
            # --- METADATA TAGGING (FIX RED TEAM) ---
            chunk_type = "text"
            is_primary = False
            
            # 1. Detect Tables
            # Check for Markdown tables (| col |) or HTML tables
            # Loose check: must have multiple pipes or <table tag
            if "<table" in content.lower() or content.count("|") > 4: 
                chunk_type = "table"
                
            # 2. Detect Primary Articles (Tablas Salariales, Convenio)
            article_ref_upper = article_ref.upper()
            if "ANEXO" in article_ref_upper or "TABLA" in article_ref_upper or "CAPÍTULO ECONÓMICO" in article_ref_upper:
                is_primary = True
            
            # Additional heuristic: If it's a table and mentions levels/salary, it's primary for calculation
            if chunk_type == "table" and any(kw in content.lower() for kw in ["nivel", "salario", "retribución", "euros", "€"]):
                is_primary = True
            
            chunk_metadata = {
                "type": chunk_type,
                "is_primary": str(is_primary).lower(), # "true" / "false"
                "company": company,
                "ref": article_ref
            }
            # ----------------------------------------

            chunk = DocumentChunk(
                document_id=doc.id,
                content=content,
                embedding=embedding,
                article_ref=article_ref,
                # Inject Metadata for Postgres/PGVector
                chunk_metadata=chunk_metadata,
                # Also populate the legacy 'doc_id' if needed or just leave null
                doc_id=f"{doc.id}_{article_ref}" 
            )
            chunks.append(chunk)
        
        # Bulk insert chunks
        if chunks:
            db.bulk_save_objects(chunks)
            db.commit()
            logger.info(f"✅ Seeded {len(chunks)} articles for {doc.title}")
            return len(chunks)
        else:
            logger.warning(f"No valid articles found in {json_file.name}")
            db.rollback()
            return 0
            
    except Exception as e:
        logger.error(f"Error processing {json_file.name}: {e}")
        print(f"CRITICAL ERROR processing {json_file.name}: {e}") # Added for immediate feedback
        import traceback
        traceback.print_exc()
        db.rollback()
        return None

def seed_documents() -> None:
    """
    Seed all JSON documents from data directory.
    """
    data_dir = get_data_dir()
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        logger.warning(f"No JSON files found in {data_dir}")
        return
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    total_articles = 0
    processed = 0
    skipped = 0
    failed = 0
    
    with SessionLocal() as db:
        for json_file in json_files:
            result = seed_single_document(json_file, db)
            
            if result is not None:
                if result > 0:
                    total_articles += result
                    processed += 1
                else:
                    skipped += 1
            else:
                failed += 1
    
    # Summary
    logger.info("="*60)
    logger.info(f"Seeding complete:")
    logger.info(f"  Processed: {processed} documents")
    logger.info(f"  Skipped: {skipped} documents (already exist)")
    logger.info(f"  Failed: {failed} documents")
    logger.info(f"  Total articles: {total_articles}")

if __name__ == "__main__":
    seed_documents()
