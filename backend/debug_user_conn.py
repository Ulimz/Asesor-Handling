import psycopg2
import os

# Hardcoded params to match .env expectation
host = "localhost"
port = 5433
db = "asistentehandling"
user = "usuario"
password = "12345"

print(f"Testing direct psycopg2 connection to: {db} as {user} on {host}:{port}...")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=db,
        user=user,
        password=password
    )
    print("✅ Direct Connection SUCCESSFUL!")
    conn.close()
except Exception as e:
    print("❌ Direct Connection FAILED")
    try:
        # Attempt to decode error explicitly as Windows-1252/cp1252 if it's failing default decode
        raw_msg = str(e)
        print(f"Error Message (str): {raw_msg}")
    except UnicodeDecodeError:
         print("Error Message could not be decoded as UTF-8.")
         # In Python 3 catch block, 'e' might already have issues if its __str__ assumes encoding
         # But usually raw bytes are in e.args or similar.
    
    print(f"Error Args: {e.args}")
