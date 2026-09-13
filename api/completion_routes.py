"""Routes added during the PROJECT_GUIDE completion audit."""

from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/api/content/bulk-generate")
async def bulk_generate(file: UploadFile = File(...)):
    """Generate one best-effort caption/prediction for each CSV topic row.

    Expected columns: topic,platform. Processing is bounded to 100 rows to keep
    one upload from consuming unbounded AI/API resources.
    """
    if file.content_type not in {None, "text/csv", "application/csv", "application/vnd.ms-excel"} and not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file with topic and platform columns.")

    raw = await file.read()
    if len(raw) > 1_000_000:
        raise HTTPException(status_code=413, detail="CSV is too large; maximum size is 1 MB.")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "topic" not in {name.strip().lower() for name in reader.fieldnames}:
        raise HTTPException(status_code=400, detail="CSV must contain a topic column.")

    try:
        from nlp.caption_generator import generate_caption
        from ml_models.predictor import predict_engagement
    except ImportError:
        from caption_generator import generate_caption
        from predictor import predict_engagement

    results = []
    for index, row in enumerate(reader):
        if index >= 100:
            break
        normalized = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
        topic = str(normalized.get("topic") or "").strip()
        platform = str(normalized.get("platform") or "Instagram").strip() or "Instagram"
        if not topic:
            continue

        caption = generate_caption(topic, platform)
        prediction_input = {
            "platform": platform,
            "content_type": "image",
            "day_of_week": datetime.now().strftime("%A"),
            "hour_posted": datetime.now().hour,
            "caption": caption,
            "hashtags": " ".join(word for word in caption.split() if word.startswith("#")),
            "sentiment_score": 0.5,
            "has_image": 1,
        }
        try:
            prediction = predict_engagement(prediction_input)
            score = prediction.get("predicted_engagement_score")
        except Exception as exc:
            prediction = {"status": "prediction_unavailable", "message": str(exc)[:300]}
            score = None

        results.append({
            "topic": topic,
            "platform": platform,
            "caption": caption,
            "predicted_engagement": score,
            "prediction": prediction,
        })

    return {"processed": len(results), "truncated_at": 100, "results": results}


@router.get("/api/cache/status")
def cache_status_route():
    from api.cache import cache_status

    return cache_status()


@router.get("/api/reports/weekly-preview")
def weekly_report_preview(platform: str | None = None):
    from api.email_reporter import send_weekly_report

    return send_weekly_report(platform=platform, dry_run=True)


@router.get("/api/scheduler/due-preview")
def due_schedule_preview():
    from scheduler.auto_scheduler import process_due_posts

    return process_due_posts(dry_run=True)
