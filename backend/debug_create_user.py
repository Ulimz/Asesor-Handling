import requests
import json

URL = "http://127.0.0.1:8000/api/users/"
DATA = {
    "email": "test_debug@example.com",
    "full_name": "Debug User",
    "password": "password123",
    "is_active": True
}

try:
    print(f"Testing direct connection to: {URL}")
    response = requests.post(URL, json=DATA)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
