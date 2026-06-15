from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS = ROOT / "data" / "raw" / "04_analytics_data.csv"

def load_analytics(platform=None):
    df = pd.read_csv(ANALYTICS)
    if platform:
        df = df[df["platform"].str.lower() == platform.lower()]
    return df

def analytics_summary(platform=None):
    df = load_analytics(platform)
    return {
        "records": int(len(df)),
        "platforms": sorted(df["platform"].unique().tolist()),
        "total_likes": int(df["likes"].sum()),
        "total_comments": int(df["comments"].sum()),
        "total_shares": int(df["shares"].sum()),
        "total_reach": int(df["reach"].sum()),
        "avg_engagement_rate": round(float(df["engagement_rate"].mean()), 4),
        "top_posts": df.sort_values("engagement_rate", ascending=False).head(5).to_dict(orient="records"),
    }

if __name__ == "__main__":
    print(analytics_summary())
