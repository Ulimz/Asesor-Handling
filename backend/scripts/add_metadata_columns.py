"""
Script para añadir las columnas doc_id y chunk_metadata a la tabla document_chunks.
Ejecutar ANTES de migrate_metadata.py
"""
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import SessionLocal, engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_columns():
    """Añade las columnas doc_id y chunk_metadata si no existen."""
    db = SessionLocal()
    
    try:
        logger.info("🔧 Verificando y añadiendo columnas...")
        
        # Añadir doc_id
        try:
            db.execute(text("""
                ALTER TABLE document_chunks 
                ADD COLUMN IF NOT EXISTS doc_id VARCHAR;
            """))
            db.commit()
            logger.info("✅ Columna doc_id añadida/verificada")
        except Exception as e:
            logger.warning(f"doc_id: {e}")
            db.rollback()
        
        # Añadir chunk_metadata
        try:
            db.execute(text("""
                ALTER TABLE document_chunks 
                ADD COLUMN IF NOT EXISTS chunk_metadata JSONB DEFAULT '{}';
            """))
            db.commit()
            logger.info("✅ Columna chunk_metadata añadida/verificada")
        except Exception as e:
            logger.warning(f"chunk_metadata: {e}")
            db.rollback()
        
        # Crear índice para doc_id
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_doc_id 
                ON document_chunks(doc_id);
            """))
            db.commit()
            logger.info("✅ Índice idx_doc_id creado/verificado")
        except Exception as e:
            logger.warning(f"idx_doc_id: {e}")
            db.rollback()
        
        logger.info("\n✅ Columnas creadas exitosamente")
        logger.info("Ahora puedes ejecutar: python backend/scripts/migrate_metadata.py")
        
    finally:
        db.close()

if __name__ == "__main__":
    add_columns()
