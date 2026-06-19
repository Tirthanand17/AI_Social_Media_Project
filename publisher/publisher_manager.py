from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from api.notifier import telegram_bot_info, send_telegram
from linkedin_publisher import publish as publish_linkedin, credential_status as linkedin_status
from twitter_publisher import publish as publish_x, credential_status as x_status

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _dry_run(dry_run=None):
    if dry_run is not None:
        return bool(dry_run)
    return os.getenv("POSTING_MODE", "dry_run").strip().lower() != "live"


def _base(platform, caption, media_url=None):
    return {
        "platform": platform,
        "caption_preview": str(caption or "")[:160],
        "media_url": media_url,
        "published_at": datetime.now().isoformat(timespec="seconds"),
    }


def publish_post(platform, caption, media_url=None, dry_run=None):
    key = str(platform or "").strip().lower()

    if key in {"linkedin", "linked in"}:
        return publish_linkedin(caption, media_url, dry_run)

    if key in {"twitter", "x"}:
        return publish_x(caption, media_url, dry_run)

    if key == "telegram":
        if _dry_run(dry_run):
            result = _base("Telegram", caption, media_url)
            result.update({"status": "dry_run_success", "message": "Telegram preview only."})
            return result
        return send_telegram(str(caption or ""))

    if key in {"instagram", "facebook"}:
        result = _base(platform, caption, media_url)
        result.update({"status": "paused", "message": "This platform is paused until Meta credentials are added."})
        return result

    result = _base(platform, caption, media_url)
    result.update({"status": "unsupported_platform", "message": "Use X, LinkedIn, or Telegram for current publishing."})
    return result


def publish_to_all(platforms, caption, media_url=None):
    selected = platforms or os.getenv("LIVE_PLATFORMS", "x,linkedin,telegram").split(",")
    return [publish_post(p.strip(), caption, media_url) for p in selected if p.strip()]


def integration_status():
    return {
        "posting_mode": os.getenv("POSTING_MODE", "dry_run"),
        "active_platforms": ["X", "LinkedIn", "Telegram"],
        "paused_platforms": ["Instagram", "Facebook"],
        "telegram": telegram_bot_info(),
        "linkedin": linkedin_status(),
        "x": x_status(),
    }


if __name__ == "__main__":
    print(publish_post("LinkedIn", "AI automation test caption #AI"))
