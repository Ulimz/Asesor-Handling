"""
Test RAG API with real queries to verify end-to-end functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_api():
    """Test the /articulos/search/chat endpoint"""
    print("\n" + "="*60)
    print("🌐 TESTING RAG API ENDPOINT")
    print("="*60)
    
    test_cases = [
        {
            "query": "¿Cuántos días de vacaciones tengo?",
            "company_slug": "azul",
            "expected_keywords": ["vacacion", "día"]
        },
        {
            "query": "¿Cómo se pagan las horas extra?",
            "company_slug": "iberia",
            "expected_keywords": ["hora", "extra"]
        },
        {
            "query": "¿Cuál es el descanso mínimo entre turnos?",
            "company_slug": "azul",
            "expected_keywords": ["descanso", "hora"]
        }
    ]
    
    passed = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        print(f"Company: {test['company_slug']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/articulos/search/chat",
                json={
                    "query": test['query'],
                    "company_slug": test['company_slug'],
                    "history": []
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '').lower()
                sources = data.get('sources', [])
                
                print(f"   Status: ✅ {response.status_code}")
                print(f"   Sources: {len(sources)} chunks")
                print(f"   Answer length: {len(answer)} chars")
                
                # Check if answer contains expected keywords
                found_keywords = [kw for kw in test['expected_keywords'] if kw in answer]
                
                if found_keywords:
                    print(f"   Keywords found: {', '.join(found_keywords)}")
                    print(f"   Answer preview: {answer[:150]}...")
                    
                    # Check if it's not a "no tengo información" response
                    if "no tengo" not in answer and "no he encontrado" not in answer:
                        print(f"   ✅ PASS: Got relevant answer")
                        passed += 1
                    else:
                        print(f"   ⚠️ PARTIAL: Answer says 'no information'")
                else:
                    print(f"   ⚠️ PARTIAL: Keywords not in answer")
                    print(f"   Answer: {answer[:200]}...")
            else:
                print(f"   ❌ FAIL: Status {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"API Tests: {passed}/{len(test_cases)} passed")
    print(f"{'='*60}")
    
    return passed, len(test_cases)

if __name__ == "__main__":
    passed, total = test_chat_api()
    
    if passed == total:
        print("\n🎉 All API tests passed!")
    elif passed > 0:
        print(f"\n✅ {passed}/{total} API tests passed")
    else:
        print("\n❌ All API tests failed - check backend logs")
