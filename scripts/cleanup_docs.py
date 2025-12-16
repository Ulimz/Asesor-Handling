import os
import shutil
from pathlib import Path

# Config
ROOT_DIR = Path("c:/Users/ulise/Programas Uli/Asistente_Handling")
DOCS_ACTIVE = ROOT_DIR / "docs" / "active"
DOCS_DEPRECATED = ROOT_DIR / "docs" / "deprecated"

# Operations Map
# (Source, Destination)
MOVES = [
    ("GUIA_SOLUCION.md", DOCS_ACTIVE / "TROUBLESHOOTING_GUIDE.md"),
    ("SESSION_SUMMARY.md", DOCS_DEPRECATED / "SESSION_SUMMARY_OLD_20251216.md"),
    ("DOCKER_SETUP.md", DOCS_ACTIVE / "INFRA_DOCKER.md"),
]

# Deletes (only if exist in active/ already)
DUPLICATES_TO_CHECK = [
    "ANALYSIS_REPORT.md",
    "BACKEND_OVERVIEW.md"
]

def run():
    print("--- STARTING CLEANUP ---")
    
    # Ensure dirs exist
    DOCS_ACTIVE.mkdir(parents=True, exist_ok=True)
    DOCS_DEPRECATED.mkdir(parents=True, exist_ok=True)

    # 1. MOVES
    for src_name, dest_path in MOVES:
        src = ROOT_DIR / src_name
        if src.exists():
            try:
                shutil.move(str(src), str(dest_path))
                print(f"✅ MOVED: {src_name} -> {dest_path.name}")
            except Exception as e:
                print(f"❌ ERROR MOVING {src_name}: {e}")
        else:
            print(f"⚠️ SKIP: {src_name} not found in root.")

    # 2. DELETES (Duplicates)
    for name in DUPLICATES_TO_CHECK:
        src = ROOT_DIR / name
        dest = DOCS_ACTIVE / name
        
        if src.exists():
            # Check if exists in docs/active (exact name match check)
            # Actually dest might not exist if I just renamed it? 
            # No, these are different files. ANALYSIS_REPORT.md might be in docs/active.
            
            if dest.exists():
                # If content is identical, safe to delete. 
                # If different, we'll backup the root one to deprecated just in case.
                src_content = src.read_bytes()
                dest_content = dest.read_bytes()
                
                if src_content == dest_content:
                    src.unlink()
                    print(f"seguro DELETED: {name} (Identical content in docs/active)")
                else:
                    # Move to deprecated
                    backup_name = f"{name.replace('.md', '')}_OLD.md"
                    shutil.move(str(src), str(DOCS_DEPRECATED / backup_name))
                    print(f"⚠️ MOVED TO DEPRECATED: {name} (Content differed, safe backup kept)")
            else:
                # If not in active, move it to active!
                shutil.move(str(src), str(dest))
                print(f"✅ MOVED: {name} -> docs/active/ (Was missing there)")
        else:
            print(f"ℹ️ {name} not found in root.")
            
    print("--- CLEANUP COMPLETE ---")

if __name__ == "__main__":
    run()
