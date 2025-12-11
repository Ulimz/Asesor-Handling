import requests
import json
import random

# Use a random email to avoid collision on repeated runs
rand_id = random.randint(1000, 9999)
email = f"test_auto_{rand_id}@example.com"
password = "password123"

url = "https://intelligent-vitality-production.up.railway.app/api/users/"
# No trailing slash on url because we fixed the code to remove it, right? 
# Wait, the script will post to /api/users directly.

payload = {
    "email": email,
    "full_name": "Test Auto User",
    "password": password,
    "company_slug": "iberia", # Assuming 'iberia' exists from previous checks/context
    "preferred_name": "Test",
    "job_group": "Administrativo",
    "salary_level": 1,
    "contract_type": "Fijo",
    "is_active": True
}

headers = {
    "Content-Type": "application/json",
    # Simulate origin to check CORS/Whitelisting if backend enforces it strictly
    "Origin": "https://asesor-handling-production.up.railway.app" 
}

print(f"Creating user: {email}")
try:
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS! User created.")
        print(response.json())
    else:
        print("❌ FAILED")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
