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

    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    author = os.getenv("LINKEDIN_AUTHOR_URN", "")
    result = {
        "platform": "LinkedIn",
        "caption_preview": caption[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "configured": bool(token),
    }

    if dry_run:
        result.update({"status": "dry_run_success", "message": "LinkedIn token is stored locally; live posting is disabled by POSTING_MODE."})
        return result
    if not token:
        result.update({"status": "missing_credentials", "message": "Set LINKEDIN_ACCESS_TOKEN in .env."})
        return result
    if not author:
        result.update({"status": "missing_author", "message": "Set LINKEDIN_AUTHOR_URN, for example urn:li:person:<id>."})
        return result

    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    response = requests.post("https://api.linkedin.com/v2/ugcPosts", json=payload, headers=headers, timeout=20)
    if response.status_code >= 400:
        result.update({"status": "linkedin_error", "message": response.text[:500], "status_code": response.status_code})
        return result
    result.update({"status": "published", "response": response.json() if response.text else {}})
    return result


def credential_status():
    return {
        "platform": "LinkedIn",
        "access_token": "configured" if os.getenv("LINKEDIN_ACCESS_TOKEN", "") else "missing",
        "author_urn": "configured" if os.getenv("LINKEDIN_AUTHOR_URN", "") else "missing",
        "live_ready": bool(os.getenv("LINKEDIN_ACCESS_TOKEN", "") and os.getenv("LINKEDIN_AUTHOR_URN", "")),
    }
