import os
import time

# This script touches main.py to trigger auto-reload
file_path = "backend/app/main.py"
print(f"Touching {file_path} to trigger reload...")
current_time = time.time()
os.utime(file_path, (current_time, current_time))
print("Done.")
