from datetime import datetime
from pathlib import Path
import os
import re

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

PLATFORM_FORMATS = {
    "instagram": "vertical 9:16",
    "linkedin": "square 1:1 professional",
    "facebook": "square 1:1",
    "twitter": "horizontal 16:9",
    "x": "horizontal 16:9",
    "youtube": "horizontal 16:9",
}


def keywords(text, limit=5):
    stop = set("the is are to for and of in on with this that your you we our it as by from use using how why what".split())
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text).lower()).split()
    return list(dict.fromkeys([w for w in words if len(w) > 2 and w not in stop]))[:limit]


def detect_category(text):
    t = str(text).lower()
    if any(x in t for x in ["ai", "automation", "machine learning"]):
        return "AI and automation"
    if any(x in t for x in ["data", "analytics", "dashboard"]):
        return "data analytics"
    if any(x in t for x in ["business", "startup", "marketing"]):
        return "business growth"
    return "social media content"


def generate_image_prompt(topic, platform="Instagram", content_type="social media visual"):
    kw = ", ".join(keywords(topic))
    fmt = PLATFORM_FORMATS.get(platform.lower(), "vertical 9:16")
    return (
        f"Create a high-quality {content_type} about '{topic}'. Category: {detect_category(topic)}. "
        f"Include visual elements for: {kw}. Style: modern, realistic, clean, premium social media design. "
        f"Format: {fmt}. Use clear subject, soft lighting, readable empty space for title. "
        "Avoid watermark, blurry details, distorted hands, messy text, and unrealistic AI look."
    )


def generate_video_prompt(topic, platform="Instagram", duration_seconds=15):
    kw = ", ".join(keywords(topic))
    fmt = PLATFORM_FORMATS.get(platform.lower(), "vertical 9:16")
    return (
        f"Create a {duration_seconds}-second short video about '{topic}'. Show problem, AI-powered solution, "
        f"and final result. Include: {kw}. Style: cinematic, natural, modern creator/business workflow. "
        f"Format: {fmt}. Avoid watermark and distorted people."
    )


def generate_prompt_package(topic, platform="Instagram"):
    return {
        "topic": topic,
        "platform": platform,
        "category": detect_category(topic),
        "keywords": keywords(topic),
        "image_prompt": generate_image_prompt(topic, platform),
        "thumbnail_prompt": generate_image_prompt(topic, platform, "reel thumbnail"),
        "video_prompt": generate_video_prompt(topic, platform),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def generate_image(topic, platform="Instagram", live=None):
    """Optionally call the image API described by the project guide.

    The safe default is prompt-only. Set IMAGE_GENERATION_MODE=live and provide
    STABLE_DIFFUSION_API_KEY to make a real provider request.
    """
    package = generate_prompt_package(topic, platform)
    if live is None:
        live = os.getenv("IMAGE_GENERATION_MODE", "prompt_only").strip().lower() == "live"
    if not live:
        return {"status": "prompt_only", **package}

    api_key = os.getenv("STABLE_DIFFUSION_API_KEY", "").strip()
    if not api_key:
        return {"status": "missing_credentials", "message": "Set STABLE_DIFFUSION_API_KEY before live image generation.", **package}

    endpoint = os.getenv("STABLE_DIFFUSION_API_URL", "https://stablediffusionapi.com/api/v3/text2img").strip()
    payload = {
        "key": api_key,
        "prompt": package["image_prompt"],
        "width": "512",
        "height": "512",
        "samples": "1",
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=45)
        data = response.json() if response.text else {}
    except requests.RequestException as exc:
        return {"status": "image_provider_network_error", "message": str(exc)[:500], **package}
    except ValueError:
        return {"status": "image_provider_error", "message": "Provider returned a non-JSON response.", **package}

    if response.status_code >= 400:
        return {"status": "image_provider_error", "status_code": response.status_code, "message": str(data)[:800], **package}

    output = data.get("output") or []
    image_url = output[0] if isinstance(output, list) and output else data.get("image_url")
    return {"status": "generated" if image_url else "provider_response", "image_url": image_url, "provider_response": data, **package}


if __name__ == "__main__":
    print(generate_image("AI Social Media Automation for creators", live=False))
