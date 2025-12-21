"""
Script to verify that legal documents are properly indexed in the database.
Checks for specific keywords related to the "tío" (uncle) permissions issue.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add backend directory to path (scripts is inside backend)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import DATABASE_URL

def verify_indexing():
    """Check if documents are indexed and contain expected content."""
    
    engine = create_engine(DATABASE_URL)
    
    print("=" * 60)
    print("VERIFICACIÓN DE INDEXACIÓN DE DOCUMENTOS")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Check total number of chunks
        result = conn.execute(text("SELECT COUNT(*) FROM document_chunks;"))
        total_chunks = result.scalar()
        print(f"\n✓ Total de chunks indexados: {total_chunks}")
        
        # 2. Check for "tío" keyword
        result = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE content ILIKE '%tío%';"))
        tio_count = result.scalar()
        print(f"✓ Chunks que contienen 'tío': {tio_count}")
        
        if tio_count > 0:
            print("\n  📄 Ejemplos de contenido con 'tío':")
            result = conn.execute(text("""
                SELECT article_ref, LEFT(content, 150) as snippet 
                FROM document_chunks 
                WHERE content ILIKE '%tío%' 
                LIMIT 3;
            """))
            for row in result:
                print(f"    - {row[0]}: {row[1]}...")
        
        # 3. Check for "segundo grado" keyword
        result = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE content ILIKE '%segundo grado%';"))
        segundo_grado_count = result.scalar()
        print(f"\n✓ Chunks que contienen 'segundo grado': {segundo_grado_count}")
        
        # 4. Check for "permiso" keyword
        result = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE content ILIKE '%permiso%';"))
        permiso_count = result.scalar()
        print(f"✓ Chunks que contienen 'permiso': {permiso_count}")
        
        # 5. Check documents by company
        print("\n📊 Distribución por documento:")
        result = conn.execute(text("""
            SELECT d.title, COUNT(c.id) as chunk_count
            FROM legal_documents d
            LEFT JOIN document_chunks c ON d.id = c.document_id
            GROUP BY d.title
            ORDER BY chunk_count DESC;
        """))
        for row in result:
            print(f"  - {row[0]}: {row[1]} chunks")
        
        # 6. Specific check for Swissport (has explicit "tío" mention)
        print("\n🔍 Verificación específica: Swissport")
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM document_chunks c
            JOIN legal_documents d ON c.document_id = d.id
            WHERE d.title ILIKE '%swissport%' AND c.content ILIKE '%tío%';
        """))
        swissport_tio = result.scalar()
        print(f"  - Chunks de Swissport con 'tío': {swissport_tio}")
        
        # 7. Check if embeddings exist
        result = conn.execute(text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;"))
        with_embeddings = result.scalar()
        print(f"\n✓ Chunks con embeddings generados: {with_embeddings}/{total_chunks}")
        
        # 8. Final diagnosis
        print("\n" + "=" * 60)
        print("DIAGNÓSTICO:")
        print("=" * 60)
        
        if total_chunks == 0:
            print("❌ PROBLEMA: No hay documentos indexados en la base de datos.")
            print("   SOLUCIÓN: Ejecutar el script de ingesta de XMLs.")
        elif tio_count == 0:
            print("⚠️  ADVERTENCIA: Los documentos están indexados pero no contienen 'tío'.")
            print("   Esto podría indicar un problema con el parsing de XMLs.")
        elif with_embeddings < total_chunks:
            print(f"⚠️  ADVERTENCIA: {total_chunks - with_embeddings} chunks sin embeddings.")
            print("   SOLUCIÓN: Regenerar embeddings para todos los chunks.")
        else:
            print("✅ Los documentos están correctamente indexados.")
            print("   El problema de búsqueda puede ser semántico (embeddings débiles).")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    verify_indexing()
