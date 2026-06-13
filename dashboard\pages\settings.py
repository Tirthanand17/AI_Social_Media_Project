from pathlib import Path
import os
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

settings = {
    "USE_GEMINI": os.getenv("USE_GEMINI", "false"),
    "GEMINI_API_KEY": "set" if os.getenv("GEMINI_API_KEY") else "missing",
    "USE_GROQ": os.getenv("USE_GROQ", "false"),
    "GROQ_API_KEY": "set" if os.getenv("GROQ_API_KEY") else "missing",
    "POSTING_MODE": os.getenv("POSTING_MODE", "dry_run"),
    "TELEGRAM_BOT_TOKEN": "set" if os.getenv("TELEGRAM_BOT_TOKEN") else "missing",
    "TELEGRAM_CHAT_ID": "set" if os.getenv("TELEGRAM_CHAT_ID") else "missing",
}

st.json(settings)
st.info("The prototype runs without API keys. Set optional keys in .env only when you want live AI generation, Telegram alerts, or real publishing.")
