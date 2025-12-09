import traceback
print("Starting import check...")
try:
    from app import main
    print("Import Success")
except Exception:
    print("Import Failed - Traceback:")
    traceback.print_exc()
