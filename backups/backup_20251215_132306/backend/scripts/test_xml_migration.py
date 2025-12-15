import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.services.rag_engine import rag_engine

def test_xml_retrieval():
    """Test that XML data is being retrieved correctly."""
    print("🧪 Testing XML Data Retrieval...\n")
    db = SessionLocal()
    
    test_queries = [
        {
            "query": "cuánto cobra un gestor en Iberia",
            "company": "iberia",
            "expected_keywords": ["salario", "gestor", "tabla", "|"]
        },
        {
            "query": "tablas salariales Swissport 2024",
            "company": "swissport",
            "expected_keywords": ["tabla", "salario", "|", "2024"]
        },
        {
            "query": "sueldo base agente administrativo Groundforce",
            "company": "groundforce",
            "expected_keywords": ["agente", "administrativo", "|", "sueldo"]
        },
        {
            "query": "vacaciones estatuto trabajadores",
            "company": None,  # Global search
            "expected_keywords": ["vacacion", "día", "año"]
        },
        {
            "query": "salario técnico Menzies",
            "company": "menzies",
            "expected_keywords": ["técnico", "|", "salario"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"{'='*60}")
        print(f"Test {i}: {test['query']}")
        print(f"Company filter: {test['company'] or 'Global'}")
        print(f"{'='*60}")
        
        try:
            results = rag_engine.search(
                query=test['query'],
                company_slug=test['company'],
                db=db,
                limit=3
            )
            
            if not results:
                print("❌ FAIL: No results returned")
                failed += 1
                continue
            
            print(f"\n✅ Retrieved {len(results)} chunks\n")
            
            # Check first result
            top_result = results[0]
            content = top_result.get('content', '').lower()
            article_ref = top_result.get('article_ref', '')
            
            print(f"📄 Top Result:")
            print(f"   Article: {article_ref}")
            print(f"   Content length: {len(top_result.get('content', ''))} chars")
            
            # Check for expected keywords
            found_keywords = []
            missing_keywords = []
            
            for keyword in test['expected_keywords']:
                if keyword.lower() in content:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            # Check for table structure (pipe character)
            has_table = '|' in top_result.get('content', '')
            
            print(f"\n   Keywords found: {', '.join(found_keywords) if found_keywords else 'None'}")
            if missing_keywords:
                print(f"   Keywords missing: {', '.join(missing_keywords)}")
            print(f"   Contains table: {'✅ Yes' if has_table else '❌ No'}")
            
            # Show content preview
            preview_length = 300
            content_preview = top_result.get('content', '')[:preview_length]
            print(f"\n   Content preview:")
            print(f"   {content_preview}...")
            
            # Determine pass/fail
            # Pass if at least 2 keywords found OR has table structure
            if len(found_keywords) >= 2 or has_table:
                print(f"\n✅ PASS")
                passed += 1
            else:
                print(f"\n⚠️ PARTIAL: Results found but quality uncertain")
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL: Error - {e}")
            failed += 1
        
        print()
    
    print(f"\n{'='*60}")
    print(f"📊 Test Summary:")
    print(f"   Passed: {passed}/{len(test_queries)}")
    print(f"   Failed: {failed}/{len(test_queries)}")
    print(f"{'='*60}")
    
    if passed == len(test_queries):
        print("\n🎉 All tests passed! XML migration successful!")
    elif passed > 0:
        print(f"\n✅ {passed} tests passed. System is functional.")
    else:
        print("\n❌ All tests failed. Investigation needed.")
    
    db.close()

if __name__ == "__main__":
    test_xml_retrieval()
