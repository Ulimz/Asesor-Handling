import requests

url = "https://intelligent-vitality-production.up.railway.app/api/users"
origin = "https://asesor-handling-production.up.railway.app"

try:
    print(f"Testing OPTIONS request to {url}")
    print(f"Origin: {origin}")
    response = requests.options(
        url,
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for k, v in response.headers.items():
        if 'access-control' in k.lower():
            print(f"  {k}: {v}")
            
    if response.status_code == 200 and 'Access-Control-Allow-Origin' in response.headers:
        print("\n✅ CORS SUCCESS!")
    else:
        print("\n❌ CORS FAILED or Invalid Response")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
