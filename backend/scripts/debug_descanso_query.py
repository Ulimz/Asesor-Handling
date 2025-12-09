import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine

def test_descanso_query():
    """Test the specific query about descanso mínimo."""
    print("🔍 Testing: '¿Cuál es el descanso mínimo entre turnos?'\n")
    db = SessionLocal()
    
    query = "descanso mínimo entre turnos"
    company = "azul"  # From the screenshot
    
    print(f"Query: {query}")
    print(f"Company: {company}\n")
    
    # Test 1: Company-specific search
    print("="*60)
    print("Test 1: Company-specific search (azul)")
    print("="*60)
    results = rag_engine.search(query, company_slug=company, db=db, limit=5)
    
    if results:
        print(f"✅ Found {len(results)} results\n")
        for i, r in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Article: {r.get('article_ref', 'N/A')}")
            print(f"  Content length: {len(r.get('content', ''))} chars")
            print(f"  Preview: {r.get('content', '')[:200]}...")
            print()
    else:
        print("❌ No results found for company-specific search\n")
    
    # Test 2: Global search (without company filter)
    print("="*60)
    print("Test 2: Global search (no company filter)")
    print("="*60)
    results_global = rag_engine.search(query, db=db, limit=5)
    
    if results_global:
        print(f"✅ Found {len(results_global)} results\n")
        for i, r in enumerate(results_global, 1):
            print(f"Result {i}:")
            print(f"  Article: {r.get('article_ref', 'N/A')}")
            print(f"  Document: {r.get('document_id', 'N/A')}")
            print(f"  Content length: {len(r.get('content', ''))} chars")
            print(f"  Preview: {r.get('content', '')[:200]}...")
            print()
    else:
        print("❌ No results found for global search\n")
    
    # Test 3: Alternative queries
    print("="*60)
    print("Test 3: Alternative query variations")
    print("="*60)
    
    alternative_queries = [
        "descanso entre jornadas",
        "horas de descanso",
        "tiempo de descanso trabajadores",
        "artículo 34 estatuto trabajadores"
    ]
    
    for alt_query in alternative_queries:
        print(f"\nTrying: '{alt_query}'")
        alt_results = rag_engine.search(alt_query, db=db, limit=2)
        if alt_results:
            print(f"  ✅ Found {len(alt_results)} results")
            print(f"  Top: {alt_results[0].get('article_ref', 'N/A')}")
        else:
            print(f"  ❌ No results")
    
    db.close()

if __name__ == "__main__":
    test_descanso_query()
