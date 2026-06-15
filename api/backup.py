from datetime import datetime
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BACKUP_DIR = ROOT / "backups"


def backup_data_files():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"data_backup_{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    copied = []
    for csv_file in DATA_DIR.rglob("*.csv"):
        if ".ipynb_checkpoints" in csv_file.parts:
            continue
        destination = target / csv_file.relative_to(DATA_DIR)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(csv_file, destination)
        copied.append(str(destination.relative_to(ROOT)))

    return {"status": "success", "backup_dir": str(target), "files_copied": len(copied), "files": copied}


if __name__ == "__main__":
    print(backup_data_files())
