
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("No DATABASE_URL set.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def clean_pollution():
    # Concepts that are Leveled (Valid in SalaryTable)
    valid_leveled = [
        "SALARIO_BASE", "SALARIO_BASE_ANUAL",
        "HORA_EXTRA",
        "HORA_PERENTORIA", 
        "HORA_COMPLEMENTARIA_ESP"
    ]
    
    # We want to DELETE everything else for azul-handling in salary_tables
    # To be safe, we delete known polluted concepts explicitly or NOT IN list.
    # Let's delete NOT IN list.
    
    val_str = "', '".join(valid_leveled)
    query = f"DELETE FROM salary_tables WHERE company_id = 'azul-handling' AND concept NOT IN ('{val_str}')"
    
    print(f"Executing: {query}")
    with engine.connect() as conn:
        res = conn.execute(text(query))
        conn.commit()
        print(f"Deleted {res.rowcount} polluted rows.")

if __name__ == "__main__":
    clean_pollution()
