
import sys
import os
import httpx
import time
from typing import List, Dict

# Add backend to path for direct service testing
sys.path.append(os.path.join(os.getcwd(), "backend"))

# API Base URL
API_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_api_health():
    print_section("1. API Health Check")
    try:
        response = httpx.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Root API: OK")
        else:
            print(f"❌ Root API Failed: {response.status_code}")
            
        # Check Convenios
        response = httpx.get(f"{API_URL}/convenios/")
        if response.status_code == 200:
            count = len(response.json())
            print(f"✅ Convenios Endpoint: OK ({count} companies found)")
            return count > 0
        else:
            print(f"❌ Convenios Endpoint Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_rag_search(query: str, company_slug: str = None, category: str = None):
    print(f"\n🔍 Searching for: '{query}' [Company: {company_slug}, Category: {category}]")
    try:
        # TEST 1: Semantic Search (GET)
        params = {"q": query}
        print(f"   [GET] /articulos/search")
        response = httpx.get(f"{API_URL}/articulos/search/", params=params) # Note trailing slash might be needed
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            print(f"   ✅ Search OK: {len(results)} chunks found")
        else:
            print(f"   ❌ Search Failed: {response.status_code}")

        # TEST 2: Chat RAG (POST)
        print(f"   [POST] /articulos/search/chat")
        payload = {
            "query": query,
            "company_slug": company_slug,
        }
        response_chat = httpx.post(f"{API_URL}/articulos/search/chat", json=payload)
        
        if response_chat.status_code == 200:
            data = response_chat.json()
            answer = data.get("answer", "")[:100] + "..."
            print(f"   ✅ Chat OK: {answer}")
        else:
            print(f"   ❌ Chat Failed: {response_chat.status_code} - {response_chat.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def run_all_tests():
    print("🚀 Starting System Verification")
    
    # 1. Health
    if not test_api_health():
        print("\n⛔ Critical: API is not healthy. Aborting.")
        return

    print_section("2. RAG Search Verification")
    
    # 2. General Query
    test_rag_search("vacaciones", company_slug="general")
    
    # 3. Specific Company Query (Iberia)
    test_rag_search("incremento salarial", company_slug="iberia")
    
    # 4. Specific Company Query (Groundforce)
    test_rag_search("jornada laboral", company_slug="groundforce")
    
    # 5. Jurisprudencia
    test_rag_search("subrogación", category="Jurisprudencia")
    
    # 6. Estatuto
    test_rag_search("despido improcedente", company_slug="estatuto", category="Legislación")

if __name__ == "__main__":
    run_all_tests()
