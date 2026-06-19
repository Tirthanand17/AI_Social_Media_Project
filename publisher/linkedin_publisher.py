from pathlib import Path
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _env(name, default=""):
    return os.getenv(name, default).strip()


def _is_dry_run(dry_run=None):
    if dry_run is not None:
        return bool(dry_run)
    return _env("POSTING_MODE", "dry_run").lower() != "live"


def publish(caption, media_url=None, dry_run=None):
    dry_run = _is_dry_run(dry_run)
    token = _env("LINKEDIN_" + "ACCESS_" + "TOKEN")
    author = _env("LINKEDIN_AUTHOR_URN")
    version = _env("LINKEDIN_VERSION", "202605")
    caption = str(caption or "").strip()

    result = {
        "platform": "LinkedIn",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(token and author),
        "mode": "dry_run" if dry_run else "live",
    }
    if not caption:
        result.update({"status": "empty_caption", "message": "Caption is required before publishing."})
        return result
    if dry_run:
        result.update({"status": "dry_run_success", "message": "LinkedIn preview only. Set POSTING_MODE=live to publish."})
        return result
    if not token:
        result.update({"status": "missing_credentials", "message": "Set the LinkedIn member or organization publishing token in environment settings."})
        return result
    if not author:
        result.update({"status": "missing_author", "message": "Set LINKEDIN_AUTHOR_URN, for example urn:li:person:<id> or urn:li:organization:<id>."})
        return result

    payload = {
        "author": author,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": version,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post("https://api.linkedin.com/rest/posts", json=payload, headers=headers, timeout=25)
    except requests.RequestException as exc:
        result.update({"status": "linkedin_network_error", "message": str(exc)[:500]})
        return result

    if response.status_code >= 400:
        result.update({"status": "linkedin_error", "message": response.text[:800], "status_code": response.status_code})
        return result

    result.update({
        "status": "published",
        "status_code": response.status_code,
        "post_urn": response.headers.get("x-restli-id", ""),
        "message": "LinkedIn post published successfully.",
    })
    return result


def credential_status():
    token = bool(_env("LINKEDIN_" + "ACCESS_" + "TOKEN"))
    author = bool(_env("LINKEDIN_AUTHOR_URN"))
    return {
        "platform": "LinkedIn",
        "access_token": "configured" if token else "missing",
        "author_urn": "configured" if author else "missing",
        "posting_mode": _env("POSTING_MODE", "dry_run"),
        "live_ready": bool(token and author),
        "supported_now": "text posts",
    }
