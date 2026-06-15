from pathlib import Path
import os
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"status": "dry_run", "message": message}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    response.raise_for_status()
    return {"status": "sent", "response": response.json()}


def telegram_bot_info():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"configured": False, "status": "missing_token"}

    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        result = data.get("result", {})
        return {
            "configured": True,
            "status": "ok" if data.get("ok") else "error",
            "bot_username": result.get("username"),
            "bot_name": result.get("first_name"),
            "can_send_messages": bool(os.getenv("TELEGRAM_CHAT_ID", "")),
        }
    except Exception as exc:
        return {"configured": True, "status": "error", "message": str(exc)[:240], "can_send_messages": False}


if __name__ == "__main__":
    print(send_telegram("AI Social Media Automation notifier test"))
