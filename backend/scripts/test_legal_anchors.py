"""
Script de prueba para Legal Anchors
Ejecutar: python backend/scripts/test_legal_anchors.py
"""
import os
import sys
import logging

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.legal_anchors import LegalAnchors
from app.db.database import SessionLocal

# Configura Logging
logging.basicConfig(level=logging.INFO)

def test_legal_anchors():
    """Prueba el servicio de Legal Anchors con diferentes intents."""
    
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

if __name__ == "__main__":
    test_legal_anchors()
