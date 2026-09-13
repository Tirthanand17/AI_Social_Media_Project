from pathlib import Path
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

try:
    from .analytics_fetcher import analytics_summary
except ImportError:
    from analytics_fetcher import analytics_summary


def _env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def build_weekly_report_html(platform=None):
    summary = analytics_summary(platform)
    rows = "".join(
        f"<tr><td>{p.get('post_id','')}</td><td>{p.get('platform','')}</td>"
        f"<td>{p.get('likes',0)}</td><td>{p.get('comments',0)}</td>"
        f"<td>{p.get('shares',0)}</td><td>{p.get('engagement_rate',0)}</td></tr>"
        for p in summary.get("top_posts", [])
    )
    return f"""
    <h2>Weekly Social Media Report</h2>
    <p>Total reach: {summary.get('total_reach', 0)}</p>
    <p>Average engagement rate: {summary.get('avg_engagement_rate', 0)}</p>
    <table border='1' cellpadding='6' cellspacing='0'>
      <tr><th>Post</th><th>Platform</th><th>Likes</th><th>Comments</th><th>Shares</th><th>Engagement</th></tr>
      {rows}
    </table>
    """.strip()


def send_weekly_report(platform=None, to_email=None, dry_run=None):
    """Build and optionally send the weekly HTML report.

    Email is dry-run unless EMAIL_SEND_ENABLED=true or dry_run=False is passed.
    This prevents a demo/test run from unexpectedly sending mail.
    """
    sender = os.getenv("GMAIL_USER", "").strip()
    password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    recipient = (to_email or os.getenv("EMAIL_REPORT_TO") or sender).strip()
    if dry_run is None:
        dry_run = not _env_bool("EMAIL_SEND_ENABLED", False)

    html = build_weekly_report_html(platform)
    result = {
        "status": "dry_run" if dry_run else "pending",
        "recipient": recipient,
        "platform": platform or "all",
        "html": html,
    }
    if dry_run:
        result["message"] = "Weekly report generated; email sending is disabled."
        return result
    if not sender or not password or not recipient:
        result.update({"status": "missing_credentials", "message": "Set GMAIL_USER, GMAIL_APP_PASSWORD and optionally EMAIL_REPORT_TO."})
        return result

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly Social Media Summary"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(sender, password)
            server.send_message(msg)
    except Exception as exc:
        result.update({"status": "email_error", "message": str(exc)[:500]})
        return result

    result.update({"status": "sent", "message": "Weekly report sent successfully."})
    return result


def configure_weekly_schedule():
    schedule.every().monday.at(os.getenv("WEEKLY_REPORT_TIME", "09:00")).do(send_weekly_report)
    return {"status": "scheduled", "day": "monday", "time": os.getenv("WEEKLY_REPORT_TIME", "09:00")}


def run_reporter_loop():
    configure_weekly_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    print(send_weekly_report(dry_run=True))
