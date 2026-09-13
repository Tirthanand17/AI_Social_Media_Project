from pathlib import Path
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _is_dry_run(dry_run=None) -> bool:
    if dry_run is not None:
        return bool(dry_run)
    return _env("POSTING_MODE", "dry_run").lower() != "live"


def _graph_url(path: str) -> str:
    version = _env("META_GRAPH_VERSION")
    prefix = f"/{version.strip('/')}" if version else ""
    return f"https://graph.facebook.com{prefix}/{path.lstrip('/')}"


def publish(caption, media_url=None, dry_run=None):
    """Publish a Facebook Page feed post, or safely preview it in dry-run mode."""
    dry_run = _is_dry_run(dry_run)
    caption = str(caption or "").strip()
    token = _env("FACEBOOK_ACCESS_TOKEN")
    page_id = _env("FACEBOOK_PAGE_ID")

    result = {
        "platform": "Facebook",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(token and page_id),
        "mode": "dry_run" if dry_run else "live",
    }
    if not caption:
        result.update({"status": "empty_caption", "message": "Caption is required before publishing."})
        return result
    if dry_run:
        result.update({"status": "dry_run_success", "message": "Facebook preview only. Set POSTING_MODE=live to publish."})
        return result
    if not token or not page_id:
        result.update({"status": "missing_credentials", "message": "Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID before live posting."})
        return result

    payload = {"message": caption, "access_token": token}
    if media_url:
        payload["link"] = str(media_url)

    try:
        response = requests.post(_graph_url(f"{page_id}/feed"), data=payload, timeout=25)
    except requests.RequestException as exc:
        result.update({"status": "facebook_network_error", "message": str(exc)[:500]})
        return result

    data = response.json() if response.text else {}
    if response.status_code >= 400 or data.get("error"):
        result.update({"status": "facebook_error", "status_code": response.status_code, "message": str(data.get("error") or response.text)[:800]})
        return result

    result.update({"status": "published", "status_code": response.status_code, "post_id": data.get("id"), "response": data})
    return result


def credential_status():
    token = bool(_env("FACEBOOK_ACCESS_TOKEN"))
    page_id = bool(_env("FACEBOOK_PAGE_ID"))
    return {
        "platform": "Facebook",
        "access_token": "configured" if token else "missing",
        "page_id": "configured" if page_id else "missing",
        "posting_mode": _env("POSTING_MODE", "dry_run"),
        "live_ready": bool(token and page_id),
    }
