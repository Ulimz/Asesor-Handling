"""
Legal Anchors Service - VERSIÓN HÍBRIDA
Combina arquitectura del experto con caché de performance.

Capa 2 del RAG: Recuperación Determinista basada en Reglas.
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, Boolean, Integer
from app.db.models import DocumentChunk

logger = logging.getLogger(__name__)


class LegalAnchors:
    """
    Capa 2 del RAG: Recuperación Determinista.
    ✅ HÍBRIDO: Filtros del experto + Caché optimizado
    """
    
    # ✅ DE MI CÓDIGO: Caché versionado
    _cache = {}
    _expiry = {}
    
    def _get_version_hash(self, company: str, db: Session) -> str:
        """
        Obtiene version_hash del convenio más reciente.
        ✅ MEJORA: Ordenar por ID desc para obtener el más reciente
        """
        chunk = db.query(DocumentChunk).filter(
            DocumentChunk.metadata['company'].astext == company
        ).order_by(DocumentChunk.id.desc()).first()
        
        if chunk and chunk.metadata:
            return chunk.metadata.get('version_hash', 'default')
        
        return 'default'
    
    def get_anchors(
        self,
        intent: str,
        db: Session,
        company_slug: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 2,
    ) -> List[DocumentChunk]:
        """
        Recupera chunks usando metadata (100% determinista).
        
        ✅ HÍBRIDO:
        - Filtros específicos por intent (del experto)
        - Caché versionado (de mi código)
        - Logging detallado (de mi código)
        
        Args:
            intent: Intent detectado (LEAVE, SALARY, DISMISSAL)
            db: Sesión de base de datos
            company_slug: Empresa del usuario (opcional)
            year: Año del convenio (default: año actual)
            limit: Número máximo de chunks
            
        Returns:
            Lista de DocumentChunk que son "anclas"
        """
        
        if intent not in ["LEAVE", "SALARY", "DISMISSAL"]:
            logger.debug(f"LegalAnchors: Intent '{intent}' no requiere anclas")
            return []
        
        # Año por defecto
        target_year = year or datetime.now().year
        
        # ✅ DE MI CÓDIGO: Caché versionado
        version = self._get_version_hash(company_slug, db) if company_slug else 'general'
        cache_key = f"{intent}_{company_slug}_{version}_{target_year}"
        now = datetime.now()
        
        if cache_key in self._cache and now < self._expiry.get(cache_key, now):
            logger.info(f"Cache HIT: {cache_key}")
            return self._cache[cache_key]
        
        try:
            # ✅ DEL EXPERTO: Array contains
            query = db.query(DocumentChunk).filter(
                DocumentChunk.metadata['intent'].contains([intent])
            )
            
            # ✅ DEL EXPERTO: Filtros específicos por intent
            if intent == "SALARY":
                query = query.filter(
                    DocumentChunk.metadata['type'].astext == 'table'
                )
            elif intent == "DISMISSAL":
                query = query.filter(
                    DocumentChunk.metadata['type'].astext == 'regulation'
                )
            elif intent == "LEAVE":
                query = query.filter(
                    DocumentChunk.metadata['type'].astext.in_(['article', 'table'])
                )
            
            # ✅ DEL EXPERTO: Manejo correcto de company_slug None
            if company_slug:
                query = query.filter(
                    or_(
                        DocumentChunk.metadata['company'].astext == company_slug,
                        DocumentChunk.metadata['company'].astext == 'general'
                    )
                )
            else:
                query = query.filter(
                    DocumentChunk.metadata['company'].astext == 'general'
                )
            
            # ✅ DEL EXPERTO: Filtro por año
            query = query.filter(
                DocumentChunk.metadata['year'].astext.cast(Integer) == target_year
            )
            
            # ✅ DEL EXPERTO: Filtro por version_hash
            query = query.filter(
                DocumentChunk.metadata['version_hash'].astext == version
            )
            
            # ✅ DEL EXPERTO: Boolean casting
            query = query.filter(
                DocumentChunk.metadata['is_primary'].astext.cast(Boolean) == True
            ).order_by(
                DocumentChunk.metadata['chunk_size'].astext.cast(Integer).desc()
            )
            
            anchors = query.limit(limit).all()
            
            # ✅ DE MI CÓDIGO: Guardar en caché
            self._cache[cache_key] = anchors
            self._expiry[cache_key] = now + timedelta(hours=1)
            
            # ✅ DE MI CÓDIGO: Logging detallado
            if anchors:
                logger.info(
                    f"LegalAnchors: intent={intent}, company={company_slug}, "
                    f"year={target_year}, found={len(anchors)} (Cache MISS)"
                )
                doc_titles = [a.document.title if a.document else "Unknown" for a in anchors]
                logger.debug(f"Docs: {doc_titles}")
            else:
                logger.warning(
                    f"LegalAnchors: intent={intent}, company={company_slug}, "
                    f"year={target_year}, found=0"
                )
            
            return anchors
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return []
