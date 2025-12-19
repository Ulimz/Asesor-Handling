#!/usr/bin/env python3
"""
Test production API directly
"""
import requests
import json

API_URL = "https://asistente-handling-production.up.railway.app"

# Get auth token (you'll need to replace with a valid token)
print("Testing EasyJet calculator in PRODUCTION\n")

# Test data
payload = {
    "company_slug": "easyjet",
    "user_level": "Agente de Rampa",  # Category
    "user_group": "Nivel 3",  # Level
    "gross_annual_salary": 0,
    "payments": 14,
    "contract_percentage": 100,
    "dynamic_variables": {
        "PLUS_HORA_PERENTORIA": 10
    }
}

print("Request payload:")
print(json.dumps(payload, indent=2))
print("\nSending request to production API...")

try:
    response = requests.post(
        f"{API_URL}/api/calculator/calculate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print(f"\nTotal: {result['gross_monthly_total']}€")
        print("\nBreakdown:")
        for item in result['breakdown']:
            print(f"  - {item['name']}: {item['amount']}€")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
