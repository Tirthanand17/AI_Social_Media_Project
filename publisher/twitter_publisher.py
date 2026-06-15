from pathlib import Path
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def publish(caption, media_url=None, dry_run=None):
    if dry_run is None:
        dry_run = os.getenv("POSTING_MODE", "dry_run") == "dry_run"

    result = {
        "platform": "X",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(os.getenv("X_BEARER_TOKEN", "")),
    }
    if dry_run:
        result.update({"status": "dry_run_success", "message": "X API credentials are stored locally; live posting is disabled by POSTING_MODE."})
        return result

    result.update({
        "status": "needs_user_context",
        "message": "X posting requires user-context OAuth credentials with write permission. The current bearer token is useful for read/status checks, not safe live posting.",
    })
    return result


def credential_status():
    return {
        "platform": "X",
        "api_key": "configured" if os.getenv("X_API_KEY", "") else "missing",
        "api_secret": "configured" if os.getenv("X_API_SECRET", "") else "missing",
        "bearer_token": "configured" if os.getenv("X_BEARER_TOKEN", "") else "missing",
        "live_ready": False,
        "note": "Live posting needs OAuth user access token and token secret with write permission.",
    }


def bearer_status():
    token = os.getenv("X_BEARER_TOKEN", "")
    if not token:
        return {"configured": False, "status": "missing_token"}
    response = requests.get(
        "https://api.x.com/2/tweets/search/recent?query=from:XDevelopers&max_results=10",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    return {"configured": True, "status_code": response.status_code, "ok": response.status_code < 400}
