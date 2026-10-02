# AI Social Media Platform — Complete Project Guide
### 52 Tasks | 12 Phases | Step-by-Step for Junior Developers

---

## PROJECT OVERVIEW

Build a full AI-powered social media management platform that:
- Generates captions using LLaMA 3 (Groq API)
- Predicts engagement scores using a trained ML model
- Auto-schedules posts at peak times
- Publishes to Facebook, Instagram, LinkedIn, Twitter
- Tracks analytics and sends weekly reports
- Includes a Streamlit dashboard + admin panel

**Tech Stack:** Python 3.11 · FastAPI · MySQL 8 · Streamlit · scikit-learn · XGBoost · Groq API · HuggingFace · Redis · Celery

---

## NEW FEATURE — PRED (Smart Post Performance Predictor Dashboard)

**What it does:** Before you post anything, PRED shows you:
- Predicted engagement score (0–100)
- Expected likes and estimated reach
- Best platform to post on for that caption
- Best day and time to post

**How it works:** Uses the trained ML model (engagement_model.pkl) in real-time as the user types a caption inside the dashboard.

---

## DATASETS USED IN THIS PROJECT

All 10 datasets are located in `data/raw/`. Each dataset is purpose-built for specific tasks.

**Dataset provenance note:** the repository ships illustrative/sample records for reproducible portfolio and classroom use. Treat them as demo data rather than live customer or platform data.

| # | File | Used In Tasks | What It Contains |
|---|------|--------------|------------------|
| 1 | `01_social_media_engagement.csv` | Task 6, 7 | 60 real-style posts — raw data for cleaning phase |
| 2 | `02_ml_training_dataset.csv` | Task 13, 14, 15, 16, 17 | 50 posts with all 8 ML features + engagement_score target |
| 3 | `03_nlp_captions_dataset.csv` | Task 9, 10, 11 | 50 captions with extracted keywords, sentiment, CTA flags |
| 4 | `04_analytics_data.csv` | Task 28, 40, 42 | 50 analytics records — simulates Facebook/Instagram API response |
| 5 | `05_scheduler_data.csv` | Task 22, 23, 30, 31 | 60 scheduling records — published, pending, and failed posts |
| 6 | `06_best_time_dataset.csv` | Task 17, 29 | Best posting time per platform/day/hour — converts to best_time.json |
| 7 | `07_trends_data.csv` | Task 12, 43, 49 | 30 trending keywords — simulates daily RSS + Pytrends fetch |
| 8 | `08_ab_testing_data.csv` | Task 41 | 10 completed A/B tests with winners and insights |
| 9 | `09_competitor_tracking_data.csv` | Task 42 | 10 competitor brands tracked — engagement gaps and alerts |
| 10 | `10_users_data.csv` | Task 45 | 15 users across 3 roles — admin, editor, viewer |

> Full column-by-column explanation is in `data/DATASET_GUIDE.md`

---

## FOLDER STRUCTURE

```
ai-social-media-platform/
├── api/
│   ├── main.py
│   ├── content.py
│   ├── analytics_fetcher.py
│   └── rate_limiter.py
├── nlp/
│   ├── caption_generator.py
│   ├── keyword_extractor.py
│   ├── hashtag_generator.py
│   ├── trend_analyzer.py
│   ├── plagiarism_checker.py
│   ├── content_moderator.py
│   └── translator.py
├── ml_models/
│   ├── train_model.py
│   ├── predictor.py
│   ├── ab_tester.py
│   └── engagement_model.pkl        ← generated after training
├── publisher/
│   ├── facebook_publisher.py
│   ├── instagram_publisher.py
│   ├── linkedin_publisher.py
│   ├── twitter_publisher.py
│   └── publisher_manager.py
├── scheduler/
│   └── auto_scheduler.py
├── database/
│   └── db_connection.py
├── dashboard/
│   ├── dashboard.py
│   └── admin_panel.py
├── data/
│   ├── raw/
│   └── cleaned/
├── backups/
├── logs/
├── .env                            ← never commit this
├── requirements.txt
└── best_time.json                  ← generated after training
```

---

## PHASE 1 — SETUP & ENVIRONMENT
### Tasks 1–5

---

### Task 1 — Install All Tools

Install each tool below. Verify every install before moving on.

| Tool | Version | Verify Command |
|------|---------|----------------|
| Python | 3.11 | `python --version` |
| VS Code | Latest | Open it |
| MySQL | 8.0 | `mysql --version` |
| Postman | Latest | Open it |
| Git | Latest | `git --version` |
| Anaconda | Latest | `conda --version` |

**Download links:**
- Python: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/
- MySQL: https://dev.mysql.com/downloads/installer/
- Postman: https://www.postman.com/downloads/
- Git: https://git-scm.com/downloads
- Anaconda: https://www.anaconda.com/download

**VS Code Extensions to install:**
- Python (Microsoft)
- Pylance
- GitLens
- MySQL (cweijan)
- REST Client

---

### Task 2 — Create GitHub Repository

```bash
# Step 1: Go to github.com → New Repository
# Name: ai-social-media-platform
# Visibility: Private
# Check: Add README, Add .gitignore (Python)

# Step 2: Clone it locally
git clone https://github.com/<your-username>/ai-social-media-platform.git
cd ai-social-media-platform

# Step 3: Create both branches
git checkout -b python-team
git push origin python-team

git checkout main
git checkout -b ds-team
git push origin ds-team
```

---

### Task 3 — Create Folder Structure

Run this in your project root (Windows CMD):

```cmd
mkdir api nlp ml_models publisher scheduler database dashboard data\raw data\cleaned backups logs
```

Then create empty `__init__.py` files in each folder:

```cmd
type nul > api\__init__.py
type nul > nlp\__init__.py
type nul > ml_models\__init__.py
type nul > publisher\__init__.py
type nul > scheduler\__init__.py
type nul > database\__init__.py
type nul > dashboard\__init__.py
```

---

### Task 4 — Install Python Packages

Create `requirements.txt` in the project root:

```txt
fastapi==0.111.0
uvicorn==0.30.0
sqlalchemy==2.0.30
pymysql==1.1.1
python-dotenv==1.0.1
groq==0.9.0
spacy==3.7.4
pytrends==4.9.2
scikit-learn==1.5.0
xgboost==2.0.3
pandas==2.2.2
numpy==1.26.4
joblib==1.4.2
streamlit==1.35.0
plotly==5.22.0
httpx==0.27.0
python-jose[cryptography]==3.3.0
bcrypt==4.1.3
feedparser==6.0.11
googletrans==4.0.0rc1
transformers==4.41.2
torch==2.3.0
difflib2==1.0.0
redis==5.0.4
slowapi==0.1.9
smtplib2==0.2.1
python-telegram-bot==21.3
schedule==1.2.2
celery==5.4.0
```

Install:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

### Task 5 — Setup MySQL Database

Open MySQL Workbench or run in terminal:

```sql
CREATE DATABASE ai_social_media;
USE ai_social_media;

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform VARCHAR(50),
    caption TEXT,
    hashtags TEXT,
    image_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft',
    engagement_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    scheduled_time DATETIME,
    platform VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    likes INT DEFAULT 0,
    reach INT DEFAULT 0,
    comments INT DEFAULT 0,
    shares INT DEFAULT 0,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE trends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255),
    score FLOAT,
    platform VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Create `.env` file in project root (NEVER commit this):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ai_social_media

GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_hf_key
FACEBOOK_ACCESS_TOKEN=your_fb_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_USER_ID=your_ig_id
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_twitter_access
TWITTER_ACCESS_SECRET=your_twitter_access_secret

JWT_SECRET=change_this_to_a_random_64_char_string
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

REDIS_URL=redis://localhost:6379/0
STABLE_DIFFUSION_API_KEY=your_sd_key
```

Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pkl" >> .gitignore
echo "backups/" >> .gitignore
```

---

## PHASE 2 — DATA COLLECTION
### Tasks 6–8

---

### Task 6 — Download Datasets

> **Dataset Used:** `data/raw/01_social_media_engagement.csv`
> This dummy dataset is already provided. It contains 60 real-style posts across Instagram, Facebook, Twitter and LinkedIn with all required columns. No Kaggle download needed to start.

1. Go to https://www.kaggle.com
2. Search and download:
   - "Social Media Engagement Dataset" → save to `data/raw/social_media_engagement.csv`
   - "Instagram Posts Dataset" → save to `data/raw/instagram_posts.csv`

You need a Kaggle account. Sign up free if you don't have one.

**OR use the provided dummy dataset directly:**
```bash
# The file is already at:
# data/raw/01_social_media_engagement.csv
# Just rename it or update the path in clean_data.py
```

---

### Task 7 — Clean the Data

> **Dataset Used:** `data/raw/01_social_media_engagement.csv` → outputs to `data/cleaned/engagement_clean.csv`
> Input columns used: `caption`, `platform`, `likes_count`, `shares_count`, `comments_count`, `impressions`, `sentiment_score`, `has_image`, `content_type`, `day_of_week`, `hour_posted`, `hashtags`

Create `data/clean_data.py`:

```python
import pandas as pd
import os

# Use the provided dummy dataset
df = pd.read_csv("data/raw/01_social_media_engagement.csv")

# Drop rows with missing values in key columns
df = df.dropna(subset=["caption", "platform", "likes_count", "impressions"])

# Rename columns to match expected names
df = df.rename(columns={
    "likes_count": "likes",
    "comments_count": "comments",
    "shares_count": "shares"
})

# Compute engagement score (0-100 scale)
df["engagement_score"] = (
    (df["likes"] + df["comments"] * 2 + df["shares"] * 3) / df["impressions"]
) * 100
df["engagement_score"] = df["engagement_score"].clip(0, 100)

os.makedirs("data/cleaned", exist_ok=True)
df.to_csv("data/cleaned/engagement_clean.csv", index=False)
print(f"Saved {len(df)} rows to data/cleaned/engagement_clean.csv")
```

Run:

```bash
python data/clean_data.py
```

---

### Task 8 — Register for API Keys

Get each key and add to `.env`:

| Service | URL | What to get |
|---------|-----|-------------|
| Groq (LLaMA 3) | https://console.groq.com | API Key |
| HuggingFace | https://huggingface.co/settings/tokens | Access Token |
| Facebook | https://developers.facebook.com | Page Access Token |
| LinkedIn | https://www.linkedin.com/developers | OAuth 2.0 Token |
| Twitter/X | https://developer.twitter.com | API Key + Secret |

> Note: Facebook and Twitter require app review for posting permissions. For testing, use sandbox/test modes.

---

## PHASE 3 — NLP CONTENT ENGINE
### Tasks 9–12

---

### Task 9 — Caption Generator (`nlp/caption_generator.py`)

> **Dataset Used:** `data/raw/03_nlp_captions_dataset.csv`
> Contains 50 high-performing captions with their NLP features already extracted.
> Load the top 5 captions per platform (highest engagement) as few-shot examples in the Groq system prompt to improve caption quality.

```python
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_captions(topic: str, platform: str, tone: str = "engaging") -> list[str]:
    prompt = f"""Generate 3 different {tone} social media captions for {platform} about: {topic}
    
    Rules:
    - Each caption on a new line starting with a number (1. 2. 3.)
    - Match the platform style (Instagram = visual, LinkedIn = professional, Twitter = short)
    - Include a call-to-action
    - Do NOT include hashtags (they are added separately)
    """
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=500
    )
    
    raw = response.choices[0].message.content
    captions = [line.split(". ", 1)[1].strip() 
                for line in raw.strip().split("\n") 
                if line.strip() and line[0].isdigit()]
    return captions[:3]
```

Test it:

```bash
python -c "from nlp.caption_generator import generate_captions; print(generate_captions('AI tools', 'Instagram'))"
```

---

### Task 10 — Keyword Extractor (`nlp/keyword_extractor.py`)

> **Dataset Used:** `data/raw/03_nlp_captions_dataset.csv`
> The `extracted_keywords` column shows what good keyword extraction looks like for each caption.
> Use these as expected outputs when testing your extractor.

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    doc = nlp(text)
    keywords = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in ("NOUN", "PROPN", "ADJ")
    ]
    # Return unique keywords, most frequent first
    from collections import Counter
    return [word for word, _ in Counter(keywords).most_common(top_n)]
```

---

### Task 11 — Hashtag Generator (`nlp/hashtag_generator.py`)

> **Dataset Used:** `data/raw/03_nlp_captions_dataset.csv` + `data/raw/07_trends_data.csv`
> Caption dataset provides keyword examples per platform.
> Trends dataset provides the live trending hashtags to mix in (column: `related_hashtags`).

```python
from pytrends.request import TrendReq
from nlp.keyword_extractor import extract_keywords

STATIC_HASHTAGS = {
    "instagram": ["instagood", "photooftheday", "instadaily"],
    "twitter": ["trending", "viral"],
    "linkedin": ["leadership", "innovation", "growth"],
    "facebook": ["share", "community"]
}

def generate_hashtags(caption: str, platform: str, count: int = 10) -> list[str]:
    keywords = extract_keywords(caption, top_n=3)
    hashtags = [f"#{kw}" for kw in keywords]
    
    # Add live trending tags
    try:
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload(keywords[:2], timeframe="now 1-d")
        related = pytrends.related_queries()
        for kw in keywords[:2]:
            if kw in related and related[kw]["top"] is not None:
                top_queries = related[kw]["top"]["query"].tolist()[:3]
                hashtags += [f"#{q.replace(' ', '')}" for q in top_queries]
    except Exception:
        pass  # Pytrends can rate-limit; fall back silently
    
    # Add static platform hashtags
    hashtags += [f"#{h}" for h in STATIC_HASHTAGS.get(platform.lower(), [])]
    
    return list(dict.fromkeys(hashtags))[:count]  # deduplicate, keep order
```

---

### Task 12 — Trend Analyzer (`nlp/trend_analyzer.py`)

> **Dataset Used:** `data/raw/07_trends_data.csv`
> Contains 30 pre-collected trending keywords with trend_score, search_volume_index, related_hashtags and is_rising flag.
> Use this to pre-populate the `trends` MySQL table and test the hashtag generator without waiting for the real 8AM RSS fetch.

```python
import feedparser
import schedule
import time
from datetime import datetime
from database.db_connection import get_session
from sqlalchemy import text

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://techcrunch.com/feed/"
]

def fetch_and_save_trends():
    keywords = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            words = entry.title.split()
            keywords += [w.strip(",.!?").lower() for w in words if len(w) > 4]
    
    from collections import Counter
    top = Counter(keywords).most_common(20)
    
    with get_session() as session:
        for keyword, score in top:
            session.execute(
                text("INSERT INTO trends (keyword, score, platform) VALUES (:k, :s, :p)"),
                {"k": keyword, "s": float(score), "p": "general"}
            )
        session.commit()
    print(f"[{datetime.now()}] Saved {len(top)} trends")

# Schedule to run every morning at 8AM
schedule.every().day.at("08:00").do(fetch_and_save_trends)

if __name__ == "__main__":
    fetch_and_save_trends()  # Run once immediately on start
    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## PHASE 4 — ML PREDICTION MODEL
### Tasks 13–17

---

### Task 13 — Feature Engineering (`ml_models/feature_engineering.py`)

> **Dataset Used:** `data/raw/02_ml_training_dataset.csv`
> This dataset already has all 8 features pre-engineered (`platform_encoded`, `day_encoded`, `hour_posted`, `content_type`, `caption_length`, `hashtag_count`, `has_image`, `sentiment_score`) and the target column `engagement_score`.
> You can use this directly to skip the feature engineering step and jump straight to training.

```python
import pandas as pd
from textblob import TextBlob

PLATFORM_MAP = {"instagram": 0, "facebook": 1, "twitter": 2, "linkedin": 3}
CONTENT_MAP  = {"image": 0, "video": 1, "text": 2, "reel": 3}
DAY_MAP      = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6}

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["platform_encoded"]      = df["platform"].str.lower().map(PLATFORM_MAP).fillna(0)
    df["content_type_encoded"]  = df["content_type"].str.lower().map(CONTENT_MAP).fillna(2)
    df["day_encoded"]           = df["day_of_week"].str.lower().map(DAY_MAP).fillna(0)
    df["caption_length"]        = df["caption"].str.len()
    df["hashtag_count"]         = df["hashtags"].str.count("#").fillna(0)
    df["has_image"]             = (df["content_type"].str.lower() == "image").astype(int)
    df["sentiment_score"]       = df["caption"].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )
    return df

FEATURE_COLS = [
    "platform_encoded", "content_type_encoded", "day_encoded",
    "hour_posted", "caption_length", "hashtag_count", "has_image", "sentiment_score"
]
```

---

### Task 14 — Train Random Forest (`ml_models/train_model.py`)

> **Dataset Used:** `data/cleaned/engagement_clean.csv` (generated by Task 7)
> **OR shortcut:** Load `data/raw/02_ml_training_dataset.csv` directly — it already has all features and engagement_score ready.

```python
import pandas as pd
import joblib
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from ml_models.feature_engineering import engineer_features, FEATURE_COLS

# Option 1: Use cleaned data from Task 7
# df = pd.read_csv("data/cleaned/engagement_clean.csv")
# df = engineer_features(df)

# Option 2: Use pre-engineered dummy dataset (faster for testing)
df = pd.read_csv("data/raw/02_ml_training_dataset.csv")

X = df[FEATURE_COLS]
y = df["engagement_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
rf_score = r2_score(y_test, rf_model.predict(X_test))
print(f"Random Forest R² Score: {rf_score:.4f}")
```

---

### Task 15 — Train XGBoost & Compare

Add this to `ml_models/train_model.py`:

```python
from xgboost import XGBRegressor

xgb_model = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
xgb_model.fit(X_train, y_train)
xgb_score = r2_score(y_test, xgb_model.predict(X_test))
print(f"XGBoost R² Score:       {xgb_score:.4f}")
```

---

### Task 16 — Save Best Model

Add to `ml_models/train_model.py`:

```python
import os
os.makedirs("ml_models", exist_ok=True)

best_model = rf_model if rf_score >= xgb_score else xgb_model
best_name  = "RandomForest" if rf_score >= xgb_score else "XGBoost"

joblib.dump(best_model, "ml_models/engagement_model.pkl")
json.dump(FEATURE_COLS, open("ml_models/feature_list.json", "w"))
print(f"Saved {best_name} model (R²={max(rf_score, xgb_score):.4f})")
```

Run:

```bash
python ml_models/train_model.py
```

---

### Task 17 — Best Time Recommender

> **Dataset Used:** `data/raw/06_best_time_dataset.csv`
> Already contains pre-aggregated best posting times per platform, day, and hour with avg_engagement_rate and peak_score.
> Use this to generate `best_time.json` directly instead of computing from scratch.

**Quick way to generate best_time.json from the provided dataset:**
```python
import pandas as pd, json
df = pd.read_csv("data/raw/06_best_time_dataset.csv")
best = df.sort_values("avg_engagement_rate", ascending=False).groupby("platform").first().reset_index()
json.dump(best[["platform","day_of_week","hour_posted","avg_engagement_rate"]].to_dict(orient="records"),
          open("best_time.json","w"), indent=2)
print("best_time.json saved!")
```

Add to `ml_models/train_model.py`:

```python
best_time = (
    df.groupby(["platform", "day_encoded", "hour_posted"])["engagement_score"]
    .mean()
    .reset_index()
    .sort_values("engagement_score", ascending=False)
    .groupby("platform")
    .first()
    .reset_index()
    [["platform", "day_encoded", "hour_posted", "engagement_score"]]
    .to_dict(orient="records")
)
json.dump(best_time, open("best_time.json", "w"), indent=2)
print("Saved best_time.json")
```

---

## PHASE 5 — BACKEND API
### Tasks 18–21

---

### Task 18 — FastAPI Entry Point (`api/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.content import router as content_router

app = FastAPI(title="AI Social Media API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(content_router, prefix="/api/content")

@app.get("/")
def root():
    return {"status": "running", "version": "1.0.0"}
```

Run:

```bash
uvicorn api.main:app --reload
```

Open http://localhost:8000/docs to see all endpoints.

---

### Task 19 — Content Generation Endpoint (`api/content.py`)

```python
from fastapi import APIRouter
from pydantic import BaseModel
from nlp.caption_generator import generate_captions
from nlp.hashtag_generator import generate_hashtags
from ml_models.predictor import predict_score

router = APIRouter()

class GenerateRequest(BaseModel):
    topic: str
    platform: str
    tone: str = "engaging"

@router.post("/generate")
def generate(req: GenerateRequest):
    captions = generate_captions(req.topic, req.platform, req.tone)
    results = []
    for caption in captions:
        hashtags = generate_hashtags(caption, req.platform)
        score = predict_score(caption, req.platform)
        results.append({
            "caption": caption,
            "hashtags": hashtags,
            "predicted_engagement": round(score, 2)
        })
    return {"results": sorted(results, key=lambda x: x["predicted_engagement"], reverse=True)}
```

---

### Task 20 — Database Connection (`database/db_connection.py`)

```python
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

### Task 21 — Score Endpoint & Predictor

Create `ml_models/predictor.py`:

```python
import joblib
import json
import numpy as np
from textblob import TextBlob

model = joblib.load("ml_models/engagement_model.pkl")
features = json.load(open("ml_models/feature_list.json"))

PLATFORM_MAP = {"instagram": 0, "facebook": 1, "twitter": 2, "linkedin": 3}

def predict_score(caption: str, platform: str, hour: int = 12,
                  content_type: int = 0, day: int = 2) -> float:
    sentiment = TextBlob(caption).sentiment.polarity
    data = [[
        PLATFORM_MAP.get(platform.lower(), 0),
        content_type, day, hour,
        len(caption),
        caption.count("#"),
        1 if content_type == 0 else 0,
        sentiment
    ]]
    score = float(model.predict(np.array(data))[0])
    return max(0.0, min(100.0, score))
```

Add score endpoint to `api/content.py`:

```python
class ScoreRequest(BaseModel):
    caption: str
    platform: str
    hour: int = 12

@router.post("/score")
def score(req: ScoreRequest):
    s = predict_score(req.caption, req.platform, req.hour)
    return {"predicted_engagement": round(s, 2)}
```

---

## PHASE 6 — SCHEDULER & PUBLISHER
### Tasks 22–27

---

### Task 22–23 — Auto Scheduler (`scheduler/auto_scheduler.py`)

> **Dataset Used:** `data/raw/05_scheduler_data.csv`
> Use this to pre-populate the `schedules` MySQL table for testing.
> It contains 60 rows with statuses: `published` (50), `pending` (9), `failed` (1).
> Load it to test the scheduler without waiting for real posts to be created.

**Load scheduler test data into MySQL:**
```python
import pandas as pd
from database.db_connection import get_session
from sqlalchemy import text

df = pd.read_csv("data/raw/05_scheduler_data.csv")
# Insert pending rows to test check_due_posts()
pending = df[df["status"] == "pending"][["post_id","platform","scheduled_date","scheduled_time"]]
print(f"Found {len(pending)} pending posts to test scheduler with")
```

```python
import json
import time
import schedule
from datetime import datetime, timedelta
from database.db_connection import get_session
from sqlalchemy import text
from publisher.publisher_manager import publish_post

def schedule_post(post_id: int, platform: str):
    best = json.load(open("best_time.json"))
    timing = next((b for b in best if b["platform"] == platform), None)
    if not timing:
        return
    
    now = datetime.now()
    target = now.replace(hour=int(timing["hour_posted"]), minute=0, second=0)
    if target < now:
        target += timedelta(days=1)
    
    with get_session() as session:
        session.execute(
            text("INSERT INTO schedules (post_id, scheduled_time, platform) VALUES (:pid, :t, :p)"),
            {"pid": post_id, "t": target, "p": platform}
        )
        session.commit()
    print(f"Post {post_id} scheduled for {target}")

def check_due_posts():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:00")
    with get_session() as session:
        result = session.execute(
            text("SELECT id, post_id, platform FROM schedules WHERE scheduled_time <= :now AND status = 'pending'"),
            {"now": now}
        ).fetchall()
        for row in result:
            publish_post(row.post_id, row.platform)
            session.execute(
                text("UPDATE schedules SET status = 'published' WHERE id = :id"),
                {"id": row.id}
            )
        session.commit()

schedule.every(1).minutes.do(check_due_posts)

if __name__ == "__main__":
    print("Scheduler running...")
    while True:
        schedule.run_pending()
        time.sleep(30)
```

---

### Task 24–26 — Platform Publishers

**`publisher/facebook_publisher.py`:**

```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def publish_to_facebook(caption: str, image_url: str = None) -> dict:
    token   = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    url     = f"https://graph.facebook.com/{page_id}/feed"
    payload = {"message": caption, "access_token": token}
    if image_url:
        payload["link"] = image_url
    resp = httpx.post(url, data=payload)
    return resp.json()
```

**`publisher/instagram_publisher.py`:**

```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def publish_to_instagram(caption: str, image_url: str) -> dict:
    token   = os.getenv("FACEBOOK_ACCESS_TOKEN")
    user_id = os.getenv("INSTAGRAM_USER_ID")
    
    # Step 1: Create media container
    create_resp = httpx.post(
        f"https://graph.facebook.com/{user_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token}
    ).json()
    
    if "id" not in create_resp:
        return {"error": "Media container failed", "details": create_resp}
    
    # Step 2: Publish container
    publish_resp = httpx.post(
        f"https://graph.facebook.com/{user_id}/media_publish",
        data={"creation_id": create_resp["id"], "access_token": token}
    ).json()
    return publish_resp
```

**`publisher/linkedin_publisher.py`:**

```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def publish_to_linkedin(caption: str) -> dict:
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": "urn:li:person:me",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    resp = httpx.post("https://api.linkedin.com/v2/ugcPosts", json=payload, headers=headers)
    return resp.json()
```

**`publisher/twitter_publisher.py`:**

```python
import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

def publish_to_twitter(caption: str) -> dict:
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
    )
    # Twitter limit: 280 characters
    text = caption[:280]
    response = client.create_tweet(text=text)
    return {"tweet_id": response.data["id"]}
```

---

### Task 27 — Publisher Manager (`publisher/publisher_manager.py`)

```python
from database.db_connection import get_session
from sqlalchemy import text

def publish_post(post_id: int, platform: str) -> dict:
    with get_session() as session:
        post = session.execute(
            text("SELECT caption, image_url FROM posts WHERE id = :id"),
            {"id": post_id}
        ).fetchone()
    
    if not post:
        return {"error": f"Post {post_id} not found"}
    
    caption, image_url = post.caption, post.image_url
    platform = platform.lower()
    
    if platform == "facebook":
        from publisher.facebook_publisher import publish_to_facebook
        return publish_to_facebook(caption, image_url)
    elif platform == "instagram":
        from publisher.instagram_publisher import publish_to_instagram
        return publish_to_instagram(caption, image_url)
    elif platform == "linkedin":
        from publisher.linkedin_publisher import publish_to_linkedin
        return publish_to_linkedin(caption)
    elif platform == "twitter":
        from publisher.twitter_publisher import publish_to_twitter
        return publish_to_twitter(caption)
    else:
        return {"error": f"Unknown platform: {platform}"}
```

---

## PHASE 7 — ANALYTICS & DASHBOARD
### Tasks 28–29

---

### Task 28 — Analytics Fetcher (`api/analytics_fetcher.py`)

> **Dataset Used:** `data/raw/04_analytics_data.csv`
> Simulates what the Facebook/Instagram API returns when you fetch metrics.
> Columns include: `likes`, `comments`, `shares`, `saves`, `reach`, `impressions`, `video_views`, `link_clicks`, `engagement_rate`, `click_through_rate`.
> Use this data to populate the `analytics` MySQL table and test the dashboard without real API keys.

**Load analytics test data into MySQL:**
```python
import pandas as pd
from database.db_connection import get_session
from sqlalchemy import text

df = pd.read_csv("data/raw/04_analytics_data.csv")
print(f"Analytics test data: {len(df)} records across {df['platform'].nunique()} platforms")
# Insert into analytics table for dashboard testing
```

```python
import os
import schedule
import time
import httpx
from database.db_connection import get_session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

def fetch_facebook_analytics():
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    with get_session() as session:
        posts = session.execute(
            text("SELECT id FROM posts WHERE platform='facebook' AND status='published'")
        ).fetchall()
        for post in posts:
            resp = httpx.get(
                f"https://graph.facebook.com/{post.id}",
                params={"fields": "likes.summary(true),shares,comments.summary(true)", "access_token": token}
            ).json()
            likes    = resp.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = resp.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares   = resp.get("shares", {}).get("count", 0)
            session.execute(
                text("INSERT INTO analytics (post_id, likes, comments, shares) VALUES (:pid, :l, :c, :s)"),
                {"pid": post.id, "l": likes, "c": comments, "s": shares}
            )
        session.commit()
    print("Analytics updated.")

schedule.every(24).hours.do(fetch_facebook_analytics)

if __name__ == "__main__":
    fetch_facebook_analytics()
    while True:
        schedule.run_pending()
        time.sleep(3600)
```

---

### Task 29 — Streamlit Dashboard (`dashboard/dashboard.py`)

> **Dataset Used:** `data/raw/04_analytics_data.csv` + `data/raw/06_best_time_dataset.csv`
> If MySQL is not set up yet, load the CSV files directly into the dashboard for testing.

**Test the dashboard without MySQL using CSV:**
```python
# Replace the MySQL query with CSV loading for quick testing
df_posts = pd.read_csv("data/raw/04_analytics_data.csv")
df_best_time = pd.read_csv("data/raw/06_best_time_dataset.csv")
```

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db_connection import get_session
from sqlalchemy import text

st.set_page_config(page_title="AI Social Media Dashboard", layout="wide")
st.title("AI Social Media Platform — Analytics Dashboard")

with get_session() as session:
    df_posts = pd.read_sql(
        "SELECT p.id, p.platform, p.caption, p.created_at, "
        "COALESCE(a.likes,0) as likes, COALESCE(a.reach,0) as reach "
        "FROM posts p LEFT JOIN analytics a ON p.id = a.post_id",
        session.bind
    )

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts",    len(df_posts))
col2.metric("Total Likes",    int(df_posts["likes"].sum()))
col3.metric("Total Reach",    int(df_posts["reach"].sum()))
col4.metric("Avg Engagement", f"{df_posts['likes'].mean():.1f}")

# --- Charts ---
col_left, col_right = st.columns(2)
with col_left:
    fig = px.line(df_posts, x="created_at", y="likes", color="platform", title="Likes Over Time")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    fig2 = px.bar(
        df_posts.groupby("platform")["likes"].sum().reset_index(),
        x="platform", y="likes", title="Total Likes by Platform"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Top 10 Posts ---
st.subheader("Top 10 Posts by Likes")
st.dataframe(
    df_posts.nlargest(10, "likes")[["platform", "caption", "likes", "reach", "created_at"]],
    use_container_width=True
)
```

Run:

```bash
streamlit run dashboard/dashboard.py
```

---

## PHASE 8 — TESTING & DEPLOYMENT
### Tasks 30–35

---

### Task 30 — Module Testing Checklist

Run each test manually before integration:

| Module | Test Command | Expected Result |
|--------|-------------|-----------------|
| Caption Generator | `python -c "from nlp.caption_generator import generate_captions; print(generate_captions('AI', 'instagram'))"` | 3 captions printed |
| Keyword Extractor | `python -c "from nlp.keyword_extractor import extract_keywords; print(extract_keywords('AI tools are amazing for social media'))"` | List of keywords |
| ML Predictor | `python -c "from ml_models.predictor import predict_score; print(predict_score('Great post!', 'instagram'))"` | Number between 0–100 |
| DB Connection | `python -c "from database.db_connection import get_session; print('DB OK')"` | DB OK |
| API | `curl http://localhost:8000/` | `{"status":"running"}` |

---

### Task 31 — Integration Test

Run this end-to-end test script:

```python
# test_integration.py
import httpx

BASE = "http://localhost:8000"

# 1. Generate captions
resp = httpx.post(f"{BASE}/api/content/generate",
    json={"topic": "AI tools for marketers", "platform": "instagram"})
print("Generate:", resp.json())

# 2. Score a caption
resp2 = httpx.post(f"{BASE}/api/content/score",
    json={"caption": "AI is transforming marketing!", "platform": "instagram"})
print("Score:", resp2.json())
```

---

### Task 32–34 — Deployment

**FastAPI on Render.com:**
1. Go to https://render.com → New Web Service
2. Connect GitHub repo
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add all `.env` variables in Environment tab

**MySQL on Railway.app:**
1. Go to https://railway.app → New Project → MySQL
2. Copy the connection URL
3. Update `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` in Render environment vars

**Dashboard on Streamlit Cloud:**
1. Go to https://streamlit.io/cloud → New App
2. Connect GitHub repo
3. Set main file: `dashboard/dashboard.py`
4. Add secrets in the Secrets tab (same as .env content)

---

### Task 35 — Final Deployment Checklist

```
[ ] All API keys in .env
[ ] .env is in .gitignore (verify: git status should NOT show .env)
[ ] requirements.txt is up to date: pip freeze > requirements.txt
[ ] engagement_model.pkl exists in ml_models/
[ ] best_time.json exists in project root
[ ] MySQL tables created on Railway
[ ] All environment variables added to Render
[ ] Dashboard connected to Railway MySQL
[ ] Test all endpoints via Postman
```

---

## PHASE 9 — AI QUALITY & SAFETY
### Tasks 36–39

---

### Task 36 — Plagiarism Checker (`nlp/plagiarism_checker.py`)

```python
import difflib
from database.db_connection import get_session
from sqlalchemy import text

def is_plagiarised(new_caption: str, threshold: float = 0.80) -> bool:
    with get_session() as session:
        existing = session.execute(text("SELECT caption FROM posts")).fetchall()
    
    for row in existing:
        ratio = difflib.SequenceMatcher(None, new_caption.lower(), row.caption.lower()).ratio()
        if ratio > threshold:
            return True
    return False
```

Use in `api/content.py` — after generating captions, filter out plagiarised ones:

```python
from nlp.plagiarism_checker import is_plagiarised
captions = [c for c in captions if not is_plagiarised(c)]
```

---

### Task 37 — Content Moderator (`nlp/content_moderator.py`)

```python
from transformers import pipeline

# Load once at startup
_moderator = pipeline("text-classification", model="unitary/toxic-bert")

def is_toxic(text: str, threshold: float = 0.7) -> bool:
    result = _moderator(text[:512])[0]
    return result["label"] == "toxic" and result["score"] > threshold
```

Use in `api/content.py` — block toxic captions before returning:

```python
from nlp.content_moderator import is_toxic
captions = [c for c in captions if not is_toxic(c)]
```

---

### Task 38 — Multilingual Translator (`nlp/translator.py`)

```python
from googletrans import Translator

_translator = Translator()

SUPPORTED_LANGUAGES = {
    "hindi": "hi", "marathi": "mr", "tamil": "ta",
    "telugu": "te", "bengali": "bn", "gujarati": "gu", "kannada": "kn"
}

def translate_caption(text: str, language: str) -> str:
    lang_code = SUPPORTED_LANGUAGES.get(language.lower())
    if not lang_code:
        return text
    result = _translator.translate(text, dest=lang_code)
    return result.text
```

Add endpoint to `api/content.py`:

```python
from nlp.translator import translate_caption

class TranslateRequest(BaseModel):
    caption: str
    language: str

@router.post("/translate")
def translate(req: TranslateRequest):
    return {"translated": translate_caption(req.caption, req.language)}
```

---

### Task 39 — AI Image Prompt Generator (`nlp/image_generator.py`)

```python
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def generate_image_prompt(caption: str) -> str:
    """Convert a social media caption into a Stable Diffusion image prompt."""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{
            "role": "user",
            "content": f"Convert this social media caption into a short, vivid image generation prompt (max 20 words): {caption}"
        }],
        max_tokens=60
    )
    return resp.choices[0].message.content.strip()

def generate_image(caption: str) -> str:
    """Returns image URL from Stable Diffusion API."""
    prompt = generate_image_prompt(caption)
    api_key = os.getenv("STABLE_DIFFUSION_API_KEY")
    resp = httpx.post(
        "https://stablediffusionapi.com/api/v3/text2img",
        json={"key": api_key, "prompt": prompt, "width": "512", "height": "512", "samples": "1"},
        timeout=30
    ).json()
    return resp.get("output", [""])[0]
```

---

## PHASE 10 — SMART ANALYTICS
### Tasks 40–43

---

### Task 40 — Weekly Email Reporter (`api/email_reporter.py`)

> **Dataset Used:** `data/raw/04_analytics_data.csv`
> Use this CSV to test the weekly report without waiting a full week of real data.
> It has likes, reach, platform and fetch_date columns needed to build the HTML email table.

```python
import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.db_connection import get_session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

def send_weekly_report():
    with get_session() as session:
        rows = session.execute(text(
            "SELECT platform, COUNT(*) as posts, SUM(a.likes) as total_likes "
            "FROM posts p LEFT JOIN analytics a ON p.id=a.post_id "
            "WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) "
            "GROUP BY platform"
        )).fetchall()
    
    body = "<h2>Weekly Social Media Report</h2><table border='1'><tr><th>Platform</th><th>Posts</th><th>Likes</th></tr>"
    for row in rows:
        body += f"<tr><td>{row.platform}</td><td>{row.posts}</td><td>{row.total_likes or 0}</td></tr>"
    body += "</table>"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly Social Media Summary"
    msg["From"]    = os.getenv("GMAIL_USER")
    msg["To"]      = os.getenv("GMAIL_USER")
    msg.attach(MIMEText(body, "html"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
        server.send_message(msg)
    print("Weekly report sent!")

schedule.every().monday.at("09:00").do(send_weekly_report)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)
```

> How to get Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords

---

### Task 41 — A/B Testing Engine (`ml_models/ab_tester.py`)

> **Dataset Used:** `data/raw/08_ab_testing_data.csv`
> Contains 10 completed A/B tests with clear winners, improvement percentages, and actionable insights.
> Key insight from this data: question-based CTAs get 51% more comments, specific numbers increase shares by 90%, POV format increases reel reach by 53%.
> Use the `insight` column from winner rows to update the Groq system prompt in Task 43.

**Load A/B insights for system prompt update:**
```python
import pandas as pd
df = pd.read_csv("data/raw/08_ab_testing_data.csv")
winner_insights = df[df["status"] == "completed"][["winner", "improvement_percent", "insight"]]
print(winner_insights.to_string())  # Review before updating system prompt
```

```python
import json
import time
from database.db_connection import get_session
from sqlalchemy import text

def run_ab_test(post_id_a: int, post_id_b: int, platform: str, wait_hours: int = 24):
    """Post both captions, wait, then compare and update the generator."""
    from publisher.publisher_manager import publish_post
    publish_post(post_id_a, platform)
    time.sleep(2)
    publish_post(post_id_b, platform)
    
    print(f"A/B test started. Check results in {wait_hours} hours.")

def evaluate_ab_test(post_id_a: int, post_id_b: int) -> dict:
    with get_session() as session:
        def get_engagement(pid):
            row = session.execute(
                text("SELECT COALESCE(likes,0)+COALESCE(shares,0)*2+COALESCE(comments,0)*3 as score "
                     "FROM analytics WHERE post_id=:pid ORDER BY fetched_at DESC LIMIT 1"),
                {"pid": pid}
            ).fetchone()
            return row.score if row else 0
        
        score_a = get_engagement(post_id_a)
        score_b = get_engagement(post_id_b)
        winner  = post_id_a if score_a >= score_b else post_id_b
    
    return {"winner_post_id": winner, "score_a": score_a, "score_b": score_b}
```

---

### Task 42 — Competitor Tracker (`api/competitor_tracker.py`)

> **Dataset Used:** `data/raw/09_competitor_tracking_data.csv`
> Contains 10 competitor brands tracked across all 4 platforms.
> `alert_triggered = 1` rows already have the `alert_reason` written — use these to test your Telegram alert system.
> Also contains `data/raw/04_analytics_data.csv` for comparing our metrics vs competitors.

**Test competitor alerts using dummy data:**
```python
import pandas as pd
df = pd.read_csv("data/raw/09_competitor_tracking_data.csv")
alerts = df[df["alert_triggered"] == 1]
print(f"{len(alerts)} competitor alerts found:")
for _, row in alerts.iterrows():
    print(f"  [{row['brand_name']}] {row['alert_reason']}")
```

```python
import os
import httpx
import schedule
import time
from dotenv import load_dotenv

load_dotenv()

COMPETITOR_PAGE_IDS = ["competitor_page_id_1", "competitor_page_id_2"]  # Replace with real IDs

def check_competitors():
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    for page_id in COMPETITOR_PAGE_IDS:
        resp = httpx.get(
            f"https://graph.facebook.com/{page_id}",
            params={"fields": "fan_count,talking_about_count", "access_token": token}
        ).json()
        fans = resp.get("fan_count", 0)
        talking = resp.get("talking_about_count", 0)
        engagement_rate = (talking / fans * 100) if fans > 0 else 0
        
        # Alert if competitor engagement > your threshold
        if engagement_rate > 20:
            print(f"ALERT: Competitor {page_id} has {engagement_rate:.1f}% engagement rate!")
            # TODO: Send Telegram notification (Task 52)

schedule.every().day.at("08:00").do(check_competitors)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)
```

---

### Task 43 — Feedback Loop (`api/feedback_loop.py`)

```python
import schedule
import time
from database.db_connection import get_session
from sqlalchemy import text

SYSTEM_PROMPT_FILE = "nlp/system_prompt.txt"

def update_system_prompt():
    with get_session() as session:
        # Get top 5 performing captions this week
        winners = session.execute(text(
            "SELECT p.caption, a.likes FROM posts p JOIN analytics a ON p.id=a.post_id "
            "WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) "
            "ORDER BY a.likes DESC LIMIT 5"
        )).fetchall()
        
        # Get bottom 5
        losers = session.execute(text(
            "SELECT p.caption FROM posts p JOIN analytics a ON p.id=a.post_id "
            "WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) "
            "ORDER BY a.likes ASC LIMIT 5"
        )).fetchall()
    
    winner_examples = "\n".join([f"- {w.caption}" for w in winners])
    loser_examples  = "\n".join([f"- {l.caption}" for l in losers])
    
    new_prompt = f"""You are an expert social media copywriter.

WRITE MORE LIKE THESE (high engagement this week):
{winner_examples}

AVOID PATTERNS LIKE THESE (low engagement):
{loser_examples}

Always be engaging, platform-appropriate, and include a call-to-action."""
    
    with open(SYSTEM_PROMPT_FILE, "w") as f:
        f.write(new_prompt)
    print("System prompt updated with this week's learnings.")

schedule.every().sunday.at("23:00").do(update_system_prompt)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)
```

---

## PHASE 11 — USER INTERFACE
### Tasks 44–47

---

### Task 44 — Multi-Page Admin Panel (`dashboard/admin_panel.py`)

```python
import streamlit as st

st.set_page_config(page_title="Admin Panel", layout="wide", page_icon="🤖")

PAGES = {
    "Generate Content": "pages/generate.py",
    "Approve Posts":    "pages/approve.py",
    "Content Calendar": "pages/calendar.py",
    "Analytics":        "pages/analytics.py",
    "Settings":         "pages/settings.py"
}

page = st.sidebar.selectbox("Navigate", list(PAGES.keys()))
```

Create `dashboard/pages/generate.py`:

```python
import streamlit as st
import httpx

st.title("Generate Content")
topic    = st.text_input("Topic")
platform = st.selectbox("Platform", ["instagram", "facebook", "twitter", "linkedin"])
tone     = st.selectbox("Tone", ["engaging", "professional", "funny", "inspirational"])

if st.button("Generate Captions") and topic:
    with st.spinner("Generating..."):
        resp = httpx.post(
            "http://localhost:8000/api/content/generate",
            json={"topic": topic, "platform": platform, "tone": tone},
            timeout=30
        ).json()
    
    for i, item in enumerate(resp["results"], 1):
        with st.expander(f"Option {i} — Score: {item['predicted_engagement']}"):
            st.write(item["caption"])
            st.write("Hashtags:", " ".join(item["hashtags"]))
            if st.button(f"Schedule This Post", key=f"schedule_{i}"):
                st.success("Post saved for scheduling!")
```

Run the admin panel:

```bash
streamlit run dashboard/admin_panel.py
```

---

### Task 45 — Role-Based Authentication (`api/auth.py`)

> **Dataset Used:** `data/raw/10_users_data.csv`
> Contains 15 test users across 3 roles (admin, editor, viewer) for 10 different brands.
> Use these credentials to test all 3 permission levels in the admin panel.

**Test credentials from `10_users_data.csv`:**
| Username | Role | Password | Brand |
|----------|------|---------|-------|
| admin_techcreate | admin | admin123 | TechCreate |
| editor_techcreate | editor | editor123 | TechCreate |
| viewer_techcreate | viewer | viewer123 | TechCreate |
| admin_growthlb | admin | admin123 | GrowthLab |
| admin_styleco | admin | admin123 | StyleCo |

```python
import os
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET", "change-me")
ALGORITHM  = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# In production, store users in DB. This is a simple demo.
USERS = {
    "admin":  {"password": pwd_context.hash("admin123"), "role": "admin"},
    "editor": {"password": pwd_context.hash("editor123"), "role": "editor"},
    "viewer": {"password": pwd_context.hash("viewer123"), "role": "viewer"},
}

def create_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": data["sub"], "role": data["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(required: str):
    HIERARCHY = {"viewer": 0, "editor": 1, "admin": 2}
    def check(user: dict = Depends(get_current_user)):
        if HIERARCHY.get(user["role"], 0) < HIERARCHY.get(required, 0):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check
```

---

### Task 46 — Visual Content Calendar (`dashboard/pages/calendar.py`)

```python
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from database.db_connection import get_session
from sqlalchemy import text

st.title("Content Calendar")

with get_session() as session:
    df = pd.read_sql(
        "SELECT p.caption, s.scheduled_time, s.platform, s.status "
        "FROM schedules s JOIN posts p ON s.post_id=p.id "
        "ORDER BY s.scheduled_time",
        session.bind
    )

if df.empty:
    st.info("No scheduled posts yet.")
else:
    PLATFORM_COLORS = {
        "instagram": "rgb(225,48,108)",
        "facebook":  "rgb(24,119,242)",
        "twitter":   "rgb(29,161,242)",
        "linkedin":  "rgb(0,119,181)"
    }
    
    gantt_data = []
    for _, row in df.iterrows():
        start = pd.to_datetime(row["scheduled_time"])
        gantt_data.append({
            "Task":   row["platform"].capitalize(),
            "Start":  start.strftime("%Y-%m-%d %H:%M"),
            "Finish": (start + pd.Timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "Resource": row["platform"]
        })
    
    fig = ff.create_gantt(gantt_data, index_col="Resource", show_colorbar=True,
                          title="Scheduled Posts Calendar")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True)
```

---

### Task 47 — Bulk Upload Endpoint (`api/content.py`)

Add to `api/content.py`:

```python
import csv
import io
from fastapi import UploadFile, File

@router.post("/bulk-generate")
async def bulk_generate(file: UploadFile = File(...)):
    content = await file.read()
    reader  = csv.DictReader(io.StringIO(content.decode("utf-8")))
    results = []
    
    for row in reader:
        topic    = row.get("topic", "")
        platform = row.get("platform", "instagram")
        if not topic:
            continue
        captions = generate_captions(topic, platform)
        score    = predict_score(captions[0], platform) if captions else 0
        results.append({
            "topic": topic,
            "platform": platform,
            "best_caption": captions[0] if captions else "",
            "score": round(score, 2)
        })
    
    return {"processed": len(results), "results": results}
```

CSV format expected:
```
topic,platform
AI tools for marketers,instagram
Remote work tips,linkedin
Healthy recipes,facebook
```

---

## PHASE 12 — PRODUCTION HARDENING
### Tasks 48–52

---

### Task 48 — Redis Caching (`api/cache.py`)

```python
import os
import json
import redis
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def cache(key_prefix: str, ttl_seconds: int):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{key_prefix}:{args}:{kwargs}"
            cached = r.get(key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            r.setex(key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator
```

Use it:

```python
# In nlp/hashtag_generator.py
from api.cache import cache

@cache("hashtags", ttl_seconds=7200)   # 2 hour TTL
def generate_hashtags(caption: str, platform: str, count: int = 10) -> list[str]:
    ...

# In ml_models/predictor.py
from api.cache import cache

@cache("ml_score", ttl_seconds=3600)   # 1 hour TTL
def predict_score(caption: str, platform: str, ...) -> float:
    ...
```

Install and start Redis:
- Windows: Download from https://github.com/microsoftarchive/redis/releases
- Run: `redis-server`

---

### Task 49 — Rotating Log Handler (`api/logger.py`)

```python
import logging
import os
from logging.handlers import RotatingFileHandler
from collections import deque
from datetime import datetime

os.makedirs("logs", exist_ok=True)

# Main logger
logger = logging.getLogger("ai_social_media")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB per file
    backupCount=10
)
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())  # Also print to console

# Failure tracking for alerting
_recent_failures = deque(maxlen=100)

def log_failure(message: str):
    logger.error(message)
    _recent_failures.append(datetime.now())
    
    # Count failures in last hour
    from datetime import timedelta
    now = datetime.now()
    recent = sum(1 for t in _recent_failures if now - t < timedelta(hours=1))
    if recent >= 3:
        logger.critical(f"ALERT: {recent} failures in the last hour!")
        # TODO: Send Telegram alert (Task 52)
```

Use in every module:

```python
from api.logger import logger, log_failure

logger.info("Caption generated successfully")
log_failure("Publisher failed: timeout")
```

---

### Task 50 — Nightly Database Backup (`api/backup.py`)

```python
import os
import subprocess
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{BACKUP_DIR}/backup_{timestamp}.sql"
    
    cmd = (
        f"mysqldump -h {os.getenv('DB_HOST')} "
        f"-u {os.getenv('DB_USER')} "
        f"-p{os.getenv('DB_PASSWORD')} "
        f"{os.getenv('DB_NAME')} > {filename}"
    )
    
    result = subprocess.run(cmd, shell=True, capture_output=True)
    
    if result.returncode == 0:
        print(f"Backup saved: {filename}")
        cleanup_old_backups()
    else:
        print(f"Backup FAILED: {result.stderr.decode()}")

def cleanup_old_backups(keep_days: int = 30):
    """Delete backups older than 30 days."""
    import glob
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(days=keep_days)
    for f in glob.glob(f"{BACKUP_DIR}/backup_*.sql"):
        file_time = datetime.fromtimestamp(os.path.getmtime(f))
        if file_time < cutoff:
            os.remove(f)
            print(f"Deleted old backup: {f}")

schedule.every().day.at("02:00").do(backup_database)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)
```

---

### Task 51 — Rate Limiter & Security (`api/main.py`)

Update `api/main.py`:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.content import router as content_router

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="AI Social Media API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict to your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-dashboard.streamlit.app"],  # Change in production
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"]
)

app.include_router(content_router, prefix="/api/content")

@app.get("/")
@limiter.limit("20/minute")
def root(request: Request):
    return {"status": "running"}
```

Add rate limit to content endpoints:

```python
@router.post("/generate")
@limiter.limit("20/minute")
def generate(request: Request, req: GenerateRequest):
    ...
```

---

### Task 52 — Telegram Notification Bot (`api/notifier.py`)

```python
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message: str):
    """Send a Telegram message synchronously."""
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured. Skipping notification.")
        return
    try:
        httpx.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram notification failed: {e}")

def notify_publish(platform: str, post_id: int):
    send_telegram(f"✅ *Post Published*\nPlatform: {platform}\nPost ID: {post_id}")

def notify_performance_spike(platform: str, metric: str, value: float):
    send_telegram(f"📈 *Performance Spike!*\nPlatform: {platform}\n{metric}: {value:.1f}")

def notify_failure(module: str, error: str):
    send_telegram(f"🚨 *System Alert*\nModule: {module}\nError: {error}")
```

**How to set up Telegram bot:**
1. Open Telegram → search `@BotFather`
2. Send `/newbot`, give it a name
3. Copy the token → paste in `.env` as `TELEGRAM_BOT_TOKEN`
4. Open your bot in Telegram, send any message
5. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
6. Copy the `chat.id` from the response → paste in `.env` as `TELEGRAM_CHAT_ID`

Use throughout the project:

```python
from api.notifier import notify_publish, notify_failure

# In publisher_manager.py
notify_publish(platform, post_id)

# In logger.py
notify_failure("Publisher", str(error))
```

---

## PRED — Smart Post Performance Predictor Dashboard

This is the new feature added to the project. Add it as a new page in the admin panel.

Create `dashboard/pages/predictor.py`:

```python
import streamlit as st
import httpx

st.title("PRED — Smart Post Performance Predictor")
st.caption("See your post's predicted performance before you publish.")

col1, col2 = st.columns([2, 1])

with col1:
    caption  = st.text_area("Write your caption", height=150,
                             placeholder="Type your caption here...")
    platform = st.selectbox("Platform", ["instagram", "facebook", "twitter", "linkedin"])
    hour     = st.slider("Planned posting hour (24h format)", 0, 23, 12)

with col2:
    st.markdown("### Predicted Performance")
    
    if caption and len(caption) > 10:
        resp = httpx.post(
            "http://localhost:8000/api/content/score",
            json={"caption": caption, "platform": platform, "hour": hour},
            timeout=10
        ).json()
        
        score = resp.get("predicted_engagement", 0)
        
        # Color code the score
        color = "🟢" if score > 60 else "🟡" if score > 35 else "🔴"
        
        st.metric("Engagement Score", f"{color} {score:.1f} / 100")
        st.metric("Est. Likes",  f"~{int(score * 15):,}")
        st.metric("Est. Reach",  f"~{int(score * 80):,}")
        
        if score > 60:
            st.success("Great post! This is predicted to perform well.")
        elif score > 35:
            st.warning("Average performance expected. Try improving the caption.")
        else:
            st.error("Low engagement predicted. Consider rewriting.")
        
        st.info(f"💡 Best time to post: {hour}:00 on {platform.capitalize()}")
    else:
        st.info("Start typing your caption to see predictions...")
```

---

## TESTING TABLE

| Task | File | Test Command | Pass Criteria |
|------|------|-------------|---------------|
| 9 | `nlp/caption_generator.py` | `python -c "from nlp.caption_generator import generate_captions; print(generate_captions('AI', 'instagram'))"` | 3 captions |
| 10 | `nlp/keyword_extractor.py` | `python -c "from nlp.keyword_extractor import extract_keywords; print(extract_keywords('AI marketing tools are great'))"` | List of keywords |
| 11 | `nlp/hashtag_generator.py` | `python -c "from nlp.hashtag_generator import generate_hashtags; print(generate_hashtags('AI tools', 'instagram'))"` | List of hashtags |
| 16 | `ml_models/` | `python ml_models/train_model.py` | R² > 0.6, pkl saved |
| 18 | `api/main.py` | `curl http://localhost:8000/` | `{"status":"running"}` |
| 19 | `api/content.py` | Postman POST `/api/content/generate` | 3 scored captions |
| 20 | `database/db_connection.py` | `python -c "from database.db_connection import get_session; print('OK')"` | OK |
| 27 | `publisher/publisher_manager.py` | Postman test with test post | Published response |
| 29 | `dashboard/dashboard.py` | `streamlit run dashboard/dashboard.py` | Dashboard opens |
| 52 | `api/notifier.py` | `python -c "from api.notifier import send_telegram; send_telegram('Test')"` | Telegram message received |

---

## COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'groq'` | Package not installed | `pip install groq` |
| `Access denied for user 'root'@'localhost'` | Wrong MySQL password | Check `.env` DB_PASSWORD |
| `Connection refused` when running FastAPI | Uvicorn not running | `uvicorn api.main:app --reload` |
| `spaCy model not found` | Model not downloaded | `python -m spacy download en_core_web_sm` |
| `FileNotFoundError: engagement_model.pkl` | Model not trained | Run `python ml_models/train_model.py` first |
| `pytrends TooManyRequestsError` | Rate limited by Google | Add `time.sleep(5)` before pytrends calls |
| `Telegram: chat not found` | Wrong chat ID | Redo the getUpdates step after messaging your bot |
| `RateLimitExceeded` | Too many API calls | Reduce test frequency or increase limit in slowapi |

---

## QUICK START (Run everything locally)

```bash
# Terminal 1 — Backend API
uvicorn api.main:app --reload

# Terminal 2 — Trend Analyzer (background)
python nlp/trend_analyzer.py

# Terminal 3 — Scheduler (background)
python scheduler/auto_scheduler.py

# Terminal 4 — Analytics Fetcher (background)
python api/analytics_fetcher.py

# Terminal 5 — Dashboard
streamlit run dashboard/dashboard.py

# Terminal 6 — Admin Panel
streamlit run dashboard/admin_panel.py --server.port 8502
```

---

## DATASET QUICK REFERENCE (Final Summary)

```
Task 6  → Uses: data/raw/01_social_media_engagement.csv   (raw posts, 60 rows)
Task 7  → Uses: data/raw/01_social_media_engagement.csv   (input)
          Creates: data/cleaned/engagement_clean.csv      (output)
Task 9  → Uses: data/raw/03_nlp_captions_dataset.csv      (caption examples for Groq prompt)
Task 10 → Uses: data/raw/03_nlp_captions_dataset.csv      (keyword extraction reference)
Task 11 → Uses: data/raw/03_nlp_captions_dataset.csv      (hashtag examples)
               + data/raw/07_trends_data.csv              (trending hashtags)
Task 12 → Uses: data/raw/07_trends_data.csv               (pre-load trends table)
Task 13 → Uses: data/raw/02_ml_training_dataset.csv       (8 features ready)
Task 14 → Uses: data/raw/02_ml_training_dataset.csv       (train Random Forest)
Task 15 → Uses: data/raw/02_ml_training_dataset.csv       (train XGBoost)
Task 16 → Creates: ml_models/engagement_model.pkl         (saved model)
Task 17 → Uses: data/raw/06_best_time_dataset.csv         (create best_time.json)
          Creates: best_time.json                         (output)
Task 22 → Uses: data/raw/05_scheduler_data.csv            (test scheduler table)
Task 23 → Uses: data/raw/05_scheduler_data.csv            (pending posts)
Task 28 → Uses: data/raw/04_analytics_data.csv            (test analytics table)
Task 29 → Uses: data/raw/04_analytics_data.csv            (dashboard charts)
               + data/raw/06_best_time_dataset.csv        (best time chart)
Task 40 → Uses: data/raw/04_analytics_data.csv            (weekly email data)
Task 41 → Uses: data/raw/08_ab_testing_data.csv           (A/B test results)
Task 42 → Uses: data/raw/09_competitor_tracking_data.csv  (competitor alerts)
               + data/raw/04_analytics_data.csv           (our metrics)
Task 45 → Uses: data/raw/10_users_data.csv                (test user credentials)
```

---

*Document Version 2.1 — Includes PRED Feature + 10 Datasets Mapped | 52 Tasks | 12 Phases*
