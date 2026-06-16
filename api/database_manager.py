from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("APP_DB_PATH", ROOT / "data" / "processed" / "ai_social_studio.db"))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def rows_to_dicts(rows) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def hash_password(password: str) -> str:
    salt = os.getenv("APP_PASSWORD_SALT", "local-demo-salt")
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def init_db(seed_demo: bool = True) -> dict[str, Any]:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','editor','viewer')),
                brand_name TEXT DEFAULT '',
                password_hash TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT '',
                platform TEXT NOT NULL,
                content_type TEXT DEFAULT 'reel',
                caption TEXT NOT NULL,
                hashtags TEXT DEFAULT '',
                image_prompt TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft'
                  CHECK(status IN ('draft','pending_approval','approved','rejected','scheduled','published')),
                created_by TEXT DEFAULT 'system',
                approved_by TEXT DEFAULT '',
                scheduled_date TEXT DEFAULT '',
                scheduled_time TEXT DEFAULT '',
                publish_result TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                approved_at TEXT DEFAULT '',
                published_at TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                platform TEXT DEFAULT '',
                caption TEXT DEFAULT '',
                rating INTEGER DEFAULT 5,
                notes TEXT DEFAULT '',
                actual_engagement REAL,
                created_by TEXT DEFAULT 'system',
                created_at TEXT NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            );

            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                scheduled_date TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by TEXT DEFAULT 'system',
                created_at TEXT NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            );

            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT DEFAULT 'system',
                action TEXT NOT NULL,
                entity_type TEXT DEFAULT '',
                entity_id TEXT DEFAULT '',
                details TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )
        if seed_demo:
            seed_demo_users(conn)
        conn.commit()
    return {"status": "ready", "database": str(DB_PATH)}


def seed_demo_users(conn: sqlite3.Connection) -> None:
    users = [
        ("admin_techcreate", "admin", "TechCreate Studio", "admin123"),
        ("editor_creator", "editor", "Creator Desk", "editor123"),
        ("viewer_client", "viewer", "Client View", "viewer123"),
    ]
    for username, role, brand_name, password in users:
        conn.execute(
            """
            INSERT OR IGNORE INTO users(username, role, brand_name, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, role, brand_name, hash_password(password), now_iso()),
        )


def log_activity(username: str, action: str, entity_type: str = "", entity_id: Any = "", details: Any = "") -> None:
    if not isinstance(details, str):
        details = json.dumps(details, ensure_ascii=False)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO user_activity(username, action, entity_type, entity_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username or "system", action, entity_type, str(entity_id or ""), details, now_iso()),
        )
        conn.commit()


def list_users() -> list[dict[str, Any]]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        rows = conn.execute("SELECT id, username, role, brand_name, is_active, created_at FROM users ORDER BY id").fetchall()
    return rows_to_dicts(rows)


def save_post(
    caption: str,
    platform: str = "Instagram",
    hashtags: str = "",
    title: str = "",
    image_prompt: str = "",
    content_type: str = "reel",
    created_by: str = "system",
    status: str = "draft",
) -> dict[str, Any]:
    init_db(seed_demo=True)
    current = now_iso()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO posts(title, platform, content_type, caption, hashtags, image_prompt, status, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, platform, content_type, caption, hashtags, image_prompt, status, created_by, current, current),
        )
        post_id = cursor.lastrowid
        conn.commit()
    log_activity(created_by, "save_post", "post", post_id, {"platform": platform, "status": status})
    return get_post(post_id)


def get_post(post_id: int) -> dict[str, Any]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    return dict(row) if row else {}


def list_posts(status: Optional[str] = None, platform: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
    init_db(seed_demo=True)
    query = "SELECT * FROM posts WHERE 1=1"
    params: list[Any] = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if platform:
        query += " AND lower(platform) = lower(?)"
        params.append(platform)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows_to_dicts(rows)


def update_post(post_id: int, **fields: Any) -> dict[str, Any]:
    init_db(seed_demo=True)
    allowed = {"title", "platform", "content_type", "caption", "hashtags", "image_prompt", "status", "scheduled_date", "scheduled_time"}
    updates = {key: value for key, value in fields.items() if key in allowed and value is not None}
    if not updates:
        return get_post(post_id)
    updates["updated_at"] = now_iso()
    assignments = ", ".join([f"{key} = ?" for key in updates])
    values = list(updates.values()) + [post_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE posts SET {assignments} WHERE id = ?", values)
        conn.commit()
    log_activity(str(fields.get("updated_by") or "system"), "update_post", "post", post_id, updates)
    return get_post(post_id)


def submit_for_approval(post_id: int, username: str = "editor") -> dict[str, Any]:
    post = update_post(post_id, status="pending_approval", updated_by=username)
    log_activity(username, "submit_for_approval", "post", post_id)
    return post


def approve_post(post_id: int, approved_by: str = "admin", approved: bool = True, reason: str = "") -> dict[str, Any]:
    init_db(seed_demo=True)
    status = "approved" if approved else "rejected"
    current = now_iso()
    with get_connection() as conn:
        conn.execute(
            "UPDATE posts SET status = ?, approved_by = ?, approved_at = ?, updated_at = ? WHERE id = ?",
            (status, approved_by, current, current, post_id),
        )
        conn.commit()
    log_activity(approved_by, "approve_post" if approved else "reject_post", "post", post_id, {"reason": reason})
    return get_post(post_id)


def schedule_post(post_id: int, scheduled_date: str, scheduled_time: str, username: str = "editor") -> dict[str, Any]:
    init_db(seed_demo=True)
    post = update_post(post_id, status="scheduled", scheduled_date=scheduled_date, scheduled_time=scheduled_time, updated_by=username)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO schedules(post_id, platform, scheduled_date, scheduled_time, status, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (post_id, post.get("platform", "Instagram"), scheduled_date, scheduled_time, "pending", username, now_iso()),
        )
        conn.commit()
    log_activity(username, "schedule_post", "post", post_id, {"date": scheduled_date, "time": scheduled_time})
    return post


def save_feedback(post_id: Optional[int], platform: str, caption: str, rating: int, notes: str = "", actual_engagement: Optional[float] = None, created_by: str = "system") -> dict[str, Any]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO feedback(post_id, platform, caption, rating, notes, actual_engagement, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (post_id, platform, caption, max(1, min(5, int(rating))), notes, actual_engagement, created_by, now_iso()),
        )
        feedback_id = cursor.lastrowid
        conn.commit()
    log_activity(created_by, "save_feedback", "feedback", feedback_id, {"post_id": post_id, "rating": rating})
    return {"status": "saved", "feedback_id": feedback_id, "message": "Feedback saved"}


def list_feedback(limit: int = 50) -> list[dict[str, Any]]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return rows_to_dicts(rows)


def list_schedules(limit: int = 50) -> list[dict[str, Any]]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.*, p.caption, p.hashtags, p.status AS post_status
            FROM schedules s
            LEFT JOIN posts p ON p.id = s.post_id
            ORDER BY s.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return rows_to_dicts(rows)


def list_activity(limit: int = 80) -> list[dict[str, Any]]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM user_activity ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return rows_to_dicts(rows)


def dashboard_charts() -> dict[str, Any]:
    init_db(seed_demo=True)
    with get_connection() as conn:
        platform_rows = conn.execute("SELECT platform, COUNT(*) AS posts FROM posts GROUP BY platform ORDER BY posts DESC").fetchall()
        status_rows = conn.execute("SELECT status, COUNT(*) AS posts FROM posts GROUP BY status ORDER BY posts DESC").fetchall()
        content_rows = conn.execute("SELECT content_type, COUNT(*) AS posts FROM posts GROUP BY content_type ORDER BY posts DESC").fetchall()
        feedback_rows = conn.execute("SELECT platform, ROUND(AVG(rating), 2) AS avg_rating, COUNT(*) AS ratings FROM feedback GROUP BY platform").fetchall()
        trend_rows = conn.execute("SELECT substr(created_at, 1, 10) AS date, COUNT(*) AS posts FROM posts GROUP BY substr(created_at, 1, 10) ORDER BY date").fetchall()
    return {
        "platform_posts": rows_to_dicts(platform_rows),
        "status_breakdown": rows_to_dicts(status_rows),
        "content_type_posts": rows_to_dicts(content_rows),
        "feedback_rating_by_platform": rows_to_dicts(feedback_rows),
        "post_growth": rows_to_dicts(trend_rows),
    }
