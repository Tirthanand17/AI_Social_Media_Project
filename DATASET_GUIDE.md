# Dataset Guide — AI Social Media Platform
## 10 Datasets | What Each is For | Which Task Uses It

---

## Public dataset note

The bundled CSV files are **sample/demo datasets for this portfolio project**. They are intended for reproducible development, testing, and classroom demonstration and should not be interpreted as live customer accounts or current social-platform measurements. Example user emails use the reserved `example.com` domain.

## Quick Reference Table

| File | Dataset Name | Task(s) | Size | Purpose |
|------|-------------|---------|------|---------|
| `01_social_media_engagement.csv` | Core Engagement Data | Task 6, 7 | 60 posts | Raw data for data cleaning phase |
| `02_ml_training_dataset.csv` | ML Training Data | Task 13, 14, 15, 16, 17 | 50 posts | Train Random Forest + XGBoost models |
| `03_nlp_captions_dataset.csv` | NLP Captions Data | Task 9, 10, 11 | 50 captions | Caption analysis + keyword extraction |
| `04_analytics_data.csv` | Platform Analytics | Task 28, 40, 42 | 50 records | Analytics fetcher + weekly email report |
| `05_scheduler_data.csv` | Scheduler History | Task 22, 23, 30 | 60 records | Auto scheduler testing + integration test |
| `06_best_time_dataset.csv` | Best Time to Post | Task 17, 29 | 49 records | Best time recommender + dashboard charts |
| `07_trends_data.csv` | Trending Keywords | Task 12, 43, 49 | 30 trends | Trend analyzer + hashtag generator |
| `08_ab_testing_data.csv` | A/B Test Results | Task 41 | 10 tests | A/B testing engine training |
| `09_competitor_tracking_data.csv` | Competitor Data | Task 42 | 12 records | Competitor tracker baseline |
| `10_users_data.csv` | Users & Roles | Task 45 | 15 users | Role-based auth + admin panel |

---

## Dataset 1 — Core Engagement Data
**File:** `01_social_media_engagement.csv`
**Tasks:** Task 6 (download datasets), Task 7 (clean data)

This is the bundled RAW sample dataset used by the project and stored in `data/raw/`.
After Task 7 (`clean_data.py`), it becomes `data/cleaned/engagement_clean.csv`.

**Key Columns:**
- `post_id` — unique ID for each post
- `platform` — Instagram / Facebook / Twitter / LinkedIn
- `caption` — actual post text
- `content_type` — image / video / reel / text
- `day_of_week` — Monday to Sunday
- `hour_posted` — 0 to 23
- `likes_count`, `shares_count`, `comments_count` — engagement numbers
- `impressions`, `engagement_rate` — reach metrics
- `sentiment_score` — 0 to 1 (positive)
- `has_image` — 1 or 0

---

## Dataset 2 — ML Training Dataset
**File:** `02_ml_training_dataset.csv`
**Tasks:** Task 13 (feature engineering), Task 14 (Random Forest), Task 15 (XGBoost), Task 16 (save model), Task 17 (best time)

This is Dataset 1 AFTER feature engineering. All 8 ML features are ready.

**The 8 ML Features used for training:**
- `platform_encoded` — Instagram=0, Facebook=1, Twitter=2, LinkedIn=3
- `day_encoded` — Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
- `hour_posted` — 0 to 23
- `content_type` — mapped to number
- `caption_length` — character count
- `hashtag_count` — number of hashtags
- `has_image` — 1 or 0
- `sentiment_score` — from NLP analysis

**Target Variable:** `engagement_score` — calculated as (likes + comments*2 + shares*3) / impressions * 100

---

## Dataset 3 — NLP Captions Dataset
**File:** `03_nlp_captions_dataset.csv`
**Tasks:** Task 9 (caption generator examples), Task 10 (keyword extractor), Task 11 (hashtag generator)

Contains processed captions with NLP features extracted.

**Key Columns:**
- `extracted_keywords` — list of important words from caption
- `nlp_sentiment` — sentiment score from TextBlob
- `has_question` — 1 if caption ends with question (drives comments)
- `has_cta` — 1 if caption has call-to-action
- `has_emoji` — 1 if emoji present
- `word_count` — number of words

**Insight:** Use the top-performing captions (high engagement) as examples in the Groq LLaMA 3 system prompt.

---

## Dataset 4 — Platform Analytics
**File:** `04_analytics_data.csv`
**Tasks:** Task 28 (analytics fetcher), Task 40 (weekly email report), Task 42 (A/B test evaluation)

This simulates what you get back from Facebook/Instagram API when you fetch post metrics.

**Key Columns:**
- `fetch_date` — when metrics were fetched (24 hours after posting)
- `reach` — unique accounts that saw the post
- `impressions` — total times post was seen
- `saves` — saves count (Instagram only)
- `video_views` — for video/reel posts
- `link_clicks` — clicks on bio link
- `click_through_rate` — link_clicks / impressions

---

## Dataset 5 — Scheduler History
**File:** `05_scheduler_data.csv`
**Tasks:** Task 22-23 (auto scheduler), Task 30 (integration test), Task 31 (full integration)

Simulates the `schedules` database table. Contains both published and pending posts.

**Status Values:**
- `published` — post went live successfully
- `pending` — scheduled for future
- `failed` — publishing failed (use for error handling tests)

**Key Columns:**
- `scheduled_time` — exact date+time of publishing
- `publisher_used` — which publisher module handled it
- `publish_result` — success / api_rate_limit_exceeded / network_error

---

## Dataset 6 — Best Time to Post
**File:** `06_best_time_dataset.csv`
**Tasks:** Task 17 (best time recommender), Task 29 (dashboard charts)

Already aggregated data by platform + day + hour. Use this to populate `best_time.json`.

**How to convert to best_time.json:**
```python
import pandas as pd, json
df = pd.read_csv('data/raw/06_best_time_dataset.csv')
best = df.sort_values('avg_engagement_rate', ascending=False).groupby('platform').first().reset_index()
json.dump(best.to_dict(orient='records'), open('best_time.json','w'), indent=2)
```

---

## Dataset 7 — Trending Keywords
**File:** `07_trends_data.csv`
**Tasks:** Task 12 (trend analyzer), Task 43 (feedback loop), Task 49 (competitor tracker)

Simulates what your `trend_analyzer.py` saves to the MySQL `trends` table every morning.

**Key Columns:**
- `trend_score` — 0 to 100 (higher = more trending)
- `search_volume_index` — relative search popularity
- `source` — RSS_News or RSS+Pytrends
- `is_rising` — 1 if trend is growing, 0 if stable/declining
- `related_hashtags` — hashtags to use with this trend

---

## Dataset 8 — A/B Testing Results
**File:** `08_ab_testing_data.csv`
**Tasks:** Task 41 (A/B testing engine)

Contains 10 completed A/B tests with clear winners and actionable insights.

**Key Columns:**
- `variant` — what was being tested (caption style, CTA type, etc.)
- `caption_a` / `caption_b` — the two versions tested
- `winner` — A or B
- `improvement_percent` — how much better the winner performed
- `insight` — what you learned (use this to update system prompt in Task 43)

**Key Learnings from this data:**
1. Question-based CTAs get 51% more comments than command-based
2. Specific numbers (timeframes, quantities) increase shares by 90%
3. Contrarian/controversial angles get 3x more retweets
4. Embedded polls on Facebook get 10x more comments
5. POV format increases reel reach by 53%

---

## Dataset 9 — Competitor Tracking
**File:** `09_competitor_tracking_data.csv`
**Tasks:** Task 42 (competitor tracker)

Contains real-style competitor data for 10 competing brands across platforms.

**Key Columns:**
- `engagement_rate` — competitor's average engagement (use for alert threshold)
- `posting_frequency_per_week` — how often they post
- `top_content_type` — what content type works best for them
- `follower_gap` — negative means competitor has more followers
- `engagement_gap` — difference between competitor and our engagement rate
- `alert_triggered` — 1 if competitor outperforms our threshold
- `alert_reason` — explanation of why alert was triggered

---

## Dataset 10 — Users & Roles
**File:** `10_users_data.csv`
**Tasks:** Task 45 (role-based authentication)

Contains 15 test users across 3 roles for testing the admin panel.

**Roles:**
- `admin` — can generate, approve, schedule, publish, view analytics
- `editor` — can generate and view, cannot publish
- `viewer` — read-only access to analytics

**Test Credentials (for development only):**
| Username | Role | Password |
|----------|------|---------|
| admin_techcreate | admin | admin123 |
| editor_techcreate | editor | editor123 |
| viewer_techcreate | viewer | viewer123 |

---

## Data Flow Diagram

```
01_social_media_engagement.csv
         ↓ Task 7 (clean_data.py)
   data/cleaned/engagement_clean.csv
         ↓ Task 13 (feature_engineering.py)
02_ml_training_dataset.csv
         ↓ Task 14-16 (train_model.py)
   ml_models/engagement_model.pkl
         ↓ Task 21 (predictor.py)
   POST /api/content/score → predicted engagement score

03_nlp_captions_dataset.csv → Feed top examples to Groq system prompt
04_analytics_data.csv      → analytics_fetcher.py reads and saves to MySQL
05_scheduler_data.csv      → auto_scheduler.py checks due posts
06_best_time_dataset.csv   → converts to best_time.json
07_trends_data.csv         → trend_analyzer.py saves to trends table
08_ab_testing_data.csv     → ab_tester.py learns from winners
09_competitor_tracking_data.csv → competitor_tracker.py sends alerts
10_users_data.csv          → auth.py validates JWT tokens
```
