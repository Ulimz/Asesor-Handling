import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup Environment to find backend modules
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

# Load .env
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# OVERRIDE DATABASE_URL with CLOUD_DATABASE_URL
cloud_db = os.getenv("CLOUD_DATABASE_URL")
if cloud_db:
    print("🌍 Targeting Cloud Database...")
    if cloud_db.startswith("postgres://"):
        cloud_db = cloud_db.replace("postgres://", "postgresql://", 1)
    os.environ["DATABASE_URL"] = cloud_db
else:
    print("⚠️ CLOUD_DATABASE_URL not found in .env. Falling back to local/default.")

# Now import and run the update function
try:
    from scripts.update_azul_prices import update_azul_prices
    print("🚀 Starting Cloud Price Update...")
    update_azul_prices()
    print("✅ Cloud Update Completed.")
except Exception as e:
    print(f"❌ Error during update: {e}")
