from pathlib import Path
import time

import pandas as pd
import schedule

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "data" / "raw" / "08_ab_testing_data.csv"
TREND = ROOT / "data" / "raw" / "07_trends_data.csv"
SYSTEM_PROMPT = ROOT / "nlp" / "system_prompt.txt"
AUTO_MARKER = "\n\n# --- AUTO-LEARNED WEEKLY GUIDANCE ---\n"


def build_prompt_improvements():
    insights = []
    if AB.exists():
        df = pd.read_csv(AB)
        insights.extend(df.get("insight", pd.Series(dtype=str)).dropna().astype(str).head(5).tolist())
    trends = []
    if TREND.exists():
        df = pd.read_csv(TREND).sort_values("trend_score", ascending=False)
        trends = df.get("keyword", pd.Series(dtype=str)).dropna().astype(str).head(5).tolist()
    return {
        "ab_testing_insights": insights,
        "top_trends": trends,
        "recommendation": "Use clear value, natural calls to action, and relevant trends without making unsupported claims.",
    }


def update_system_prompt():
    """Refresh only the generated section of the caption system prompt."""
    improvements = build_prompt_improvements()
    existing = SYSTEM_PROMPT.read_text(encoding="utf-8") if SYSTEM_PROMPT.exists() else "You are an expert social media copywriter.\n"
    base = existing.split(AUTO_MARKER, 1)[0].rstrip()

    insight_lines = "\n".join(f"- {item}" for item in improvements["ab_testing_insights"]) or "- No new A/B insights available."
    trend_lines = ", ".join(improvements["top_trends"]) or "No trend dataset available"
    adaptive = (
        AUTO_MARKER
        + "Use these repository-backed observations as guidance, not guaranteed facts:\n"
        + insight_lines
        + f"\nCurrent dataset trend keywords: {trend_lines}\n"
        + f"General guidance: {improvements['recommendation']}\n"
    )
    SYSTEM_PROMPT.write_text(base + adaptive, encoding="utf-8")
    return {"status": "updated", "file": str(SYSTEM_PROMPT), **improvements}


def configure_feedback_schedule():
    schedule.every().sunday.at("23:00").do(update_system_prompt)
    return {"status": "scheduled", "day": "sunday", "time": "23:00"}


def run_feedback_loop():
    configure_feedback_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    print(build_prompt_improvements())
