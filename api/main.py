import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
FRONTEND_DIR = ROOT / "frontend"
FEEDBACK_FILE = ROOT / "data" / "processed" / "feedback_loop.csv"

for p in [ROOT, ROOT / "nlp", ROOT / "ml_models", ROOT / "api", ROOT / "scheduler", ROOT / "publisher"]:
    sys.path.append(str(p))

from caption_generator import generate_caption, generate_multiple_captions
from hashtag_generator import hashtag_strategy
from keyword_extractor import keyword_analysis
from trend_analyzer import analyze_trends, suggest_content_ideas
from content_moderator import moderate_text
from plagiarism_checker import check_plagiarism
from translator import translate_caption
from image_generator import generate_prompt_package
from predictor import predict_engagement
from ab_tester import compare_two_captions, historical_ab_insights
from analytics_fetcher import analytics_summary
from competitor_tracker import competitor_summary
from auth import login
from auto_scheduler import scheduler_summary, recommend_best_time
from publisher_manager import publish_post, integration_status
from notifier import send_telegram
from content_intelligence import content_brief, dataset_overview
from feedback_loop import build_prompt_improvements
from trained_analyser import analyse_content


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8010,http://localhost:8010,http://127.0.0.1:8501,http://localhost:8501",
    )
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://127.0.0.1:8010"]


def _platform_key(platform: str) -> str:
    return {"x": "Twitter", "twitter": "Twitter"}.get(str(platform or "Instagram").lower(), platform)


def _caption_text(caption_response) -> str:
    if isinstance(caption_response, list) and caption_response:
        first = caption_response[0]
        if isinstance(first, dict):
            return str(first.get("caption") or first.get("text") or first)
        return str(first)
    if isinstance(caption_response, dict):
        return str(caption_response.get("caption") or caption_response.get("text") or caption_response)
    return str(caption_response)


def _hashtag_string(hashtags) -> str:
    if not isinstance(hashtags, dict):
        return "#AI #SocialMedia"
    if hashtags.get("hashtag_string"):
        return str(hashtags["hashtag_string"])
    tag_list = hashtags.get("hashtags") or hashtags.get("recommended_hashtags") or []
    return " ".join(tag_list) if tag_list else "#AI #SocialMedia"


def _safe_step(name, func, fallback=None):
    try:
        return func()
    except Exception as exc:
        return fallback if fallback is not None else {"status": "error", "step": name, "message": str(exc)}


def _read_feedback_rows():
    if not FEEDBACK_FILE.exists():
        return []
    with FEEDBACK_FILE.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _save_feedback_record(platform, caption, rating, notes="", actual_engagement=None):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = _read_feedback_rows()
    fieldnames = ["feedback_id", "created_at", "platform", "caption", "rating", "actual_engagement", "notes"]
    row = {
        "feedback_id": f"fb{len(rows) + 1:04d}",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "platform": platform,
        "caption": str(caption)[:1000],
        "rating": str(max(1, min(5, int(rating)))),
        "actual_engagement": "" if actual_engagement is None else str(actual_engagement),
        "notes": notes,
    }
    rows.append(row)
    with FEEDBACK_FILE.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return {"status": "saved", "feedback": row, "total_feedback": len(rows)}


def _feedback_summary():
    rows = _read_feedback_rows()
    ratings = []
    for row in rows:
        try:
            ratings.append(float(row.get("rating", 0)))
        except Exception:
            pass
    avg = round(sum(ratings) / len(ratings), 2) if ratings else None
    by_platform = {}
    for row in rows:
        platform = row.get("platform") or "Unknown"
        by_platform.setdefault(platform, []).append(float(row.get("rating") or 0))
    by_platform_avg = {platform: round(sum(values) / len(values), 2) for platform, values in by_platform.items() if values}
    return {
        "total_feedback": len(rows),
        "average_rating": avg,
        "by_platform": by_platform_avg,
        "recent_feedback": rows[-8:],
        "prompt_improvements": _safe_step("prompt_improvements", build_prompt_improvements, {}),
    }


allowed_origins = _allowed_origins()

app = FastAPI(title="AI Social Media Automation API", version="1.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allowed_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class CaptionRequest(BaseModel):
    topic: str
    platform: str = "Instagram"
    tone: str = "engaging"


class RawToPostRequest(BaseModel):
    raw_text: str
    platform: str = "Instagram"
    tone: str = "professional"
    campaign_goal: str = "Grow engagement"
    media_url: Optional[str] = None


class MultipleCaptionRequest(BaseModel):
    topic: str
    platform: str = "Instagram"
    count: int = 3


class TextRequest(BaseModel):
    text: str
    platform: str = "Instagram"


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "Hindi"


class PredictionRequest(BaseModel):
    platform: str = "Instagram"
    content_type: str = "reel"
    day_of_week: str = "Friday"
    hour_posted: int = 19
    caption: str
    hashtags: str = "#AI #Automation #SocialMedia"
    sentiment_score: float = 0.7
    has_image: int = 1


class ABRequest(BaseModel):
    caption_a: str
    caption_b: str
    platform: str = "Instagram"


class PublishRequest(BaseModel):
    platform: str
    caption: str
    media_url: Optional[str] = None


class TelegramRequest(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class FeedbackRequest(BaseModel):
    platform: str = "Instagram"
    caption: str
    rating: int = 5
    notes: str = ""
    actual_engagement: Optional[float] = None


class TrainedAnalyserRequest(BaseModel):
    caption: str
    platform: str = "Instagram"
    content_type: str = "reel"
    day_of_week: str = "Friday"
    hour_posted: int = 19
    hashtags: str = "#AI #SocialMedia"


@app.get("/")
def root():
    return {"message": "AI Social Media Automation API", "docs": "/docs", "frontend": "/app"}


@app.get("/app")
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "AI Social Media Automation",
        "version": app.version,
        "posting_mode": os.getenv("POSTING_MODE", "dry_run"),
    }


@app.get("/api/config")
def public_config():
    return {
        "posting_mode": os.getenv("POSTING_MODE", "dry_run"),
        "demo_login_enabled": os.getenv("DEMO_LOGIN_ENABLED", "true").lower() in {"1", "true", "yes", "on"},
        "allowed_origins": allowed_origins,
    }


@app.post("/api/login")
@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    return login(req.username, req.password)


@app.get("/api/dataset-overview")
@app.get("/api/data/overview")
def api_dataset_overview():
    datasets = dataset_overview()
    return {"datasets": datasets, "total_datasets": len(datasets)}


@app.post("/api/generate-caption")
@app.post("/api/content/generate-caption")
def api_caption(req: CaptionRequest):
    captions = generate_caption(req.topic, req.platform, req.tone)
    return {"caption": _caption_text(captions), "captions": captions}


@app.post("/api/generate-multiple-captions")
def api_multiple_captions(req: MultipleCaptionRequest):
    captions = generate_multiple_captions(req.topic, count=req.count, platform=req.platform)
    return {"captions": captions}


@app.post("/api/hashtags")
@app.post("/api/content/hashtags")
def api_hashtags(req: TextRequest):
    return hashtag_strategy(req.text, req.platform)


@app.post("/api/keywords")
@app.post("/api/content/keywords")
def api_keywords(req: TextRequest):
    return keyword_analysis(req.text)


@app.get("/api/trends")
@app.get("/api/trends/analyze")
def api_trends(platform: str = "Instagram", top_n: int = 20):
    return analyze_trends(top_n=top_n, platform=_platform_key(platform))


@app.get("/api/content-ideas")
def api_ideas(platform: str = "Instagram", limit: int = 5):
    trend_result = analyze_trends(top_n=20, platform=_platform_key(platform))
    return {"ideas": suggest_content_ideas(trend_result.get("trending_keywords", []), limit=limit)}


@app.post("/api/moderate")
@app.post("/api/content/moderate")
def api_moderate(req: TextRequest):
    return moderate_text(req.text)


@app.post("/api/plagiarism")
@app.post("/api/content/plagiarism")
def api_plagiarism(req: TextRequest):
    return check_plagiarism(req.text)


@app.post("/api/translate")
@app.post("/api/multilingual/translate")
def api_translate(req: TranslateRequest):
    return translate_caption(req.text, req.target_language)


@app.post("/api/image-prompt")
@app.post("/api/content/image-prompt")
@app.post("/api/image-generator")
def api_image(req: CaptionRequest):
    return generate_prompt_package(req.topic, req.platform)


@app.post("/api/predict-engagement")
@app.post("/api/ml/predict-engagement")
def api_predict(req: PredictionRequest):
    return predict_engagement(req.dict())


@app.post("/api/trained-analyser")
@app.post("/api/trained-analyzer")
def api_trained_analyser(req: TrainedAnalyserRequest):
    return analyse_content(req.caption, req.platform, req.content_type, req.day_of_week, req.hour_posted, req.hashtags)


@app.post("/api/ab-test")
def api_ab(req: ABRequest):
    return compare_two_captions(req.caption_a, req.caption_b, req.platform)


@app.get("/api/ab-history")
def api_ab_history(platform: str = "Instagram"):
    return historical_ab_insights(platform)


@app.get("/api/analytics")
@app.get("/api/analytics/summary")
def api_analytics(platform: Optional[str] = None):
    return analytics_summary(platform)


@app.get("/api/competitors")
@app.get("/api/competitors/summary")
def api_competitors(platform: str = "Instagram"):
    return competitor_summary()


@app.get("/api/scheduler")
@app.get("/api/scheduler/summary")
def api_scheduler():
    return scheduler_summary()


@app.get("/api/best-time")
def api_best_time(platform: str = "Instagram", content_type: str = "reel"):
    return recommend_best_time(platform)


@app.get("/api/integrations")
@app.get("/api/integrations/status")
def api_integrations():
    return integration_status()


@app.post("/api/publish")
@app.post("/api/publisher/dry-run")
def api_publish(req: PublishRequest):
    return publish_post(req.platform, req.caption, req.media_url)


@app.post("/api/telegram")
@app.post("/api/integrations/telegram/send")
def api_telegram(req: TelegramRequest):
    return send_telegram(req.message)


@app.get("/api/content/brief")
def api_content_brief_get(platform: str = "Instagram"):
    return content_brief(platform)


@app.post("/api/content-brief")
def api_content_brief_post(req: RawToPostRequest):
    return content_brief(req.platform)


@app.post("/api/feedback")
@app.post("/api/feedback-loop")
def api_feedback(req: FeedbackRequest):
    return _save_feedback_record(req.platform, req.caption, req.rating, req.notes, req.actual_engagement)


@app.get("/api/feedback")
@app.get("/api/feedback-loop")
def api_feedback_summary():
    return _feedback_summary()


def build_post_package(req: RawToPostRequest):
    captions = _safe_step("caption", lambda: generate_caption(req.raw_text, req.platform, req.tone), "")
    caption_text = _caption_text(captions) if captions else req.raw_text
    hashtags = _safe_step("hashtags", lambda: hashtag_strategy(caption_text, req.platform), {"hashtag_string": "#AI #SocialMedia", "hashtags": ["#AI", "#SocialMedia"]})
    moderation = _safe_step("moderation", lambda: moderate_text(caption_text))
    plagiarism = _safe_step("plagiarism", lambda: check_plagiarism(caption_text))
    image_prompt = _safe_step("image_prompt", lambda: generate_prompt_package(req.raw_text, req.platform))
    best_time = _safe_step("best_time", lambda: recommend_best_time(req.platform), None)
    prediction = _safe_step("engagement_prediction", lambda: predict_engagement({
        "platform": req.platform,
        "content_type": "reel",
        "day_of_week": str((best_time or {}).get("day_of_week", "Friday")),
        "hour_posted": int((best_time or {}).get("hour_posted", 19)),
        "caption": caption_text,
        "hashtags": _hashtag_string(hashtags),
        "sentiment_score": 0.7,
        "has_image": 1,
    }))
    publish_preview = _safe_step("publish_preview", lambda: publish_post(req.platform, caption_text, req.media_url))
    translated = _safe_step("multilingual", lambda: translate_caption(caption_text, "Hindi"))
    analyser = _safe_step("trained_analyser", lambda: analyse_content(caption_text, req.platform, "reel", str((best_time or {}).get("day_of_week", "Friday")), int((best_time or {}).get("hour_posted", 19)), _hashtag_string(hashtags)))
    return {
        "platform": req.platform,
        "campaign_goal": req.campaign_goal,
        "caption": caption_text,
        "captions": captions,
        "hashtags": hashtags,
        "moderation": moderation,
        "plagiarism": plagiarism,
        "image_prompt": image_prompt,
        "engagement_prediction": prediction,
        "best_time": best_time,
        "multilingual_preview": translated,
        "trained_analyser": analyser,
        "content_brief": _safe_step("content_brief", lambda: content_brief(req.platform)),
        "publish_preview": publish_preview,
        "note": "Publishing remains dry-run unless POSTING_MODE=live and platform credentials are configured.",
    }


@app.post("/api/full-pipeline")
@app.post("/api/content/raw-to-post")
def api_full_pipeline(req: RawToPostRequest):
    return build_post_package(req)
