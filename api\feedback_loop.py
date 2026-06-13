from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "data" / "raw" / "08_ab_testing_data.csv"
TREND = ROOT / "data" / "raw" / "07_trends_data.csv"

def build_prompt_improvements():
    insights = []
    if AB.exists():
        df = pd.read_csv(AB)
        insights.extend(df.get("insight", pd.Series(dtype=str)).dropna().astype(str).head(5).tolist())
    trends = []
    if TREND.exists():
        df = pd.read_csv(TREND).sort_values("trend_score", ascending=False)
        trends = df.get("keyword", pd.Series(dtype=str)).dropna().astype(str).head(5).tolist()
    return {"ab_testing_insights": insights, "top_trends": trends, "recommendation": "Use question-based CTAs, clear value proposition, and trending keywords inside captions."}

if __name__ == "__main__":
    print(build_prompt_improvements())
