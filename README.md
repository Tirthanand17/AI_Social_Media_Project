# AI Social Media Automation

FastAPI + Streamlit prototype for AI-assisted social media planning. It can generate captions, hashtags, image/video prompts, moderation checks, plagiarism checks, engagement predictions, analytics summaries, trend ideas, schedule views, role login, and dry-run publishing.

## Quick Start

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python RUN_TESTS.py
python -m uvicorn api.main:app --host 127.0.0.1 --port 8010
```

Open:
- Frontend: http://127.0.0.1:8010/app
- API docs: http://127.0.0.1:8010/docs
- Health: http://127.0.0.1:8010/api/health

Streamlit dashboard:

```powershell
streamlit run dashboard/dashboard.py
```

Admin panel:

```powershell
streamlit run dashboard/admin_panel.py
```

## API Keys

No API key is required for the local prototype. The app uses dataset-backed local fallback logic by default.

Optional keys can be added to `.env`:
- `USE_GEMINI=true` and `GEMINI_API_KEY=...` for Gemini caption generation
- `USE_GROQ=true` and `GROQ_API_KEY=...` for Groq/Llama caption generation
- `TELEGRAM_BOT_TOKEN=...` and `TELEGRAM_CHAT_ID=...` for Telegram notifications
- Real social platform credentials only when moving beyond dry-run publishing

Live posting is intentionally disabled by default through `POSTING_MODE=dry_run`.

## Verification

`python RUN_TESTS.py` trains the model, rebuilds derived data, and checks NLP, prediction, scheduler, analytics, and auth modules.
