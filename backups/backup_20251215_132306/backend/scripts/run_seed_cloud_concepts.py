import os
import sys
from dotenv import load_dotenv

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_path)

# Load .env explicitly
env_path = os.path.join(backend_path, '.env')
load_dotenv(env_path)

# Ensure DATABASE_URL is set (prioritize CLOUD_DATABASE_URL if available)
if os.getenv("CLOUD_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.getenv("CLOUD_DATABASE_URL")

# Fix scheme if needed
if os.getenv("DATABASE_URL", "").startswith("postgres://"):
    os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)

print(f"✅ Loaded Environment. Target DB: {os.getenv('DATABASE_URL')[:30]}...")

try:
    # Use the logic from seed_concepts.py
    from scripts.seed_concepts import seed_concepts
    print("🚀 Starting Concept Seeding...")
    seed_concepts()
    print("✅ Concept Seeding Completed.")
except Exception as e:
    print(f"❌ Error during seeding: {e}")
    import traceback
    traceback.print_exc()
