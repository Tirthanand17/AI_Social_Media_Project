# AI Social Media Automation — Corrected Free Prototype Workflow

## Dataset mapping used
1. `01_social_media_engagement.csv` → `data/clean_data.py`
2. `02_ml_training_dataset.csv` → feature engineering + model training
3. `03_nlp_captions_dataset.csv` → caption examples, keywords, hashtags
4. `04_analytics_data.csv` → analytics API + dashboard
5. `05_scheduler_data.csv` → scheduler dry-run testing
6. `06_best_time_dataset.csv` → best posting time recommender + `best_time.json`
7. `07_trends_data.csv` → trend analyzer + hashtag generator
8. `08_ab_testing_data.csv` → A/B test insights + caption scoring
9. `09_competitor_tracking_data.csv` → competitor tracker
10. `10_users_data.csv` → role-based demo auth

## Run order
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python data/clean_data.py
python ml_models/feature_engineering.py
python ml_models/train_model.py
python RUN_TESTS.py
uvicorn api.main:app --reload
streamlit run dashboard/dashboard.py
```

## Gemini free prototype
Keep `USE_GEMINI=false` first. After getting a Gemini API key, set:
```env
USE_GEMINI=true
GEMINI_API_KEY=your_key_here
```
If Gemini limit finishes or key is missing, the project automatically uses local fallback logic.

## Live posting
Current publisher is `dry_run` only. Actual Instagram/LinkedIn posting needs company-approved API credentials and permissions.
