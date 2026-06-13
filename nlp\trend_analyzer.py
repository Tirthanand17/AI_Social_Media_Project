from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TREND_DATA = ROOT / "data" / "raw" / "07_trends_data.csv"
OUT = ROOT / "data" / "processed" / "trend_report.csv"

def get_trend_category(score):
    if score >= 80:
        return "Very High Trend"
    if score >= 60:
        return "High Trend"
    if score >= 40:
        return "Medium Trend"
    if score >= 20:
        return "Low Trend"
    return "Very Low Trend"

def analyze_trends(top_n=20, platform=None):
    if not TREND_DATA.exists():
        return {"status": "failed", "message": "07_trends_data.csv not found"}
    df = pd.read_csv(TREND_DATA)
    if platform:
        df = df[df["platform"].str.lower() == platform.lower()]
    df = df.sort_values(["is_rising", "trend_score", "search_volume_index"], ascending=False).head(top_n)
    keywords = []
    hashtags = []
    for _, row in df.iterrows():
        keywords.append({
            "keyword": row["keyword"],
            "category": row.get("category", "General"),
            "platform": row.get("platform", "All"),
            "trend_score": int(row.get("trend_score", 0)),
            "search_volume_index": int(row.get("search_volume_index", 0)),
            "is_rising": int(row.get("is_rising", 0)),
            "trend_category": get_trend_category(int(row.get("trend_score", 0))),
        })
        for tag in str(row.get("related_hashtags", "")).split():
            if tag.startswith("#"):
                hashtags.append(tag)
    return {
        "status": "success",
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_file": str(TREND_DATA.name),
        "trending_keywords": keywords,
        "trending_hashtags": list(dict.fromkeys(hashtags))[:top_n],
    }

def suggest_content_ideas(trending_keywords, limit=5):
    ideas = []
    for item in trending_keywords[:limit]:
        keyword = item["keyword"]
        ideas.append({
            "keyword": keyword,
            "idea": f"Create a reel/carousel explaining how {keyword} helps creators or businesses grow.",
            "caption_angle": f"Why {keyword} is trending and how to use it today.",
            "recommended_format": "reel/carousel",
        })
    return ideas

def save_trend_report(result):
    if result.get("status") != "success":
        return None
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in result["trending_keywords"]:
        rows.append(item)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    return OUT

if __name__ == "__main__":
    res = analyze_trends(20)
    print(res)
    print("Ideas:", suggest_content_ideas(res.get("trending_keywords", [])))
    print("Saved:", save_trend_report(res))
