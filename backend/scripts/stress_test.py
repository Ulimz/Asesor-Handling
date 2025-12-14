import requests
import json
from tabulate import tabulate

BASE_URL = "http://localhost:8000/api/articulos/search/chat"

SCENARIOS = [
    {
        "company": "iberia",
        "description": "Bolsa de Empleo (Complex Procedure)",
        "query": "¿Cómo funciona el orden de llamamiento de la bolsa de empleo eventual? ¿Qué pasa si rechazo un contrato?"
    },
    {
        "company": "General", 
        "description": "Subrogación (Sector Wide Logic)",
        "query": "Mi empresa ha perdido la licencia. ¿La nueva empresa está obligada a subrogarme? ¿Mantengo mi antigüedad y salario?"
    },
    {
        "company": "menzies",
        "description": "Cambios de Turno (Company Specific)",
        "query": "¿Puedo cambiar el turno con un compañero? ¿Con cuánta antelación debo pedirlo?"
    }
]

print(f"\n🚀 STARTING STRESS TEST on {BASE_URL}\n")

results = []

for sc in SCENARIOS:
    print(f"Testing Scenario: {sc['description']} ({sc['company']})...")
    
    payload = {
        "query": sc["query"],
        "history": [],
        "company_slug": sc["company"]
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        answer = data.get("answer", "No answer provided")
        sources = data.get("sources", [])
        
        # Check source quality
        source_titles = [s.get('article_ref', 'Unknown')[:20] for s in sources]
        
        print(f"✅ Status: {response.status_code}")
        print(f"📝 Answer: {answer[:150]}...")
        print(f"📚 Sources: {source_titles}\n")
        
        results.append([sc['company'], sc['description'], "PASS" if len(sources) > 0 else "FAIL", len(sources)])
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        results.append([sc['company'], sc['description'], "ERROR", 0])

print("\n--- TEST SUMMARY ---")
print(tabulate(results, headers=["Company", "Scenario", "Status", "Docs"], tablefmt="grid"))
