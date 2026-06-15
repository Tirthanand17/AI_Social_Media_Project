from pathlib import Path
import json
import joblib
import pandas as pd
from feature_engineering import FEATURE_COLUMNS, engineer_features

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml_models" / "engagement_model.pkl"
FEATURES_PATH = ROOT / "ml_models" / "feature_list.json"
BEST_TIME_JSON = ROOT / "best_time.json"

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model missing. Run: python ml_models/train_model.py")
    model = joblib.load(MODEL_PATH)
    features = json.loads(FEATURES_PATH.read_text(encoding="utf-8")) if FEATURES_PATH.exists() else FEATURE_COLUMNS
    return model, features

def engagement_category(score):
    return "Very High Engagement" if score >= 80 else "High Engagement" if score >= 60 else "Medium Engagement" if score >= 40 else "Low Engagement" if score >= 20 else "Very Low Engagement"

def get_best_time(platform="Instagram"):
    if not BEST_TIME_JSON.exists():
        return None
    data = json.loads(BEST_TIME_JSON.read_text(encoding="utf-8"))
    for row in data:
        if row["platform"].lower() == platform.lower():
            return row
    return data[0] if data else None

def predict_engagement(post_data):
    model, features = load_model()
    df = engineer_features(pd.DataFrame([post_data]))
    pred = float(model.predict(df[features])[0])
    return {"predicted_engagement_score": round(pred, 2), "engagement_category": engagement_category(pred), "best_time": get_best_time(post_data.get("platform", "Instagram")), "features_used": features}

if __name__ == "__main__":
    sample = {"platform":"Instagram", "content_type":"reel", "day_of_week":"Friday", "hour_posted":19, "caption":"AI automation for social media growth", "hashtags":"#AI #Automation", "sentiment_score":0.8, "has_image":1}
    print(predict_engagement(sample))
