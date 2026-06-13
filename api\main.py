import sys
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
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
from publisher_manager import publish_post

app = FastAPI(title="AI Social Media Automation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

class CaptionRequest(BaseModel):
    topic: str
    platform: str = "Instagram"
    tone: str = "engaging"

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
    content_type: str = "reel"
    day_of_week: str = "Friday"
    hour_posted: int = 19

class LoginRequest(BaseModel):
    username: str
    password: str

class PublishRequest(BaseModel):
    platform: str
    caption: str
    media_url: Optional[str] = None

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "AI Social Media Automation",
        "mode": "free prototype with optional Gemini + local fallback",
        "frontend": "/app",
        "docs": "/docs",
    }

@app.get("/app", include_in_schema=False)
def frontend_app():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/api/health")
def health():
    return home()

@app.post("/api/auth/login")
def api_login(req: LoginRequest):
    return login(req.username, req.password)

@app.post("/api/content/generate-caption")
def api_caption(req: CaptionRequest):
    return {"caption": generate_caption(req.topic, req.platform, req.tone)}

@app.post("/api/content/generate-multiple-captions")
def api_multi_caption(req: MultipleCaptionRequest):
    return {"captions": generate_multiple_captions(req.topic, req.count, req.platform)}

@app.post("/api/content/hashtags")
def api_hashtags(req: TextRequest):
    return hashtag_strategy(req.text, req.platform)

@app.post("/api/content/keywords")
def api_keywords(req: TextRequest):
    return keyword_analysis(req.text)

@app.get("/api/trends/analyze")
def api_trends(platform: Optional[str] = None):
    res = analyze_trends(20, platform)
    if res.get("status") == "success":
        res["content_ideas"] = suggest_content_ideas(res["trending_keywords"], 5)
    return res

@app.post("/api/content/moderate")
def api_moderate(req: TextRequest):
    return moderate_text(req.text)

@app.post("/api/content/plagiarism")
def api_plagiarism(req: TextRequest):
    return check_plagiarism(req.text)

@app.post("/api/content/translate")
def api_translate(req: TranslateRequest):
    return translate_caption(req.text, req.target_language)

@app.post("/api/content/image-prompt")
def api_image_prompt(req: CaptionRequest):
    return generate_prompt_package(req.topic, req.platform)

@app.post("/api/ml/predict-engagement")
def api_predict(req: PredictionRequest):
    return predict_engagement(req.dict())

@app.post("/api/ml/ab-test")
def api_ab(req: ABRequest):
    return compare_two_captions(req.caption_a, req.caption_b, req.platform, req.content_type, req.day_of_week, req.hour_posted)

@app.get("/api/ml/ab-insights")
def api_ab_insights():
    return {"insights": historical_ab_insights()}

@app.get("/api/analytics/summary")
def api_analytics(platform: Optional[str] = None):
    return analytics_summary(platform)

@app.get("/api/competitors/summary")
def api_competitors():
    return competitor_summary()

@app.get("/api/scheduler/summary")
def api_scheduler():
    return scheduler_summary()

@app.get("/api/scheduler/best-time")
def api_best_time(platform: str = "Instagram"):
    return recommend_best_time(platform)

@app.post("/api/publisher/dry-run")
def api_publish(req: PublishRequest):
    return publish_post(req.platform, req.caption, req.media_url, dry_run=True)

@app.post("/api/content/full-pipeline")
def api_full_pipeline(req: CaptionRequest):
    caption = generate_caption(req.topic, req.platform, req.tone)
    hashtags = hashtag_strategy(caption, req.platform)
    moderation = moderate_text(caption)
    plagiarism = check_plagiarism(caption)
    image_prompt = generate_prompt_package(req.topic, req.platform)
    prediction = predict_engagement({"platform": req.platform, "content_type": "reel", "day_of_week": "Friday", "hour_posted": 19, "caption": caption, "hashtags": hashtags["hashtag_string"], "sentiment_score": 0.7, "has_image": 1})
    return {"caption": caption, "hashtags": hashtags, "moderation": moderation, "plagiarism": plagiarism, "image_prompt": image_prompt, "engagement_prediction": prediction}
