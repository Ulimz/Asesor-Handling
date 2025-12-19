#!/usr/bin/env python3
"""
Test production API directly
"""
import requests
import json

API_URL = "https://intelligent-vitality-production.up.railway.app"

# Test data
payload = {
    "company_slug": "easyjet",
    "user_level": "Agente de Rampa",
    "user_group": "Nivel 3",
    "gross_annual_salary": 0,
    "payments": 14,
    "contract_percentage": 100
}

print(f"Testing {API_URL}...")
try:
    response = requests.post(f"{API_URL}/api/calculadoras/smart", json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error: {e}")
