"""
Database initialization script.
Creates all tables and enables pgvector extension.
"""
from app.db.database import engine
from app.db.models import Base
from sqlalchemy import text

def init_db():
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_db()
