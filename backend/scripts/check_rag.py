import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv(os.path.join('backend', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = os.getenv("CLOUD_DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def check_rag_status():
    print(f"Connecting to DB...")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # 1. Check pgvector extension
            print("1. Checking pgvector extension...")
            result = connection.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
            if result.fetchone():
                print("   ✅ pgvector is INSTALLED.")
            else:
                print("   ❌ pgvector is NOT installed.")
            
            # 2. Check Articles count
            print("\n2. Checking Article count...")
            result = connection.execute(text("SELECT count(*) FROM articulos;"))
            count = result.scalar()
            print(f"   📊 Total Articles: {count}")
            
            # 3. Check Embeddings
            if count > 0:
                print("\n3. Checking Embeddings (sample)...")
                # Check if embedding column is not null
                result = connection.execute(text("SELECT count(*) FROM articulos WHERE embedding IS NOT NULL;"))
                embedded_count = result.scalar()
                print(f"   🧠 Articles with Embeddings: {embedded_count}")
                
                if embedded_count == 0:
                    print("   ❌ NO EMBEDDINGS FOUND. Search will fail.")
                elif embedded_count < count:
                    print(f"   ⚠️ PARTIAL EMBEDDINGS. {count - embedded_count} articles missing vector data.")
                else:
                    print("   ✅ All articles have embeddings.")
            else:
                print("   ❌ No articles found. Database is empty.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_rag_status()
