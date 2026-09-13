# AI Social Media Automation Platform

Private AI-assisted social-media management project built from the 52-task / 12-phase specification in [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md).

The repository includes caption and hashtag generation, content intelligence, trend analysis, moderation, plagiarism checks, multilingual fallback support, image/video prompt generation, engagement prediction, best-time recommendations, scheduling data, analytics, A/B analysis, competitor tracking, role-based demo authentication, dashboards, notifications, and multi-platform publishing adapters.

> **Safe default:** real social-media posting is disabled unless `POSTING_MODE=live` is explicitly configured. Keep `POSTING_MODE=dry_run` while developing or demonstrating the project.

## Project specification

`PROJECT_GUIDE.md` is the preserved implementation guide and contains all 52 documented tasks, the 12 phases, dataset mapping, original setup steps, testing table, deployment guidance, and the PRED smart performance predictor requirements.

All 10 documented datasets are included under `data/raw/`.

## Current architecture

```text
Frontend / Streamlit
        |
        v
FastAPI application
        |
        +-- NLP + content intelligence
        +-- ML engagement predictor / PRED
        +-- scheduler + best-time recommendation
        +-- analytics / A-B / competitor analysis
        +-- approval / feedback / auth flows
        +-- publisher manager
              |-- Facebook (dry-run or Meta Graph API)
              |-- Instagram (dry-run or Meta Graph API)
              |-- LinkedIn
              |-- X/Twitter
              `-- Telegram notification path

Storage options
  - SQLite prototype: api/database_manager.py
  - MySQL guide-compatible path: database/db_connection.py + database/schema.sql
```

## Important folders

```text
api/                 FastAPI, auth, analytics, storage, reporting, hardening
nlp/                 captions, hashtags, keywords, trends, moderation, prompts
ml_models/           training, feature engineering, predictor, A/B analysis
publisher/           platform publisher adapters + manager
scheduler/           schedule and best-time logic
dashboard/           Streamlit dashboard, admin pages, PRED page
data/raw/            10 source datasets from the project specification
data/cleaned/        generated cleaned data
data/processed/      generated application/demo data
database/            MySQL connection + reproducible schema
tests/               offline contract/safety tests
.github/workflows/   automated CI
```

## Local setup

### 1. Create a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Never commit `.env`. It is already excluded by `.gitignore`.

### 2. Optional MySQL + Redis services

The default prototype can run with its local SQLite path. To use the MySQL/Redis architecture described in the guide:

```bash
docker compose up -d mysql redis
```

The MySQL container automatically applies `database/schema.sql` on first initialization.

### 3. Run the verification scripts

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python RUN_TESTS.py
```

`RUN_TESTS.py` rebuilds/validates local data and model components. The `tests/` suite is intentionally offline and will not publish content or require platform credentials.

### 4. Start the API

Development entrypoint:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8010
```

Hardened entrypoint with `/api/*` rate limiting:

```powershell
python -m uvicorn api.secure_main:app --host 127.0.0.1 --port 8010
```

Docker uses the hardened entrypoint automatically.

Open:

- Frontend: `http://127.0.0.1:8010/app`
- API docs: `http://127.0.0.1:8010/docs`
- Health: `http://127.0.0.1:8010/api/health`

### 5. Streamlit

```powershell
streamlit run dashboard/dashboard.py
streamlit run dashboard/admin_panel.py --server.port 8502
```

## AI providers

The repository supports local/dataset-backed fallbacks, so an external AI key is not required for the basic demo. Optional providers are configured through `.env.example`, including Gemini and Groq.

Do not put real tokens in source code or commit them to GitHub.

## Publishing

Supported adapters are Facebook, Instagram, LinkedIn, X/Twitter, and Telegram-related notification flows. Facebook and Instagram now use Meta Graph API adapters when live mode is explicitly enabled and credentials are present.

Instagram live image publishing requires a publicly reachable media URL. Platform permissions, app review, token scopes, and account eligibility are controlled by the external platforms and must be validated with the user's own developer accounts.

For safe development:

```env
POSTING_MODE=dry_run
```

## Environment configuration

Copy `.env.example` to `.env`. It documents:

- app/CORS/security settings
- optional MySQL and Redis settings
- Gemini/Groq configuration
- Facebook/Instagram credentials
- LinkedIn credentials
- X/Twitter credentials
- Telegram and email reporting settings

## Automated checks

GitHub Actions runs on pushes to `main` and on pull requests. CI:

1. installs `requirements.txt` on Python 3.11,
2. compiles the Python source tree,
3. checks the 10-dataset contract and MySQL schema,
4. verifies the image-prompt compatibility module,
5. verifies Facebook/Instagram remain dry-run safe in offline tests.

## What is intentionally not stored in GitHub

- `.env` and real API credentials
- generated backups and logs
- private production data
- platform secrets/tokens

## External steps still required for live production

Code can be made repository-complete without possessing third-party accounts, but real production posting still requires valid platform developer credentials, approved permissions/scopes where applicable, a deployed database if MySQL is chosen, and deployment-specific environment variables. These are operational credentials/configuration, not missing source files.

For the original phase-by-phase instructions, use [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md). For the current gap audit and completion notes, use [`PROJECT_COMPLETION_AUDIT.md`](PROJECT_COMPLETION_AUDIT.md).
