import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path=Path("../.env")) 
load_dotenv(dotenv_path=Path(".env"))

user = os.getenv('POSTGRES_USER', 'usuario')
password = os.getenv('POSTGRES_PASSWORD', 'password')
host = "127.0.0.1" # Force IPv4
port = os.getenv('POSTGRES_PORT', '5440') 
dbname = os.getenv('POSTGRES_DB', 'asistentehandling')

print(f"Connecting to: {user}:***@{host}:{port}/{dbname}")

try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name = 'vector';")
    print(f"pg_available_extensions (vector): {cur.fetchone()}")


    cur.execute("SELECT typname FROM pg_type WHERE typname = 'vector';")
    print(f"Vector Type Found: {cur.fetchone()}")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
