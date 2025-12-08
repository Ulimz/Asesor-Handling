from app.db.database import DATABASE_URL, engine
from sqlalchemy import text
import os
import sys

# Print encoding info
print(f"System encoding: {sys.getdefaultencoding()}")
print(f"Stdout encoding: {sys.stdout.encoding}")

print(f"DEBUG: DATABASE_URL read by app: {DATABASE_URL}")

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"✅ Connection Successful: {result.fetchone()}")
except Exception as e:
    print("❌ SQLAlchemy Connection Failed")
    print(f"Error Type: {type(e)}")
    try:
        print(f"Error Message: {str(e)}")
    except:
        print("Could not decode error message")
