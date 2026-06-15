# AI Social Media Automation Platform

A FastAPI + Streamlit prototype for AI-assisted social media planning and publishing. The system can generate captions, hashtags, image/video prompts, moderation checks, plagiarism checks, engagement predictions, analytics summaries, trend ideas, schedule views, role-based login, Telegram notifications, and dry-run/live publishing workflows.

> Current status: internship/demo-ready prototype. Real posting should stay in `POSTING_MODE=dry_run` until each platform credential is verified.

## Tech Stack

| Layer | Tools |
|---|---|
| Backend API | FastAPI, Uvicorn, Pydantic |
| Dashboard | Streamlit |
| ML / Analytics | Pandas, scikit-learn, XGBoost, Plotly |
| AI Providers | Local fallback, Gemini optional, Groq optional |
| Publishing | Dry-run by default, LinkedIn live support, X/Twitter credential placeholders |
| Deployment | Dockerfile, Render config |

## Main Features

- AI caption generation for Instagram, LinkedIn, Facebook, and X/Twitter.
- Hashtag recommendation and keyword extraction.
- Trend analysis and content idea generation.
- Content moderation and plagiarism similarity check.
- Engagement prediction using ML model.
- A/B caption comparison.
- Scheduler and best-time recommendation.
- Analytics and competitor summary.
- Telegram notification support.
- Role login for admin, editor, and viewer.
- Dry-run publishing to avoid accidental real posting.

## Architecture

```text
User / Admin
   |
   |-- Streamlit Dashboard / HTML Frontend
   |
FastAPI Backend
   |-- NLP Modules
   |-- ML Engagement Predictor
   |-- Scheduler
   |-- Publisher Manager
   |-- Telegram Notifier
   |
Datasets + Model Artifacts + Optional External APIs
```

## Folder Structure

```text
AI_Social_Media_Project/
├── api/                 # FastAPI routes and auth
├── dashboard/           # Streamlit dashboard and admin panel
├── data/                # Raw and processed datasets
├── frontend/            # Local HTML frontend
├── ml_models/           # Training and prediction logic
├── nlp/                 # Caption, hashtag, trend, moderation modules
├── publisher/           # LinkedIn/X/dry-run publishing logic
├── scheduler/           # Scheduling and best-time logic
├── requirements.txt
├── RUN_TESTS.py
├── Dockerfile
├── render.yaml
├── SECURITY.md
└── .env.example
```

## Quick Start - Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python RUN_TESTS.py
python -m uvicorn api.main:app --host 127.0.0.1 --port 8010
```

Open:

- Frontend: `http://127.0.0.1:8010/app`
- API docs: `http://127.0.0.1:8010/docs`
- Health: `http://127.0.0.1:8010/api/health`
- Public config: `http://127.0.0.1:8010/api/config`

## Streamlit Dashboard

```powershell
streamlit run dashboard/dashboard.py
```

## Admin Panel

```powershell
streamlit run dashboard/admin_panel.py
```

## Demo Login

Local demo login works only when `DEMO_LOGIN_ENABLED=true` in `.env`.

| Role | Username example | Password |
|---|---|---|
| Admin | `admin_techcreate` | `admin123` |
| Editor | dataset editor user | `editor123` |
| Viewer | dataset viewer user | `viewer123` |

Before live deployment, set:

```env
DEMO_LOGIN_ENABLED=false
APP_SECRET=your_long_random_secret
ADMIN_PASSWORD=your_secure_password
EDITOR_PASSWORD=your_secure_password
VIEWER_PASSWORD=your_secure_password
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

For stronger security, use password hash and salt. See `SECURITY.md`.

## API Keys

No API key is required for the local prototype. The app uses dataset-backed local fallback logic by default.

Optional keys can be added to `.env`:

- `USE_GEMINI=true` and `GEMINI_API_KEY=...` for Gemini caption generation.
- `USE_GROQ=true` and `GROQ_API_KEY=...` for Groq/Llama caption generation.
- `TELEGRAM_BOT_TOKEN=...` and `TELEGRAM_CHAT_ID=...` for Telegram notifications.
- `LINKEDIN_ACCESS_TOKEN=...` and `LINKEDIN_AUTHOR_URN=...` for LinkedIn live posting.
- X/Twitter needs OAuth user-context credentials before real posting.

## Publishing Mode

```env
POSTING_MODE=dry_run
```

Use `dry_run` for demo and testing. Change to `live` only after you have valid platform credentials and have tested with safe content.

## Deploy with Docker

```bash
docker build -t ai-social-media-automation .
docker run -p 8010:8010 --env-file .env ai-social-media-automation
```

## Deploy on Render

A starter `render.yaml` is included. Add these environment variables in Render dashboard:

- `APP_SECRET`
- `ALLOWED_ORIGINS`
- `ADMIN_PASSWORD`, `EDITOR_PASSWORD`, `VIEWER_PASSWORD` or password hashes
- Optional API keys for Gemini, Groq, Telegram, LinkedIn, and X/Twitter

Keep `POSTING_MODE=dry_run` during first deployment.

## Verification

```powershell
python RUN_TESTS.py
```

This trains/rebuilds local model artifacts and checks NLP, prediction, scheduler, analytics, and auth modules.

## Production Readiness Checklist

- [x] Configurable CORS through `ALLOWED_ORIGINS`.
- [x] Signed expiring auth token.
- [x] Environment-based passwords and optional password hashes.
- [x] `.env.example` with safe placeholders.
- [x] Dockerfile and Render config.
- [x] Security checklist.
- [ ] Add screenshots and demo video.
- [ ] Complete Instagram/Facebook Graph API integration.
- [ ] Complete X/Twitter OAuth user-context live posting.
- [ ] Add database-backed users instead of CSV users.
- [ ] Add automated API tests with pytest.

## Resume Line

Built an AI-powered social media automation platform using FastAPI, Streamlit, NLP, ML engagement prediction, scheduling, analytics, and safe dry-run publishing with optional Gemini/Groq/LinkedIn/Telegram integrations.
