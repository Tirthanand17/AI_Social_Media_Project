from pathlib import Path
from datetime import datetime
import inspect
import os
from dotenv import load_dotenv
from api.notifier import telegram_bot_info, send_telegram

try:
    from .facebook_publisher import publish as publish_facebook, credential_status as facebook_status
    from .instagram_publisher import publish as publish_instagram, credential_status as instagram_status
    from .linkedin_publisher import publish as publish_linkedin, credential_status as linkedin_status
    from .twitter_publisher import publish as publish_x, credential_status as x_status
except ImportError:  # supports the existing sys.path based local startup
    from facebook_publisher import publish as publish_facebook, credential_status as facebook_status
    from instagram_publisher import publish as publish_instagram, credential_status as instagram_status
    from linkedin_publisher import publish as publish_linkedin, credential_status as linkedin_status
    from twitter_publisher import publish as publish_x, credential_status as x_status

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _called_from_package_generation():
    return any(frame.function == "api_full_pipeline" for frame in inspect.stack()[1:6])


def _dry_run(dry_run=None):
    if _called_from_package_generation():
        return True
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
    """Publish through one platform adapter.

    POSTING_MODE=dry_run is the safe default. A caller must explicitly enable
    live mode and supply valid platform credentials before any real post occurs.
    """
    key = str(platform or "").strip().lower()
    safe_preview = _dry_run(dry_run)

    if key == "facebook":
        return publish_facebook(caption, media_url, safe_preview)
    if key == "instagram":
        return publish_instagram(caption, media_url, safe_preview)
    if key in {"linkedin", "linked in"}:
        return publish_linkedin(caption, media_url, safe_preview)
    if key in {"twitter", "x"}:
        return publish_x(caption, media_url, safe_preview)
    if key == "telegram":
        if safe_preview:
            result = _base("Telegram", caption, media_url)
            result.update({"status": "dry_run_success", "message": "Telegram preview only."})
            return result
        return send_telegram(str(caption or ""))

    result = _base(platform, caption, media_url)
    result.update({"status": "unsupported_platform", "message": "Supported platforms: Facebook, Instagram, LinkedIn, X/Twitter, Telegram."})
    return result


def publish_to_all(platforms, caption, media_url=None, dry_run=None):
    selected = platforms or os.getenv("LIVE_PLATFORMS", "facebook,instagram,x,linkedin,telegram").split(",")
    return [publish_post(p.strip(), caption, media_url, dry_run=dry_run) for p in selected if p.strip()]


def integration_status():
    statuses = {
        "facebook": facebook_status(),
        "instagram": instagram_status(),
        "linkedin": linkedin_status(),
        "x": x_status(),
        "telegram": telegram_bot_info(),
    }
    ready = [name for name, value in statuses.items() if value.get("live_ready") or value.get("configured") is True]
    return {
        "posting_mode": os.getenv("POSTING_MODE", "dry_run"),
        "supported_platforms": ["Facebook", "Instagram", "LinkedIn", "X", "Telegram"],
        "live_ready_platforms": ready,
        **statuses,
    }


if __name__ == "__main__":
    print(publish_post("LinkedIn", "AI automation test caption #AI"))
