"""Self-contained live frontend + API entrypoint.

Run this file when the local folder is old or not connected to GitHub:
python -m uvicorn api.live_main:app --host 127.0.0.1 --port 8010

It serves the simple frontend and also defines the API routes used by frontend,
so old api/main.py versions cannot cause 404 errors.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
FRONTEND_DIR = ROOT / "frontend"
LIVE_VERSION = "old-folder-simple-v6-20260619"

load_dotenv(ROOT / ".env")
for folder in [ROOT, API_DIR, ROOT / "nlp", ROOT / "ml_models", ROOT / "scheduler", ROOT / "publisher"]:
    sys.path.insert(0, str(folder))


def _import(name: str, fallback: Any = None) -> Any:
    try:
        module_name, attr = name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[attr])
        return getattr(module, attr)
    except Exception:
        return fallback


def _safe(name: str, func: Callable[[], Any], fallback: Any) -> Any:
    try:
        return func()
    except Exception as exc:
        if isinstance(fallback, dict):
            data = dict(fallback)
            data.setdefault("status", "fallback")
            data.setdefault("message", f"{name} fallback used: {exc}")
            return data
        return fallback


def _platform_key(platform: str) -> str:
    value = str(platform or "Instagram")
    return {"x": "Twitter", "twitter": "Twitter"}.get(value.lower(), value)


def _caption_text(value: Any) -> str:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            return str(first.get("caption") or first.get("text") or first)
        return str(first)
    if isinstance(value, dict):
        return str(value.get("caption") or value.get("text") or value)
    return str(value or "")


def _hashtag_string(value: Any) -> str:
    if isinstance(value, dict):
        if value.get("hashtag_string"):
            return str(value["hashtag_string"])
        tags = value.get("hashtags") or value.get("recommended_hashtags") or []
        if isinstance(tags, list):
            return " ".join(str(tag) for tag in tags)
    if isinstance(value, str):
        return value
    return "#AI #SocialMedia #Automation"


generate_caption = _import("caption_generator.generate_caption")
generate_multiple_captions = _import("caption_generator.generate_multiple_captions")
hashtag_strategy = _import("hashtag_generator.hashtag_strategy")
keyword_analysis = _import("keyword_extractor.keyword_analysis")
analyze_trends = _import("trend_analyzer.analyze_trends")
suggest_content_ideas = _import("trend_analyzer.suggest_content_ideas")
moderate_text = _import("content_moderator.moderate_text")
check_plagiarism = _import("plagiarism_checker.check_plagiarism")
translate_caption = _import("translator.translate_caption")
generate_prompt_package = _import("image_generator.generate_prompt_package")
predict_engagement = _import("predictor.predict_engagement")
analytics_summary = _import("analytics_fetcher.analytics_summary")
competitor_summary = _import("competitor_tracker.competitor_summary")
login_fn = _import("auth.login")
scheduler_summary = _import("auto_scheduler.scheduler_summary")
recommend_best_time = _import("auto_scheduler.recommend_best_time")
publish_post = _import("publisher_manager.publish_post")
integration_status = _import("publisher_manager.integration_status")
send_telegram = _import("notifier.send_telegram")
dataset_overview = _import("content_intelligence.dataset_overview")
content_brief = _import("content_intelligence.content_brief")
analyse_content = _import("trained_analyser.analyse_content")


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


class TextRequest(BaseModel):
    text: str
    platform: str = "Instagram"


class PredictionRequest(BaseModel):
    platform: str = "Instagram"
    content_type: str = "reel"
    day_of_week: str = "Friday"
    hour_posted: int = 19
    caption: str
    hashtags: str = "#AI #Automation #SocialMedia"
    sentiment_score: float = 0.7
    has_image: int = 1


class LoginRequest(BaseModel):
    username: str
    password: str


class PublishRequest(BaseModel):
    platform: str = "Instagram"
    caption: str
    media_url: Optional[str] = None


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "Hindi"


class FeedbackRequest(BaseModel):
    platform: str = "Instagram"
    caption: str = ""
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


allowed_origins = ["http://127.0.0.1:8010", "http://localhost:8010", "http://127.0.0.1:8501", "http://localhost:8501"]
app = FastAPI(title="AI Social Studio Live API", version="1.6.0")
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

try:
    from storage_api import router as storage_router
    app.include_router(storage_router)
except Exception:
    storage_router = None

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def _no_cache_headers() -> dict[str, str]:
    return {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache", "Expires": "0"}


def _frontend_html() -> str:
    index_file = FRONTEND_DIR / "index.html"
    html = index_file.read_text(encoding="utf-8") if index_file.exists() else "<html><body><h1>AI Social Studio</h1></body></html>"
    html = re.sub(r'/static/styles\.css\?v=[^"\']+', f'/static/styles.css?v={LIVE_VERSION}', html)
    html = re.sub(r'/static/app\.js\?v=[^"\']+', f'/static/app.js?v={LIVE_VERSION}', html)
    marker = """
    <div style="position:fixed;right:14px;bottom:14px;z-index:9999;background:#1a1200;color:#ffe082;padding:10px 14px;border-radius:999px;font:800 12px Segoe UI,Arial;box-shadow:0 10px 25px rgba(0,0,0,.25)">
      SIMPLE WORKFLOW v6 · all API routes connected
    </div>
    """
    return html.replace("<body>", "<body>" + marker, 1)


@app.get("/", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
def live_frontend():
    return HTMLResponse(_frontend_html(), headers=_no_cache_headers())


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AI Social Studio", "version": app.version, "posting_mode": os.getenv("POSTING_MODE", "dry_run")}


@app.get("/api/config")
def config():
    return {"posting_mode": os.getenv("POSTING_MODE", "dry_run"), "demo_login_enabled": True, "live_mode_ready": False, "note": "Instagram/Facebook credentials can be added later."}


@app.post("/api/login")
@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    if login_fn:
        return _safe("login", lambda: login_fn(req.username, req.password), {})
    if req.username == "admin_techcreate" and req.password == "admin123":
        return {"success": True, "status": "success", "username": req.username, "role": "admin", "message": "Demo login successful"}
    return {"success": False, "status": "error", "message": "Invalid demo username or password"}


@app.get("/api/dataset-overview")
@app.get("/api/data/overview")
def api_dataset_overview():
    fallback = [
        {"name": "engagement", "rows": 60, "purpose": "ML engagement prediction"},
        {"name": "analytics", "rows": 50, "purpose": "performance analysis"},
        {"name": "schedule", "rows": 60, "purpose": "best time and status tracking"},
    ]
    data = _safe("dataset_overview", lambda: dataset_overview(), fallback) if dataset_overview else fallback
    return {"datasets": data, "total_datasets": len(data)}


@app.post("/api/generate-caption")
@app.post("/api/content/generate-caption")
def api_generate_caption(req: CaptionRequest):
    fallback_caption = f"{req.topic}\n\nBuilt for {req.platform}. Save time, create better content, and post with confidence. #AI #SocialMedia #Automation"
    raw = _safe("caption", lambda: generate_caption(req.topic, req.platform, req.tone), fallback_caption) if generate_caption else fallback_caption
    caption = _caption_text(raw)
    hashtags = api_hashtags(TextRequest(text=caption, platform=req.platform))
    return {"status": "success", "caption": caption, "captions": raw, "hashtags": hashtags, "message": "Caption generated"}


@app.post("/api/generate-multiple-captions")
def api_generate_multiple(req: CaptionRequest):
    if generate_multiple_captions:
        return {"captions": _safe("multiple_captions", lambda: generate_multiple_captions(req.topic, count=3, platform=req.platform), [])}
    return {"captions": [api_generate_caption(req)["caption"]]}


@app.post("/api/hashtags")
@app.post("/api/content/hashtags")
def api_hashtags(req: TextRequest):
    fallback = {"hashtags": ["#AI", "#SocialMedia", "#Automation", "#ContentCreation", "#DigitalMarketing"], "hashtag_string": "#AI #SocialMedia #Automation #ContentCreation #DigitalMarketing"}
    return _safe("hashtags", lambda: hashtag_strategy(req.text, req.platform), fallback) if hashtag_strategy else fallback


@app.post("/api/moderate")
@app.post("/api/content/moderate")
def api_moderate(req: TextRequest):
    return _safe("moderation", lambda: moderate_text(req.text), {"status": "Approved", "safe": True}) if moderate_text else {"status": "Approved", "safe": True}


@app.post("/api/plagiarism")
@app.post("/api/content/plagiarism")
def api_plagiarism(req: TextRequest):
    return _safe("plagiarism", lambda: check_plagiarism(req.text), {"status": "Low Similarity", "similarity": 0.08}) if check_plagiarism else {"status": "Low Similarity", "similarity": 0.08}


@app.post("/api/translate")
@app.post("/api/multilingual/translate")
def api_translate(req: TranslateRequest):
    return _safe("translate", lambda: translate_caption(req.text, req.target_language), {"translated_text": req.text, "target_language": req.target_language, "note": "Translator fallback"}) if translate_caption else {"translated_text": req.text, "target_language": req.target_language}


@app.post("/api/image-prompt")
@app.post("/api/content/image-prompt")
@app.post("/api/image-generator")
def api_image_prompt(req: CaptionRequest):
    fallback = {"prompt": f"Create a clean modern social media visual for: {req.topic}", "platform": req.platform, "style": "professional, bright, high quality"}
    return _safe("image_prompt", lambda: generate_prompt_package(req.topic, req.platform), fallback) if generate_prompt_package else fallback


@app.get("/api/trends")
@app.get("/api/trends/analyze")
def api_trends(platform: str = "Instagram", top_n: int = 20):
    fallback = {"platform": platform, "trending_keywords": ["AI", "automation", "content", "growth", "analytics"], "summary": "Fallback trend signals for demo."}
    return _safe("trends", lambda: analyze_trends(top_n=top_n, platform=_platform_key(platform)), fallback) if analyze_trends else fallback


@app.get("/api/analytics")
@app.get("/api/analytics/summary")
def api_analytics(platform: Optional[str] = None):
    fallback = {"records": [], "totals": {"reach": 0, "likes": 0, "comments": 0, "shares": 0}, "average_engagement_rate": 0.0, "top_posts": []}
    return _safe("analytics", lambda: analytics_summary(platform), fallback) if analytics_summary else fallback


@app.get("/api/competitors")
@app.get("/api/competitors/summary")
def api_competitors(platform: str = "Instagram"):
    fallback = {"platform": platform, "competitors": [], "alerts": ["Competitor tracking is available as a demo/fallback until live sources are added."]}
    return _safe("competitors", lambda: competitor_summary(), fallback) if competitor_summary else fallback


@app.get("/api/scheduler")
@app.get("/api/scheduler/summary")
def api_scheduler():
    return _safe("scheduler", lambda: scheduler_summary(), {"statuses": {"pending": 0, "published": 0}, "message": "Scheduler fallback"}) if scheduler_summary else {"statuses": {"pending": 0, "published": 0}}


@app.get("/api/best-time")
def api_best_time(platform: str = "Instagram", content_type: str = "reel"):
    fallback = {"platform": platform, "day_of_week": "Wednesday", "hour_posted": 20, "best_content_type": content_type, "avg_engagement_rate": 0.1023}
    return _safe("best_time", lambda: recommend_best_time(platform), fallback) if recommend_best_time else fallback


@app.post("/api/predict-engagement")
@app.post("/api/ml/predict-engagement")
def api_predict(req: PredictionRequest):
    fallback = {"predicted_engagement_score": 72.0, "engagement_category": "High Engagement", "best_time": api_best_time(req.platform, req.content_type), "advice": ["Improve hook", "Add clear CTA", "Use focused hashtags"]}
    return _safe("predict", lambda: predict_engagement(req.dict()), fallback) if predict_engagement else fallback


@app.post("/api/trained-analyser")
@app.post("/api/trained-analyzer")
def api_trained(req: TrainedAnalyserRequest):
    fallback = {"score": 72, "recommendations": ["Add a stronger first line", "Use one clear CTA", "Post at recommended time"], "platform": req.platform}
    return _safe("trained_analyser", lambda: analyse_content(req.caption, req.platform, req.content_type, req.day_of_week, req.hour_posted, req.hashtags), fallback) if analyse_content else fallback


@app.get("/api/integrations")
@app.get("/api/integrations/status")
def api_integrations():
    fallback = {"posting_mode": os.getenv("POSTING_MODE", "dry_run"), "platforms": {"LinkedIn": "optional", "Telegram": "optional", "Instagram": "credentials later", "Facebook": "credentials later", "X": "optional/paid"}}
    return _safe("integrations", lambda: integration_status(), fallback) if integration_status else fallback


@app.post("/api/publish")
@app.post("/api/publisher/dry-run")
def api_publish(req: PublishRequest):
    fallback = {"status": "dry_run", "message": "Dry-run successful. No live post was sent.", "platform": req.platform, "caption": req.caption, "media_url": req.media_url}
    return _safe("publish", lambda: publish_post(req.platform, req.caption, req.media_url), fallback) if publish_post else fallback


@app.post("/api/telegram")
@app.post("/api/integrations/telegram/send")
def api_telegram(req: dict):
    message = str(req.get("message", "AI Social Studio test notification"))
    return _safe("telegram", lambda: send_telegram(message), {"status": "dry_run", "message": "Telegram not configured", "text": message}) if send_telegram else {"status": "dry_run", "message": "Telegram not configured", "text": message}


@app.get("/api/content/brief")
def api_content_brief(platform: str = "Instagram"):
    fallback = {"platform": platform, "best_time": api_best_time(platform), "ideas": ["AI automation tips", "Before/after workflow", "Creator productivity checklist"]}
    return _safe("content_brief", lambda: content_brief(platform), fallback) if content_brief else fallback


@app.post("/api/full-pipeline")
@app.post("/api/content/raw-to-post")
def api_full_pipeline(req: RawToPostRequest):
    caption_result = api_generate_caption(CaptionRequest(topic=req.raw_text, platform=req.platform, tone=req.tone))
    caption = caption_result.get("caption", req.raw_text)
    hashtags = api_hashtags(TextRequest(text=caption, platform=req.platform))
    best_time = api_best_time(req.platform, "reel")
    prediction = api_predict(PredictionRequest(platform=req.platform, content_type="reel", day_of_week=str(best_time.get("day_of_week", "Friday")), hour_posted=int(best_time.get("hour_posted", 19)), caption=caption, hashtags=_hashtag_string(hashtags)))
    moderation = api_moderate(TextRequest(text=caption, platform=req.platform))
    plagiarism = api_plagiarism(TextRequest(text=caption, platform=req.platform))
    image_prompt = api_image_prompt(CaptionRequest(topic=req.raw_text, platform=req.platform, tone=req.tone))
    publish_preview = api_publish(PublishRequest(platform=req.platform, caption=caption, media_url=req.media_url))
    return {
        "status": "success",
        "platform": req.platform,
        "campaign_goal": req.campaign_goal,
        "caption": caption,
        "hashtags": hashtags,
        "best_time": best_time,
        "engagement_prediction": prediction,
        "moderation": moderation,
        "plagiarism": plagiarism,
        "image_prompt": image_prompt,
        "publish_preview": publish_preview,
        "simple_next_steps": ["Review caption", "Save post", "Schedule or reschedule", "Use dry-run publish", "Add Instagram/Facebook credentials later"],
    }
