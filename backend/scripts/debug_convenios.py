
import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.database import SessionLocal
from app.modules.convenios.models import Convenio
from sqlalchemy import text

def verify():
    db = SessionLocal()
    try:
        # Check if table exists
        try:
            count = db.query(Convenio).count()
            print(f"Convenios count: {count}")
            for c in db.query(Convenio).all():
                print(f" - {c.name} ({c.slug})")
        except Exception as e:
            print(f"Error querying Convenio: {e}")
            
    finally:
        db.close()

    # Test API
    import httpx
    try:
        print("\nTesting API Endpoint...")
        response = httpx.get("http://localhost:8000/convenios/")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            print("API OK")
    except Exception as e:
        print(f"API Request Failed: {e}")

if __name__ == "__main__":
    verify()
