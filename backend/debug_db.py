import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("POSTGRES_HOST", "localhost")
db = os.getenv("POSTGRES_DB", "asistentehandling")
user = os.getenv("POSTGRES_USER", "usuario")
password = os.getenv("POSTGRES_PASSWORD", "12345")

print(f"Testing connection to: {db} as {user} on {host}...")

try:
    conn = psycopg2.connect(
        host=host,
        database=db,
        user=user,
        password=password
    )
    print("✅ Connection SUCCESSFUL!")
    conn.close()
except Exception as e:
    print("❌ Connection FAILED")
    print(f"Error Type: {type(e)}")
    # Print repr to avoid UnicodeDecodeError if the message has weird bytes
    print(f"Error Details (repr): {repr(e)}")
    
    # Try to decode safely
    try:
        print(f"Error Message: {str(e)}")
    except:
        print("Could not decode error message string.")
