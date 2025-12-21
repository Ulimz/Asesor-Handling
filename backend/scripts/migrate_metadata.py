"""
Script de migración para añadir metadata a chunks existentes.
VERSIÓN HÍBRIDA - Combina estabilidad del experto con descriptividad mejorada.

Ejecutar: python backend/scripts/migrate_metadata.py
"""
import os
import sys
import hashlib
import re
from datetime import datetime

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import SessionLocal
from app.db.models import DocumentChunk, LegalDocument
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_version_hash(document: LegalDocument, year: int) -> str:
    """
    ✅ DEL EXPERTO: Hash estable usando document.id
    """
    title = document.title or "unknown"
    base = f"{document.id}_{title}_{year}"
    return hashlib.md5(base.encode()).hexdigest()[:8]


def generate_doc_id(document: LegalDocument, year: int) -> str:
    """
    ✅ HÍBRIDO: doc_id descriptivo pero estable
    Usa company + slug del título + year
    """
    company = document.company or "general"
    title = document.title or "unknown"
    # Crear slug del título
    title_slug = re.sub(r'[^a-z0-9]+', '_', title.lower())[:30]
    # ✅ MEJORA: Strip underscores al inicio/final
    title_slug = title_slug.strip("_")
    return f"{company}_{title_slug}_{year}"


def infer_chunk_type(chunk: DocumentChunk) -> str:
    """
    ✅ MEJORADO: Inferencia robusta de tablas
    """
    content_lower = (chunk.content or "").lower()
    article_ref = (chunk.article_ref or "").lower()

    # Tablas - detección mejorada
    table_keywords = [
        'tabla salarial', 'tablas salariales',
        'retribución', 'retribuciones',
        'salario', 'anexo', 'tabla'
    ]
    
    if 'anexo' in article_ref:
        if any(kw in content_lower for kw in ['retribu', 'salario', 'plus', 'nivel']):
            return 'table'
    
    if any(kw in content_lower for kw in table_keywords):
        return 'table'

    # Artículos
    if 'artículo' in article_ref or 'art.' in article_ref:
        return 'article'

    # Regulaciones
    if any(kw in content_lower for kw in ['régimen disciplinario', 'faltas y sanciones']):
        return 'regulation'

    return 'text'


def infer_intents(chunk: DocumentChunk, chunk_type: str) -> list:
    """
    ✅ MEJORADO: Inferencia con fallback SALARY para tablas
    """
    content_lower = (chunk.content or "").lower()
    intents = []

    # SALARY
    salary_keywords = [
        'salario', 'retribución', 'tabla salarial', 
        'plus', 'paga extra', 'retribu'
    ]
    if any(kw in content_lower for kw in salary_keywords):
        intents.append('SALARY')

    # LEAVE
    leave_keywords = [
        'permiso', 'vacaciones', 'licencia', 
        'parentesco', 'ausencia'
    ]
    if any(kw in content_lower for kw in leave_keywords):
        intents.append('LEAVE')

    # DISMISSAL
    dismissal_keywords = [
        'despido', 'sanción', 'disciplinario', 'extinción'
    ]
    if any(kw in content_lower for kw in dismissal_keywords):
        intents.append('DISMISSAL')

    # ✅ Fallback SALARY para tablas
    if chunk_type == 'table' and 'SALARY' not in intents:
        intents.append('SALARY')
        logger.debug(f"Chunk {chunk.id}: Añadido SALARY (tabla sin keywords)")

    return intents if intents else ['GENERAL']


def migrate_chunk_metadata(chunk: DocumentChunk, document: LegalDocument) -> dict:
    """
    ✅ HÍBRIDO: Metadata completa con mejores prácticas
    """
    chunk_type = infer_chunk_type(chunk)
    intents = infer_intents(chunk, chunk_type)

    # Extraer año
    year = 2025
    if document.title:
        year_match = re.search(r'20\d{2}', document.title)
        if year_match:
            year = int(year_match.group(0))

    # ✅ DEL EXPERTO: version_hash estable
    version_hash = generate_version_hash(document, year)

    # ✅ HÍBRIDO: doc_id descriptivo
    doc_id = generate_doc_id(document, year)

    # Extraer artículo
    article_num = None
    if chunk.article_ref:
        art_match = re.search(r'(\d+)', chunk.article_ref)
        if art_match:
            article_num = int(art_match.group(1))

    return {
        "doc_id": doc_id,
        "company": document.company or "general",
        "intent": intents,
        "type": chunk_type,
        "year": year,
        "source": "convenio" if (document.title and "convenio" in document.title.lower()) else "estatuto",
        "article": article_num,
        "version_hash": version_hash,
        "chunk_size": len(chunk.content or ""),
        "is_primary": chunk_type in ['table', 'article'],
    }


def main():
    db = SessionLocal()

    try:
        logger.info("🔄 Iniciando migración HÍBRIDA de metadata...")

        chunks = db.query(DocumentChunk).all()
        total = len(chunks)

        logger.info(f"📊 Total de chunks: {total}")

        migrated = 0
        skipped = 0

        for i, chunk in enumerate(chunks, 1):
            if not hasattr(chunk, 'document') or chunk.document is None:
                logger.warning(f"⚠️  Chunk {chunk.id} sin documento, saltando...")
                skipped += 1
                continue

            # Generar metadata
            metadata = migrate_chunk_metadata(chunk, chunk.document)

            # ✅ DEL EXPERTO: Actualizar columna Y metadata
            chunk.chunk_metadata = metadata
            chunk.doc_id = metadata["doc_id"]
            
            migrated += 1

            if i % 100 == 0:
                db.commit()
                logger.info(f"✅ Procesados {i}/{total}...")

        db.commit()
        logger.info(f"\n✅ Migración completada:")
        logger.info(f"   - Migrados: {migrated}")
        logger.info(f"   - Saltados: {skipped}")

        # ✅ MEJORADO: Estadísticas detalladas
        logger.info("\n📊 Estadísticas por tipo:")
        for chunk_type in ['table', 'article', 'regulation', 'text']:
            count = db.query(DocumentChunk).filter(
                DocumentChunk.chunk_metadata['type'].astext == chunk_type
            ).count()
            logger.info(f"   - {chunk_type}: {count}")

        logger.info("\n📊 Estadísticas por intent:")
        for intent in ['SALARY', 'LEAVE', 'DISMISSAL', 'GENERAL']:
            count = db.query(DocumentChunk).filter(
                DocumentChunk.chunk_metadata['intent'].contains([intent])
            ).count()
            logger.info(f"   - {intent}: {count}")

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
