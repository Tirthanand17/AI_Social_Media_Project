from datetime import datetime
import re

PLATFORM_FORMATS = {"instagram": "vertical 9:16", "linkedin": "square 1:1 professional", "facebook": "square 1:1", "twitter": "horizontal 16:9", "x": "horizontal 16:9", "youtube": "horizontal 16:9"}

def keywords(text, limit=5):
    stop = set("the is are to for and of in on with this that your you we our it as by from use using how why what".split())
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text).lower()).split()
    return list(dict.fromkeys([w for w in words if len(w)>2 and w not in stop]))[:limit]

def detect_category(text):
    t = str(text).lower()
    if any(x in t for x in ["ai", "automation", "machine learning"]): return "AI and automation"
    if any(x in t for x in ["data", "analytics", "dashboard"]): return "data analytics"
    if any(x in t for x in ["business", "startup", "marketing"]): return "business growth"
    return "social media content"

def generate_image_prompt(topic, platform="Instagram", content_type="social media visual"):
    kw = ", ".join(keywords(topic))
    fmt = PLATFORM_FORMATS.get(platform.lower(), "vertical 9:16")
    return f"Create a high-quality {content_type} about '{topic}'. Category: {detect_category(topic)}. Include visual elements for: {kw}. Style: modern, realistic, clean, premium social media design. Format: {fmt}. Use clear subject, soft lighting, readable empty space for title. Avoid watermark, blurry details, distorted hands, messy text, and unrealistic AI look."

def generate_video_prompt(topic, platform="Instagram", duration_seconds=15):
    kw = ", ".join(keywords(topic))
    fmt = PLATFORM_FORMATS.get(platform.lower(), "vertical 9:16")
    return f"Create a {duration_seconds}-second short video about '{topic}'. Show problem, AI-powered solution, and final result. Include: {kw}. Style: cinematic, natural, modern creator/business workflow. Format: {fmt}. Avoid watermark and distorted people."

def generate_prompt_package(topic, platform="Instagram"):
    return {"topic": topic, "platform": platform, "category": detect_category(topic), "keywords": keywords(topic), "image_prompt": generate_image_prompt(topic, platform), "thumbnail_prompt": generate_image_prompt(topic, platform, "reel thumbnail"), "video_prompt": generate_video_prompt(topic, platform), "created_at": datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    print(generate_prompt_package("AI Social Media Automation for creators"))
