
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Path to backend
backend_path = Path(__file__).resolve().parent

# Load .env
load_dotenv(backend_path / ".env")

DATABASE_URL = os.getenv('CLOUD_DATABASE_URL') or os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    print("Error: No DATABASE_URL found in .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

print("--- Data Check for azul-handling in PostgreSQL ---")
query = text('''
SELECT "group", level, concept, amount 
FROM salary_tables 
WHERE company_id = 'azul-handling'
AND concept IN ('HORA_EXTRA', 'HORA_PERENTORIA', 'HORA_COMPLEMENTARIA_ESP', 'SALARIO_BASE')
LIMIT 40
''')

try:
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
        print(f"Found {len(rows)} records.")
        print("| Group | Level | Concept | Amount |")
        print("|---|---|---|---|")
        for r in rows:
            print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")
except Exception as e:
    print(f"Error executing query: {e}")
