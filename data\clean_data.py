from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "01_social_media_engagement.csv"
OUT = ROOT / "data" / "cleaned" / "engagement_clean.csv"

NUMERIC_DEFAULTS = {
    "hour_posted": 12,
    "likes_count": 0,
    "shares_count": 0,
    "comments_count": 0,
    "impressions": 0,
    "engagement_rate": 0.0,
    "sentiment_score": 0.0,
    "has_image": 0,
    "caption_length": 0,
    "hashtag_count": 0,
    "is_weekend": 0,
    "is_holiday": 0,
    "month": 0,
    "year": 0,
    "engagement_score": 0.0,
}

def clean_social_media_data(input_file=RAW, output_file=OUT):
    df = pd.read_csv(input_file)
    df = df.drop_duplicates()
    for col in ["caption", "hashtags", "platform", "content_type", "day_of_week"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    for col, default in NUMERIC_DEFAULTS.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(default)
    if "caption" in df.columns:
        df["caption_length"] = df["caption"].astype(str).str.len()
    if "hashtags" in df.columns:
        df["hashtag_count"] = df["hashtags"].astype(str).str.count("#")
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)
    return df, output_file

if __name__ == "__main__":
    df, out = clean_social_media_data()
    print("Data cleaning completed")
    print("Rows:", len(df))
    print("Saved:", out)
