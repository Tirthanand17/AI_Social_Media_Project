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


if __name__ == "__main__":
    print(send_telegram("AI Social Media Automation notifier test"))
