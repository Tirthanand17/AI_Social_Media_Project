from datetime import datetime

from keyword_extractor import keyword_analysis
from content_moderator import moderate_text
from plagiarism_checker import check_plagiarism
from image_generator import generate_prompt_package
from predictor import predict_engagement
from auto_scheduler import recommend_best_time


def _safe(name, fn, fallback=None):
    try:
        return fn()
    except Exception as exc:
        return fallback if fallback is not None else {"status": "error", "step": name, "message": str(exc)}


def _risk_label(score):
    try:
        value = float(score)
    except Exception:
        return "unknown"
    if value >= 75:
        return "strong"
    if value >= 50:
        return "medium"
    return "needs_improvement"


def analyse_content(caption, platform="Instagram", content_type="reel", day_of_week="Friday", hour_posted=19, hashtags="#AI #SocialMedia"):
    best_time = _safe("best_time", lambda: recommend_best_time(platform), None)
    prediction_payload = {
        "platform": platform,
        "content_type": content_type,
        "day_of_week": day_of_week or str((best_time or {}).get("day_of_week", "Friday")),
        "hour_posted": int(hour_posted or (best_time or {}).get("hour_posted", 19)),
        "caption": caption,
        "hashtags": hashtags,
        "sentiment_score": 0.7,
        "has_image": 1,
    }
    prediction = _safe("prediction", lambda: predict_engagement(prediction_payload), {})
    score = prediction.get("predicted_engagement_score") or prediction.get("engagement_score") or prediction.get("score") or 0
    keywords = _safe("keywords", lambda: keyword_analysis(caption), {})
    moderation = _safe("moderation", lambda: moderate_text(caption), {})
    plagiarism = _safe("plagiarism", lambda: check_plagiarism(caption), {})
    prompt_package = _safe("image_prompt", lambda: generate_prompt_package(caption, platform), {})

    recommendations = []
    if float(score or 0) < 50:
        recommendations.append("Improve the opening hook and add a clearer call to action.")
    if len(str(caption).split()) < 12:
        recommendations.append("Add more context so the post feels useful and complete.")
    if "#" not in str(hashtags):
        recommendations.append("Add 3 to 8 relevant hashtags for better discovery.")
    if not recommendations:
        recommendations.append("Content is ready for review. Keep the dry-run publisher enabled before live posting.")

    return {
        "status": "success",
        "analysed_at": datetime.now().isoformat(timespec="seconds"),
        "platform": platform,
        "content_type": content_type,
        "quality_label": _risk_label(score),
        "engagement_prediction": prediction,
        "keyword_analysis": keywords,
        "moderation": moderation,
        "plagiarism": plagiarism,
        "best_time": best_time,
        "image_prompt_package": prompt_package,
        "recommendations": recommendations,
    }
