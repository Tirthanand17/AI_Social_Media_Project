from datetime import datetime, timedelta
from pathlib import Path
import os
import shutil
import subprocess
import time

import schedule
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BACKUP_DIR = ROOT / "backups"
load_dotenv(ROOT / ".env")


def _stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_data_files():
    """Back up CSV/SQLite demo data without touching source datasets."""
    target = BACKUP_DIR / f"data_backup_{_stamp()}"
    target.mkdir(parents=True, exist_ok=True)

    copied = []
    for pattern in ("*.csv", "*.db", "*.sqlite", "*.sqlite3"):
        for source in DATA_DIR.rglob(pattern):
            if ".ipynb_checkpoints" in source.parts:
                continue
            destination = target / source.relative_to(DATA_DIR)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(str(destination.relative_to(ROOT)))

    return {"status": "success", "backup_dir": str(target), "files_copied": len(copied), "files": copied}


def backup_mysql_database():
    """Create a mysqldump when MySQL credentials and mysqldump are available."""
    host = os.getenv("DB_HOST", "").strip()
    port = os.getenv("DB_PORT", "3306").strip()
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "").strip()

    if not all([host, user, database]):
        return {"status": "skipped", "message": "MySQL credentials are not configured."}
    executable = shutil.which("mysqldump")
    if not executable:
        return {"status": "skipped", "message": "mysqldump is not installed on this machine."}

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    destination = BACKUP_DIR / f"mysql_{database}_{_stamp()}.sql"
    command = [
        executable,
        "--single-transaction",
        "--routines",
        "--triggers",
        "-h", host,
        "-P", port,
        "-u", user,
        database,
    ]
    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password

    try:
        with destination.open("wb") as output:
            result = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, env=env, check=False, timeout=300)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        return {"status": "error", "message": str(exc)[:500]}

    if result.returncode != 0:
        destination.unlink(missing_ok=True)
        return {"status": "error", "message": result.stderr.decode("utf-8", errors="replace")[:800]}
    return {"status": "success", "backup_file": str(destination)}


def cleanup_old_backups(keep_days=30):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=max(1, int(keep_days)))
    deleted = []
    for item in BACKUP_DIR.iterdir():
        try:
            modified = datetime.fromtimestamp(item.stat().st_mtime)
        except OSError:
            continue
        if modified >= cutoff:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink(missing_ok=True)
        deleted.append(item.name)
    return {"status": "success", "deleted": deleted}


def backup_all():
    result = {
        "demo_data": backup_data_files(),
        "mysql": backup_mysql_database(),
        "cleanup": cleanup_old_backups(int(os.getenv("BACKUP_RETENTION_DAYS", "30"))),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    return result


def configure_nightly_schedule():
    at = os.getenv("BACKUP_TIME", "02:00")
    schedule.every().day.at(at).do(backup_all)
    return {"status": "scheduled", "time": at}


def run_backup_loop():
    configure_nightly_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    print(backup_all())
