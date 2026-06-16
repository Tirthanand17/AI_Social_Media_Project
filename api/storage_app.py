from pathlib import Path
import sys

from fastapi import FastAPI

ROOT = Path(__file__).resolve().parents[1]
for p in [ROOT, ROOT / "api"]:
    sys.path.append(str(p))

from storage_api import router as storage_router

app = FastAPI(title="AI Social Studio Storage API", version="1.0.0")
app.include_router(storage_router)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "SQLite storage API is running",
        "docs": "/docs",
        "init_db": "/api/db/init",
        "posts": "/api/db/posts",
        "schedule": "/api/db/schedule",
        "reschedule": "/api/db/reschedule",
        "schedules": "/api/db/schedules",
    }
