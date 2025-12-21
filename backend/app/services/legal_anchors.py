"""
Legal Anchors Service - Capa 2 del Sistema RAG Híbrido (Elite Version)

Fuerza la inyección de documentos críticos (tablas, anexos) según el Intent detectado.
Implementa recuperación determinista basada en reglas para garantizar que información
clave siempre llegue al contexto del LLM.

Validado por 8 opiniones expertas - Nivel producción enterprise.
"""
import logging
from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk

logger = logging.getLogger(__name__)

class LegalAnchors:
    """
    Capa 2 del RAG: Recuperación Determinista basada en Reglas.
    Fuerza la inyección de documentos críticos según el Intent.
    """

    # MAPA MAESTRO DE ANCLAS
    # Define qué palabras clave DEBEN estar en el contenido para considerarse "documento ancla"
    # Esto busca LITERALMENTE en el texto del chunk.
    ANCHOR_MAP = {
        "LEAVE": [
            "grados de parentesco", 
            "tabla de consanguinidad", 
            "permisos retribuidos",
            "licencias retribuidas",
            "segundo grado",
            "tercer grado"
        ],
        "SALARY": [
            "tabla salarial", 
            "tablas salariales", 
            "retribución bruta anual",
            "niveles salariales",
            "grupo profesional",
            "plus de nocturnidad",
            "complemento salarial"
        ],
        "DISMISSAL": [
            "régimen disciplinario",
            "faltas y sanciones",
            "indemnización por despido",
            "liquidación de haberes",
            "extinción del contrato"
        ]
    }

    def get_anchors(self, intent: str, db: Session, company_slug: str = None, limit: int = 2) -> List[DocumentChunk]:
        """
        Recupera chunks específicos basándose en el Intent detectado.
        
        Args:
            intent: Intent detectado por QueryExpander (LEAVE, SALARY, DISMISSAL, GENERAL)
            db: Sesión de base de datos
            company_slug: Empresa del usuario (opcional, para filtrar)
            limit: Número máximo de chunks ancla a recuperar
            
        Returns:
            Lista de DocumentChunk que son "anclas" para este intent
        """
        # 1. Si el intent es GENERAL, no forzamos anclas (dejamos que el vector search decida)
        keywords = self.ANCHOR_MAP.get(intent)
        if not keywords:
            logger.debug(f"LegalAnchors: No hay anclas definidas para el intent '{intent}'")
            return []

        try:
            # 2. Construcción de la Query "OR" (Búsqueda Léxica)
            # Buscamos chunks que contengan CUALQUIERA de las palabras clave del intent.
            
            # Opción A: Búsqueda en contenido (funciona sin metadata)
            text_filters = [DocumentChunk.content.ilike(f"%{kw}%") for kw in keywords]
            
            # Opción B (FUTURA - cuando tengamos metadata):
            # text_filters = [DocumentChunk.metadata['type'] == 'table' ...]

            query = db.query(DocumentChunk).filter(or_(*text_filters))
            
            # 3. Filtrar por empresa si se proporciona
            if company_slug:
                from app.db.models import LegalDocument
                query = query.join(LegalDocument).filter(
                    (LegalDocument.company == company_slug) | 
                    (LegalDocument.company.ilike('general'))
                )
            
            anchors = query.limit(limit).all()

            if anchors:
                logger.info(f"LegalAnchors: Inyectados {len(anchors)} chunks para Intent '{intent}'")
                # Log de títulos para auditoría
                doc_titles = [a.document.title if a.document else "Unknown" for a in anchors] 
                logger.debug(f"LegalAnchors Docs: {doc_titles}")
            else:
                logger.warning(
                    f"LegalAnchors: Intent '{intent}' activo, pero no se encontraron documentos "
                    f"con keywords: {keywords[:3]}... (total: {len(keywords)} keywords)"
                )

            return anchors

        except Exception as e:
            logger.error(f"Error recuperando anclas: {str(e)}", exc_info=True)
            return []

# --- BLOQUE DE PRUEBA (Ejecutar directamente este archivo) ---
if __name__ == "__main__":
    import os
    import sys
    
    # Add backend to path BEFORE importing app modules
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_dir)
    
    # NOW we can import from app
    from app.db.database import SessionLocal
    
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 70)
    print("PRUEBA DE LEGAL ANCHORS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        anchors_service = LegalAnchors()
        
        test_intents = [
            ("LEAVE", "Permisos/Parentesco"),
            ("SALARY", "Tablas salariales"),
            ("DISMISSAL", "Sanciones/Despidos"),
            ("GENERAL", "Sin anclas")
        ]
        
        for intent, description in test_intents:
            print(f"\n🔍 Intent: {intent} ({description})")
            anchors = anchors_service.get_anchors(intent, db, limit=3)
            
            if anchors:
                print(f"   ✅ Encontrados {len(anchors)} chunks ancla:")
                for i, anchor in enumerate(anchors, 1):
                    doc_title = anchor.document.title if anchor.document else "Unknown"
                    article_ref = anchor.article_ref or "N/A"
                    content_preview = anchor.content[:100].replace('\n', ' ')
                    print(f"      {i}. [{doc_title}] {article_ref}")
                    print(f"         Preview: {content_preview}...")
            else:
                print(f"   ⚠️  No se encontraron anclas")
            
            print("-" * 70)
    
    finally:
        db.close()

