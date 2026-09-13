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
    """Publish an Instagram image post through the Meta Graph API.

    Live Instagram publishing requires a publicly reachable image URL. Dry-run
    mode remains the default so the project never posts merely because it starts.
    """
    dry_run = _is_dry_run(dry_run)
    caption = str(caption or "").strip()
    token = _env("FACEBOOK_ACCESS_TOKEN") or _env("INSTAGRAM_ACCESS_TOKEN")
    user_id = _env("INSTAGRAM_USER_ID")

    result = {
        "platform": "Instagram",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(token and user_id),
        "mode": "dry_run" if dry_run else "live",
    }
    if not caption:
        result.update({"status": "empty_caption", "message": "Caption is required before publishing."})
        return result
    if dry_run:
        result.update({"status": "dry_run_success", "message": "Instagram preview only. Live image publishing additionally requires a public media_url."})
        return result
    if not token or not user_id:
        result.update({"status": "missing_credentials", "message": "Set INSTAGRAM_USER_ID and FACEBOOK_ACCESS_TOKEN (or INSTAGRAM_ACCESS_TOKEN) before live posting."})
        return result
    if not media_url:
        result.update({"status": "missing_media", "message": "Instagram live image publishing requires a publicly reachable media_url."})
        return result

    try:
        create_response = requests.post(
            _graph_url(f"{user_id}/media"),
            data={"image_url": str(media_url), "caption": caption, "access_token": token},
            timeout=25,
        )
        create_data = create_response.json() if create_response.text else {}
    except requests.RequestException as exc:
        result.update({"status": "instagram_network_error", "message": str(exc)[:500]})
        return result

    creation_id = create_data.get("id")
    if create_response.status_code >= 400 or not creation_id:
        result.update({"status": "instagram_container_error", "status_code": create_response.status_code, "message": str(create_data.get("error") or create_response.text)[:800]})
        return result

    try:
        publish_response = requests.post(
            _graph_url(f"{user_id}/media_publish"),
            data={"creation_id": creation_id, "access_token": token},
            timeout=25,
        )
        publish_data = publish_response.json() if publish_response.text else {}
    except requests.RequestException as exc:
        result.update({"status": "instagram_network_error", "creation_id": creation_id, "message": str(exc)[:500]})
        return result

    if publish_response.status_code >= 400 or publish_data.get("error"):
        result.update({"status": "instagram_publish_error", "status_code": publish_response.status_code, "creation_id": creation_id, "message": str(publish_data.get("error") or publish_response.text)[:800]})
        return result

    result.update({"status": "published", "status_code": publish_response.status_code, "creation_id": creation_id, "post_id": publish_data.get("id"), "response": publish_data})
    return result


def credential_status():
    token = bool(_env("FACEBOOK_ACCESS_TOKEN") or _env("INSTAGRAM_ACCESS_TOKEN"))
    user_id = bool(_env("INSTAGRAM_USER_ID"))
    return {
        "platform": "Instagram",
        "access_token": "configured" if token else "missing",
        "user_id": "configured" if user_id else "missing",
        "posting_mode": _env("POSTING_MODE", "dry_run"),
        "live_ready": bool(token and user_id),
        "live_requirement": "public image URL",
    }
