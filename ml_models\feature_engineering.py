from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ML_DATA = ROOT / "data" / "raw" / "02_ml_training_dataset.csv"
BEST_TIME_DATA = ROOT / "data" / "raw" / "06_best_time_dataset.csv"
OUT = ROOT / "data" / "processed" / "ml_features.csv"
BEST_TIME_JSON = ROOT / "best_time.json"
TARGET_COLUMN = "engagement_score"
FEATURE_COLUMNS = ["platform_encoded", "day_encoded", "hour_posted", "content_type_encoded", "caption_length", "hashtag_count", "has_image", "sentiment_score"]
PLATFORM_MAP = {"instagram": 0, "facebook": 1, "twitter": 2, "x": 2, "linkedin": 3}
DAY_MAP = {"monday":0,"tuesday":1,"wednesday":2,"thursday":3,"friday":4,"saturday":5,"sunday":6}
CONTENT_MAP = {"image":0,"video":1,"text":2,"reel":3,"carousel":4}

def count_hashtags(value):
    return len(re.findall(r"#\w+", str(value or "")))

def engineer_features(df):
    df = df.copy()
    if "platform_encoded" not in df.columns:
        df["platform_encoded"] = df.get("platform", "Instagram").astype(str).str.lower().map(PLATFORM_MAP).fillna(0)
    if "day_encoded" not in df.columns:
        df["day_encoded"] = df.get("day_of_week", "Monday").astype(str).str.lower().map(DAY_MAP).fillna(0)
    if "content_type_encoded" not in df.columns:
        df["content_type_encoded"] = df.get("content_type", "image").astype(str).str.lower().map(CONTENT_MAP).fillna(0)
    if "caption_length" not in df.columns:
        df["caption_length"] = df.get("caption", "").astype(str).str.len()
    if "hashtag_count" not in df.columns:
        if "hashtags" in df.columns:
            df["hashtag_count"] = df["hashtags"].apply(count_hashtags)
        else:
            df["hashtag_count"] = df.get("caption", "").astype(str).apply(count_hashtags)
    for col in ["hour_posted", "has_image", "sentiment_score", "engagement_score"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def get_features_and_target(csv_path=ML_DATA):
    df = pd.read_csv(csv_path)
    df = engineer_features(df)
    return df[FEATURE_COLUMNS], df[TARGET_COLUMN], df

def save_engineered_features(df):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df[FEATURE_COLUMNS + [TARGET_COLUMN]].to_csv(OUT, index=False)
    return OUT

def create_best_time_json():
    if not BEST_TIME_DATA.exists():
        return None
    df = pd.read_csv(BEST_TIME_DATA)
    best = df.sort_values("peak_score", ascending=False).groupby("platform").first().reset_index()
    data = best[["platform", "day_of_week", "hour_posted", "avg_engagement_rate", "best_content_type", "peak_score"]].to_dict(orient="records")
    BEST_TIME_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return BEST_TIME_JSON

if __name__ == "__main__":
    X, y, df = get_features_and_target()
    print("Feature engineering completed")
    print("CSV used:", ML_DATA)
    print("Features:", X.shape, "Target:", y.shape)
    print("Saved:", save_engineered_features(df))
    print("Best time JSON:", create_best_time_json())
