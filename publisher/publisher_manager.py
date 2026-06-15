from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from api.notifier import telegram_bot_info
from linkedin_publisher import publish as publish_linkedin, credential_status as linkedin_status
from twitter_publisher import publish as publish_x, credential_status as x_status

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def publish_post(platform, caption, media_url=None, dry_run=None):
    key = str(platform or "").lower()
    if key in {"linkedin", "linked in"}:
        return publish_linkedin(caption, media_url, dry_run)
    if key in {"twitter", "x"}:
        return publish_x(caption, media_url, dry_run)

    if dry_run is None:
        dry_run = os.getenv("POSTING_MODE", "dry_run") == "dry_run"
    result = {"platform": platform, "caption_preview": caption[:120], "media_url": media_url, "published_at": datetime.now().isoformat(timespec="seconds")}
    if dry_run:
        result.update({"status": "dry_run_success", "message": "Prototype mode: post not actually published."})
    else:
        result.update({"status": "needs_real_api_credentials", "message": "Connect Instagram/LinkedIn/Facebook API before live posting."})
    return result

def publish_to_all(platforms, caption, media_url=None):
    return [publish_post(p, caption, media_url) for p in platforms]

def integration_status():
    return {
        "posting_mode": os.getenv("POSTING_MODE", "dry_run"),
        "telegram": telegram_bot_info(),
        "linkedin": linkedin_status(),
        "x": x_status(),
    }

if __name__ == "__main__":
    print(publish_post("Instagram", "AI automation test caption #AI"))
