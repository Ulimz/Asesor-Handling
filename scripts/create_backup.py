import shutil
import os
import datetime
from pathlib import Path

def make_backup():
    root_dir = Path("c:/Users/ulise/Programas Uli/Asistente_Handling")
    backup_folder = root_dir / "backups"
    backup_folder.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = backup_folder / f"backup_full_{timestamp}"
    
    print(f"📦 Starting backup to: {output_filename}.zip")
    
    # Define ignore pattern
    def ignore_patterns(path, names):
        wont_copy = []
        for name in names:
            if name in ['node_modules', '.venv', '.git', '__pycache__', '.next', 'out', 'backups', 'auditoria_resultados']:
                wont_copy.append(name)
            elif name.endswith('.pyc') or name.endswith('.zip'):
                wont_copy.append(name)
        return wont_copy

    try:
        shutil.make_archive(
            str(output_filename), 
            'zip', 
            root_dir, 
            base_dir=".",
            verbose=1
        )
        print("✅ Backup created successfully!")
        return str(output_filename) + ".zip"
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    make_backup()
