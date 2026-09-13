from pathlib import Path
from datetime import datetime
import json
import os
import time

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHED = ROOT / "data" / "raw" / "05_scheduler_data.csv"
BEST = ROOT / "data" / "raw" / "06_best_time_dataset.csv"


def load_schedule(status=None):
    df = pd.read_csv(SCHED)
    if status:
        df = df[df["status"].astype(str).str.lower() == status.lower()]
    return df


def records(df):
    return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")


def pending_posts():
    return records(load_schedule("pending"))


def recommend_best_time(platform="Instagram"):
    df = pd.read_csv(BEST)
    platform_key = {"x": "twitter"}.get(str(platform or "Instagram").lower(), str(platform or "Instagram").lower())
    df = df[df["platform"].str.lower() == platform_key].sort_values("peak_score", ascending=False)
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def scheduler_summary():
    df = pd.read_csv(SCHED)
    return {
        "total": int(len(df)),
        "by_status": df["status"].value_counts().to_dict(),
        "pending": pending_posts(),
        "best_times": {
            platform: recommend_best_time(platform)
            for platform in ["Instagram", "Facebook", "Twitter", "LinkedIn"]
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def process_due_posts(now=None, dry_run=None, limit=20):
    """Process due schedules from the self-contained SQLite application database.

    Nothing is posted accidentally: publisher_manager remains dry-run by default.
    In dry-run mode due rows are previewed but left pending so they can still be
    published later after the owner explicitly enables POSTING_MODE=live.
    """
    try:
        from api.database_manager import get_connection, init_db
        from publisher.publisher_manager import publish_post
    except ImportError:
        from database_manager import get_connection, init_db
        from publisher_manager import publish_post

    init_db(seed_demo=True)
    current = now or datetime.now()
    current_text = current.strftime("%Y-%m-%d %H:%M:%S")
    if dry_run is None:
        dry_run = os.getenv("POSTING_MODE", "dry_run").strip().lower() != "live"

    with get_connection() as conn:
        due = conn.execute(
            """
            SELECT s.id AS schedule_id, s.post_id, s.platform, s.scheduled_date,
                   s.scheduled_time, p.caption, p.hashtags, p.status AS post_status
            FROM schedules s
            JOIN posts p ON p.id = s.post_id
            WHERE s.status = 'pending'
              AND datetime(s.scheduled_date || ' ' || s.scheduled_time) <= datetime(?)
              AND p.status IN ('approved', 'scheduled')
            ORDER BY s.scheduled_date, s.scheduled_time
            LIMIT ?
            """,
            (current_text, max(1, int(limit))),
        ).fetchall()

    results = []
    for row in due:
        item = dict(row)
        caption = item.get("caption", "")
        hashtags = item.get("hashtags", "")
        final_caption = f"{caption}\n\n{hashtags}".strip() if hashtags else caption
        publish_result = publish_post(item["platform"], final_caption, dry_run=dry_run)
        result_status = publish_result.get("status", "unknown") if isinstance(publish_result, dict) else "unknown"

        if not dry_run:
            schedule_status = "published" if result_status == "published" else "failed"
            with get_connection() as conn:
                conn.execute("UPDATE schedules SET status = ? WHERE id = ?", (schedule_status, item["schedule_id"]))
                if schedule_status == "published":
                    conn.execute(
                        "UPDATE posts SET status='published', published_at=?, publish_result=?, updated_at=? WHERE id=?",
                        (
                            datetime.now().isoformat(timespec="seconds"),
                            json.dumps(publish_result, default=str),
                            datetime.now().isoformat(timespec="seconds"),
                            item["post_id"],
                        ),
                    )
                conn.commit()

        results.append({
            "schedule_id": item["schedule_id"],
            "post_id": item["post_id"],
            "platform": item["platform"],
            "dry_run": bool(dry_run),
            "publish_result": publish_result,
        })

    return {
        "checked_at": current.isoformat(timespec="seconds"),
        "dry_run": bool(dry_run),
        "due_count": len(due),
        "processed": results,
    }


def run_scheduler_loop(interval_seconds=30):
    """Run the due-post worker. Safe previews occur until live mode is enabled."""
    interval = max(10, int(interval_seconds))
    while True:
        process_due_posts()
        time.sleep(interval)


if __name__ == "__main__":
    print(scheduler_summary())
    print("Best Instagram time:", recommend_best_time("Instagram"))
    print("Due post preview:", process_due_posts(dry_run=True))
