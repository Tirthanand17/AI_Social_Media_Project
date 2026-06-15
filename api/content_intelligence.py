from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def _read_csv(name):
    path = RAW / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _records(df):
    return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")


def _platform_key(platform):
    value = str(platform or "Instagram").strip()
    return {"x": "twitter"}.get(value.lower(), value.lower())


def dataset_overview():
    datasets = []
    for path in sorted(RAW.glob("*.csv")):
        try:
            df = pd.read_csv(path)
            datasets.append({"file": path.name, "rows": int(len(df)), "columns": list(df.columns)})
        except Exception as exc:
            datasets.append({"file": path.name, "rows": 0, "error": str(exc)})
    return datasets


def content_brief(platform="Instagram"):
    platform_key = _platform_key(platform)
    analytics = _read_csv("04_analytics_data.csv")
    trends = _read_csv("07_trends_data.csv")
    best_time = _read_csv("06_best_time_dataset.csv")
    captions = _read_csv("03_nlp_captions_dataset.csv")

    if not analytics.empty and "platform" in analytics.columns:
        analytics = analytics[analytics["platform"].astype(str).str.lower() == platform_key]
    if not trends.empty and "platform" in trends.columns:
        platform_trends = trends[trends["platform"].astype(str).str.lower() == platform_key]
        if not platform_trends.empty:
            trends = platform_trends
    if not best_time.empty and "platform" in best_time.columns:
        best_time = best_time[best_time["platform"].astype(str).str.lower() == platform_key]
    if not captions.empty and "platform" in captions.columns:
        platform_captions = captions[captions["platform"].astype(str).str.lower() == platform_key]
        if not platform_captions.empty:
            captions = platform_captions

    top_posts = []
    if not analytics.empty and "engagement_rate" in analytics.columns:
        top_posts = _records(analytics.sort_values("engagement_rate", ascending=False).head(3))

    top_trends = []
    if not trends.empty and "trend_score" in trends.columns:
        top_trends = trends.sort_values("trend_score", ascending=False).head(5)["keyword"].dropna().astype(str).tolist()

    best = None
    if not best_time.empty and "peak_score" in best_time.columns:
        best = _records(best_time.sort_values("peak_score", ascending=False).head(1))
        best = best[0] if best else None

    examples = []
    if not captions.empty and "caption" in captions.columns:
        examples = captions["caption"].dropna().astype(str).head(3).tolist()

    topic_seed = ", ".join(top_trends[:3]) if top_trends else f"{platform} content growth"
    return {
        "platform": platform,
        "topic_seed": topic_seed,
        "recommended_topic": f"{topic_seed} for audience growth",
        "best_time": best,
        "top_trends": top_trends,
        "top_posts": top_posts,
        "caption_examples": examples,
        "dataset_overview": dataset_overview(),
    }
