import os
import sys
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
FRONTEND_DIR = ROOT / "frontend"
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


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8010,http://localhost:8010,http://127.0.0.1:8501,http://localhost:8501",
    )
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://127.0.0.1:8010"]


allowed_origins = _allowed_origins()

app = FastAPI(title="AI Social Media Automation API", version="1.1.0")
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

@app.get("/")
def root():
    return {"message": "AI Social Media Automation API", "docs": "/docs", "frontend": "/app"}

@app.get("/app")
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

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
def api_login(req: LoginRequest):
    return login(req.username, req.password)

@app.post("/api/generate-caption")
def api_caption(req: CaptionRequest):
    return {"captions": generate_caption(req.topic, req.platform, req.tone)}

@app.post("/api/generate-multiple-captions")
def api_multiple_captions(req: MultipleCaptionRequest):
    return {"captions": generate_multiple_captions(req.topic, req.platform, req.count)}

@app.post("/api/hashtags")
def api_hashtags(req: TextRequest):
    return hashtag_strategy(req.text, req.platform)

@app.post("/api/keywords")
def api_keywords(req: TextRequest):
    return keyword_analysis(req.text)

@app.get("/api/trends")
def api_trends(platform: str = "Instagram"):
    return analyze_trends(platform)

@app.get("/api/content-ideas")
def api_ideas(platform: str = "Instagram", niche: str = "AI"):
    return {"ideas": suggest_content_ideas(platform, niche)}

@app.post("/api/moderate")
def api_moderate(req: TextRequest):
    return moderate_text(req.text)

@app.post("/api/plagiarism")
def api_plagiarism(req: TextRequest):
    return check_plagiarism(req.text)

@app.post("/api/translate")
def api_translate(req: TranslateRequest):
    return translate_caption(req.text, req.target_language)

@app.post("/api/image-prompt")
def api_image(req: CaptionRequest):
    return generate_prompt_package(req.topic, req.platform, req.tone)

@app.post("/api/predict-engagement")
def api_predict(req: PredictionRequest):
    return predict_engagement(req.dict())

@app.post("/api/ab-test")
def api_ab(req: ABRequest):
    return compare_two_captions(req.caption_a, req.caption_b, req.platform)

@app.get("/api/ab-history")
def api_ab_history(platform: str = "Instagram"):
    return historical_ab_insights(platform)

@app.get("/api/analytics")
def api_analytics(platform: str = "Instagram"):
    return analytics_summary(platform)

@app.get("/api/competitors")
def api_competitors(platform: str = "Instagram"):
    return competitor_summary(platform)

@app.get("/api/scheduler")
def api_scheduler(platform: str = "Instagram"):
    return scheduler_summary(platform)

@app.get("/api/best-time")
def api_best_time(platform: str = "Instagram", content_type: str = "reel"):
    return recommend_best_time(platform, content_type)

@app.get("/api/integrations")
def api_integrations():
    return integration_status()

@app.post("/api/publish")
def api_publish(req: PublishRequest):
    return publish_post(req.platform, req.caption, req.media_url)

@app.post("/api/telegram")
def api_telegram(req: TelegramRequest):
    return send_telegram(req.message)

@app.get("/api/dataset-overview")
def api_dataset_overview():
    return dataset_overview()

@app.post("/api/content-brief")
def api_content_brief(req: RawToPostRequest):
    return content_brief(req.raw_text, req.platform, req.tone)

@app.post("/api/full-pipeline")
def api_full_pipeline(req: RawToPostRequest):
    caption = generate_caption(req.raw_text, req.platform, req.tone)
    caption_text = caption[0]["caption"] if isinstance(caption, list) else str(caption)
    hashtags = hashtag_strategy(caption_text, req.platform)
    moderation = moderate_text(caption_text)
    plagiarism = check_plagiarism(caption_text)
    prediction = predict_engagement({
        "platform": req.platform,
        "content_type": "reel",
        "day_of_week": "Friday",
        "hour_posted": 19,
        "caption": caption_text,
        "hashtags": " ".join(hashtags.get("recommended_hashtags", [])),
        "sentiment_score": 0.7,
        "has_image": 1,
    })
    schedule = recommend_best_time(req.platform, "reel")
    brief = content_brief(req.raw_text, req.platform, req.tone)
    return {
        "caption": caption,
        "hashtags": hashtags,
        "moderation": moderation,
        "plagiarism": plagiarism,
        "engagement_prediction": prediction,
        "recommended_schedule": schedule,
        "content_brief": brief,
        "note": "Publishing remains dry-run unless POSTING_MODE=live and platform credentials are configured.",
    }
