import os
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Prioritize a custom variable to bypass Railway's sticky DATABASE_URL issue if needed
DATABASE_URL = os.getenv('CLOUD_DATABASE_URL') or os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'usuario')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'asistentehandling')}"

# Sanitize URL for logging (hide password)
if '@' in DATABASE_URL:
    safe_url = DATABASE_URL.split('@')[1]  # Get host/db part only
    print(f"[DEBUG] DATABASE_HOST: {safe_url}")
else:
    print("[DEBUG] DATABASE_URL: configured")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
