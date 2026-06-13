from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

def publish_post(platform, caption, media_url=None, dry_run=None):
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

if __name__ == "__main__":
    print(publish_post("Instagram", "AI automation test caption #AI"))
