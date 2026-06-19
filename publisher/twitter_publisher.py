from pathlib import Path
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

try:
    from requests_oauthlib import OAuth1
except Exception:  # dependency may be missing until requirements are installed
    OAuth1 = None

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
    caption = str(caption or "").strip()
    api_key = _env("X_API_KEY")
    api_secret = _env("X_API_SECRET")
    user_token = _env("X_" + "ACCESS_" + "TOKEN")
    user_secret = _env("X_" + "ACCESS_" + "TOKEN_" + "SECRET")

    result = {
        "platform": "X",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(api_key and api_secret and user_token and user_secret),
        "mode": "dry_run" if dry_run else "live",
    }
    if not caption:
        result.update({"status": "empty_caption", "message": "Caption is required before publishing."})
        return result
    if dry_run:
        result.update({"status": "dry_run_success", "message": "X preview only. Set POSTING_MODE=live to publish."})
        return result
    if not all([api_key, api_secret, user_token, user_secret]):
        result.update({"status": "missing_credentials", "message": "X live posting needs API key, API secret, user access token, and user access secret with write permission."})
        return result
    if OAuth1 is None:
        result.update({"status": "missing_dependency", "message": "Install requests-oauthlib before live X posting."})
        return result

    auth = OAuth1(api_key, api_secret, user_token, user_secret)
    payload = {"text": caption[:280]}
    try:
        response = requests.post("https://api.twitter.com/2/tweets", json=payload, auth=auth, timeout=25)
    except requests.RequestException as exc:
        result.update({"status": "x_network_error", "message": str(exc)[:500]})
        return result

    if response.status_code >= 400:
        result.update({"status": "x_error", "message": response.text[:800], "status_code": response.status_code})
        return result
    data = response.json() if response.text else {}
    result.update({"status": "published", "status_code": response.status_code, "post_id": data.get("data", {}).get("id"), "response": data})
    return result


def credential_status():
    api_key = bool(_env("X_API_KEY"))
    api_secret = bool(_env("X_API_SECRET"))
    user_token = bool(_env("X_" + "ACCESS_" + "TOKEN"))
    user_secret = bool(_env("X_" + "ACCESS_" + "TOKEN_" + "SECRET"))
    return {
        "platform": "X",
        "api_key": "configured" if api_key else "missing",
        "api_secret": "configured" if api_secret else "missing",
        "user_token": "configured" if user_token else "missing",
        "user_secret": "configured" if user_secret else "missing",
        "posting_mode": _env("POSTING_MODE", "dry_run"),
        "live_ready": all([api_key, api_secret, user_token, user_secret, OAuth1 is not None]),
    }


def bearer_status():
    bearer = _env("X_BEARER_TOKEN")
    if not bearer:
        return {"configured": False, "status": "missing_token"}
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/recent?query=from:XDevelopers&max_results=10",
        headers={"Authorization": f"Bearer {bearer}"},
        timeout=15,
    )
    return {"configured": True, "status_code": response.status_code, "ok": response.status_code < 400}
