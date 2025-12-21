"""
Script de prueba manual para Query Expander (Elite Version)
Ejecutar: python backend/scripts/test_query_expansion.py
"""
import os
import sys
import logging

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.query_expander import QueryExpander

# Configura Logging
logging.basicConfig(level=logging.INFO)

def test_queries():
    """Prueba el Query Expander con queries reales."""
    
    expander = QueryExpander()
    
    test_cases = [
        "mi tío está malo tengo permiso",
        "cuánto cobra un agente de rampa nivel 3",
        "me han sancionado injustamente",
        "quiero reclamar horas extras",
        "mi abuela está hospitalizada",
        "cuántos días de vacaciones tengo",
        "plus de nocturnidad en easyjet",
        "hola buenos días"
    ]
    
    print("=" * 70)
    print("PRUEBA DE QUERY EXPANSION (Elite Version)")
    print("=" * 70)
    
    for query in test_cases:
        print(f"\n📝 Query original: '{query}'")
        expansion = expander.expand(query)
        
        print(f"   Intent: {expansion['intent']}")
        print(f"   Keywords: {expansion['keywords_busqueda']}")
        print(f"   Entidades: {expansion['entidades_detectadas']}")
        print(f"   Requiere tablas: {expansion['requiere_tablas']}")
        print(f"   Meta: {expansion['meta']}")
        print(f"   → Búsqueda: '{expander.get_expanded_query_text(expansion)}'")
        print("-" * 70)

if __name__ == "__main__":
    test_queries()

