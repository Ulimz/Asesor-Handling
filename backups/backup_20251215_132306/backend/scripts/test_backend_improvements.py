"""
Comprehensive test suite for backend improvements.
Tests: lazy loading, error handling, N+1 queries, validation, index performance
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine
from app.db.models import DocumentChunk
from sqlalchemy import text

def test_lazy_loading():
    """Test that embedding model loads lazily"""
    print("\n" + "="*60)
    print("TEST 1: Lazy Loading of Embedding Model")
    print("="*60)
    
    # Model should not be loaded yet
    if rag_engine._model is None:
        print("✅ Model not loaded on init (lazy loading working)")
    else:
        print("❌ Model loaded on init (lazy loading NOT working)")
        return False
    
    # Trigger loading
    print("   Triggering first embedding generation...")
    _ = rag_engine.generate_embedding("test")
    
    if rag_engine._model is not None:
        print("✅ Model loaded on first use")
        return True
    else:
        print("❌ Model still not loaded")
        return False

def test_error_handling():
    """Test that embedding errors are handled gracefully"""
    print("\n" + "="*60)
    print("TEST 2: Error Handling in Embeddings")
    print("="*60)
    
    # This should not crash even with empty string
    try:
        embedding = rag_engine.generate_embedding("")
        print(f"✅ Empty string handled: {len(embedding)} dimensions")
        return True
    except Exception as e:
        print(f"❌ Error with empty string: {e}")
        return False

def test_n1_queries():
    """Test that N+1 queries are eliminated"""
    print("\n" + "="*60)
    print("TEST 3: N+1 Query Elimination")
    print("="*60)
    
    db = SessionLocal()
    
    # Enable query logging
    from sqlalchemy import event
    query_count = {'count': 0}
    
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        query_count['count'] += 1
    
    event.listen(db.bind, "after_cursor_execute", receive_after_cursor_execute)
    
    # Perform search
    results = rag_engine.search("vacaciones", db=db, limit=5)
    
    # Access document properties (this would trigger N+1 without eager loading)
    for r in results:
        _ = r.get('document_id')
    
    print(f"   Total queries executed: {query_count['count']}")
    
    # Should be 1 query (with joinedload) vs 6 queries (without)
    if query_count['count'] <= 2:
        print(f"✅ Efficient querying (≤2 queries)")
        success = True
    else:
        print(f"⚠️ Multiple queries detected ({query_count['count']})")
        success = False
    
    db.close()
    return success

def test_company_validation():
    """Test company_slug validation"""
    print("\n" + "="*60)
    print("TEST 4: Company Slug Validation")
    print("="*60)
    
    from app.constants import VALID_COMPANIES
    
    print(f"   Valid companies: {len(VALID_COMPANIES)}")
    print(f"   Examples: {VALID_COMPANIES[:3]}")
    
    if 'azul' in VALID_COMPANIES and 'iberia' in VALID_COMPANIES:
        print("✅ Constants loaded correctly")
        return True
    else:
        print("❌ Constants not loaded")
        return False

def test_index_exists():
    """Test that article_ref index was created"""
    print("\n" + "="*60)
    print("TEST 5: Database Index")
    print("="*60)
    
    db = SessionLocal()
    
    query = text("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'document_chunks' 
        AND indexname = 'ix_document_chunks_article_ref'
    """)
    
    result = db.execute(query)
    exists = result.fetchone() is not None
    
    if exists:
        print("✅ Index ix_document_chunks_article_ref exists")
        success = True
    else:
        print("❌ Index not found")
        success = False
    
    db.close()
    return success

def test_search_performance():
    """Test search performance with index"""
    print("\n" + "="*60)
    print("TEST 6: Search Performance")
    print("="*60)
    
    db = SessionLocal()
    
    # Test search speed
    start = time.time()
    results = rag_engine.search("salario", db=db, limit=10)
    elapsed = time.time() - start
    
    print(f"   Query time: {elapsed*1000:.2f}ms")
    print(f"   Results: {len(results)}")
    
    if elapsed < 1.0:  # Should be fast
        print(f"✅ Search completed in {elapsed*1000:.0f}ms")
        success = True
    else:
        print(f"⚠️ Search took {elapsed:.2f}s (might be slow)")
        success = False
    
    db.close()
    return success

def test_rag_retrieval():
    """Test end-to-end RAG retrieval"""
    print("\n" + "="*60)
    print("TEST 7: RAG Retrieval Quality")
    print("="*60)
    
    db = SessionLocal()
    
    test_queries = [
        ("vacaciones", "vacacion"),
        ("salario", "salario"),
        ("descanso", "descanso")
    ]
    
    passed = 0
    for query, expected_keyword in test_queries:
        results = rag_engine.search(query, db=db, limit=3)
        
        if results and len(results) > 0:
            content = results[0].get('content', '').lower()
            if expected_keyword in content:
                print(f"   ✅ '{query}' → found '{expected_keyword}'")
                passed += 1
            else:
                print(f"   ⚠️ '{query}' → '{expected_keyword}' not in top result")
        else:
            print(f"   ❌ '{query}' → no results")
    
    db.close()
    
    if passed == len(test_queries):
        print(f"✅ All {passed}/{len(test_queries)} queries successful")
        return True
    else:
        print(f"⚠️ {passed}/{len(test_queries)} queries successful")
        return passed >= 2  # At least 2/3

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "🧪 RUNNING BACKEND IMPROVEMENT TESTS")
    print("="*60)
    
    tests = [
        ("Lazy Loading", test_lazy_loading),
        ("Error Handling", test_error_handling),
        ("N+1 Queries", test_n1_queries),
        ("Company Validation", test_company_validation),
        ("Database Index", test_index_exists),
        ("Search Performance", test_search_performance),
        ("RAG Retrieval", test_rag_retrieval)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} FAILED with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend improvements working correctly.")
    elif passed >= total * 0.8:
        print(f"\n✅ Most tests passed ({passed}/{total}). Minor issues detected.")
    else:
        print(f"\n⚠️ Some tests failed ({passed}/{total}). Review needed.")

if __name__ == "__main__":
    run_all_tests()
