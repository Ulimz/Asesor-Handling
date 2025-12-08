import psycopg2
import os

# Testing POSTGRES user
host = "127.0.0.1"
port = 5433
db = "postgres"
user = "postgres"
password = "123456"

print(f"Testing SUPERUSER connection to: {db} as {user} on {host}:{port}...")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=db,
        user=user,
        password=password
    )
    print("✅ Superuser Connection SUCCESSFUL!")
    conn.close()
except Exception as e:
    print("❌ Superuser Connection FAILED")
    try:
        print(f"Error Message (str): {str(e)}")
    except:
         print("Error string decode failed.")
