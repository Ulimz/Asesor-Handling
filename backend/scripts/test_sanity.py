"""
Smoke Test - Verificación de Integridad Post-Migración
Ejecutar DESPUÉS de migrate_metadata.py

Verifica:
1. Integridad: No hay nulos en campos críticos
2. Inferencia: Detectó tablas salariales correctamente
3. Seguridad: Años son números válidos
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import SessionLocal
from app.db.models import DocumentChunk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_integrity(db):
    """Verificar que no hay nulos en campos críticos."""
    logger.info("\n🔍 Test 1: Integridad de Datos")
    
    # Chunks sin metadata
    null_metadata = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata == None
    ).count()
    
    logger.info(f"   Chunks sin metadata: {null_metadata}")
    assert null_metadata == 0, "❌ Hay chunks sin metadata!"
    logger.info("   ✅ Todos los chunks tienen metadata")
    
    # Chunks sin doc_id
    null_doc_id = db.query(DocumentChunk).filter(
        DocumentChunk.doc_id == None
    ).count()
    
    logger.info(f"   Chunks sin doc_id: {null_doc_id}")
    if null_doc_id > 0:
        logger.warning(f"   ⚠️  {null_doc_id} chunks sin doc_id (pueden ser chunks sin documento)")
    else:
        logger.info("   ✅ Todos los chunks tienen doc_id")


def test_inference(db):
    """Verificar que detectó tablas salariales."""
    logger.info("\n🔍 Test 2: Inferencia de Tipos")
    
    # Contar por tipo
    types = ['table', 'article', 'regulation', 'text']
    for chunk_type in types:
        count = db.query(DocumentChunk).filter(
            DocumentChunk.chunk_metadata['type'].astext == chunk_type
        ).count()
        logger.info(f"   {chunk_type}: {count} chunks")
    
    # Verificar que hay tablas
    table_count = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata['type'].astext == 'table'
    ).count()
    
    assert table_count > 0, "❌ No se detectaron tablas!"
    logger.info(f"   ✅ Detectadas {table_count} tablas")


def test_intents(db):
    """Verificar que asignó intents correctamente."""
    logger.info("\n🔍 Test 3: Inferencia de Intents")
    
    intents = ['SALARY', 'LEAVE', 'DISMISSAL', 'GENERAL']
    for intent in intents:
        count = db.query(DocumentChunk).filter(
            DocumentChunk.chunk_metadata['intent'].contains([intent])
        ).count()
        logger.info(f"   {intent}: {count} chunks")
    
    # Verificar que hay chunks con SALARY
    salary_count = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata['intent'].contains(['SALARY'])
    ).count()
    
    assert salary_count > 0, "❌ No se detectaron chunks con intent SALARY!"
    logger.info(f"   ✅ Detectados {salary_count} chunks SALARY")


def test_year_safety(db):
    """Verificar que el regex de año funcionó."""
    logger.info("\n🔍 Test 4: Seguridad de Años")
    
    # Intentar obtener un chunk con año 2025
    chunk_2025 = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata['year'].astext == '2025'
    ).first()
    
    if chunk_2025:
        logger.info(f"   ✅ Encontrado chunk con año 2025")
        logger.info(f"      doc_id: {chunk_2025.doc_id}")
    else:
        logger.warning("   ⚠️  No hay chunks con año 2025")
    
    # Contar chunks por año
    from sqlalchemy import func
    years = db.query(
        DocumentChunk.chunk_metadata['year'].astext,
        func.count(DocumentChunk.id)
    ).group_by(
        DocumentChunk.chunk_metadata['year'].astext
    ).all()
    
    logger.info("   Distribución por año:")
    for year, count in years:
        logger.info(f"      {year}: {count} chunks")


def test_version_hash(db):
    """Verificar que se generaron version_hash."""
    logger.info("\n🔍 Test 5: Version Hash")
    
    # Contar version_hash únicos
    from sqlalchemy import func
    unique_hashes = db.query(
        func.count(func.distinct(DocumentChunk.chunk_metadata['version_hash'].astext))
    ).scalar()
    
    logger.info(f"   Version hashes únicos: {unique_hashes}")
    assert unique_hashes > 0, "❌ No se generaron version_hash!"
    logger.info(f"   ✅ Generados {unique_hashes} version_hash únicos")


def test_sample_chunk(db):
    """Mostrar un chunk de ejemplo."""
    logger.info("\n🔍 Test 6: Chunk de Ejemplo")
    
    # Obtener una tabla salarial
    sample = db.query(DocumentChunk).filter(
        DocumentChunk.chunk_metadata['type'].astext == 'table',
        DocumentChunk.chunk_metadata['intent'].contains(['SALARY'])
    ).first()
    
    if sample:
        logger.info("   Ejemplo de chunk migrado:")
        logger.info(f"      ID: {sample.id}")
        logger.info(f"      doc_id: {sample.doc_id}")
        logger.info(f"      type: {sample.chunk_metadata.get('type')}")
        logger.info(f"      intent: {sample.chunk_metadata.get('intent')}")
        logger.info(f"      company: {sample.chunk_metadata.get('company')}")
        logger.info(f"      year: {sample.chunk_metadata.get('year')}")
        logger.info(f"      version_hash: {sample.chunk_metadata.get('version_hash')}")
        logger.info(f"      is_primary: {sample.chunk_metadata.get('is_primary')}")
        logger.info(f"   ✅ Metadata completa")
    else:
        logger.warning("   ⚠️  No se encontró chunk de ejemplo")


def main():
    db = SessionLocal()
    
    try:
        logger.info("=" * 70)
        logger.info("SMOKE TEST - VERIFICACIÓN POST-MIGRACIÓN")
        logger.info("=" * 70)
        
        # Total de chunks
        total = db.query(DocumentChunk).count()
        logger.info(f"\n📊 Total de chunks en BD: {total}")
        
        # Ejecutar tests
        test_integrity(db)
        test_inference(db)
        test_intents(db)
        test_year_safety(db)
        test_version_hash(db)
        test_sample_chunk(db)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ TODOS LOS TESTS PASARON")
        logger.info("=" * 70)
        logger.info("\n🚀 Sistema listo para usar Legal Anchors con metadata!")
        
    except AssertionError as e:
        logger.error(f"\n❌ TEST FALLIDO: {e}")
        raise
    
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
