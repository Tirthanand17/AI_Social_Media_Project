import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

try:
    from google import genai
except Exception:
    genai = None


def fallback_caption(topic, platform="Instagram", tone="engaging"):
    hooks = [
        f"Want to grow faster with {topic}?",
        f"Here is a smarter way to use {topic}.",
        f"{topic} can help creators save time and post with more confidence.",
        f"Let's turn {topic} into a simple content workflow.",
    ]
    body_by_tone = {
        "professional": f"With the right workflow, {topic} can improve planning, reduce manual work, and support better content decisions.",
        "casual": f"If content creation feels time-consuming, {topic} can make the process easier and more consistent.",
        "engaging": f"Use {topic} to generate better captions, hashtags, image ideas, and posting plans in one place.",
        "motivational": f"Start small with {topic}, stay consistent, and build better content habits step by step.",
    }
    ctas = ["Save this for later.", "Comment your thoughts below.", "Share this with someone who needs it.", "Follow for more practical AI tips."]
    hashtags = "#AI #SocialMedia #Automation #ContentCreation #DigitalMarketing"
    return f"{random.choice(hooks)}\n\n{body_by_tone.get(tone.lower(), body_by_tone['engaging'])}\n\n{random.choice(ctas)}\n\n{hashtags}"


def build_generation_prompt(topic, platform="Instagram", tone="engaging", count=3):
    return f"""
Generate {count} {tone} social media captions for {platform} about: {topic}

Rules:
- Return only captions, numbered 1 to {count}.
- Each caption must include a strong hook, useful value, one CTA, and relevant hashtags.
- Keep it practical, brand-safe, and natural.
- Do not mention that an AI generated the caption unless the topic requires it.
""".strip()


def parse_numbered_captions(text, count=3):
    text = (text or "").strip()
    if not text:
        return []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    captions = []
    current = []
    for line in lines:
        marker = line.split(maxsplit=1)[0].rstrip(".):")
        if marker.isdigit() and current:
            captions.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        captions.append("\n".join(current).strip())
    cleaned = []
    for caption in captions:
        first, *rest = caption.splitlines()
        marker = first.split(maxsplit=1)[0].rstrip(".):")
        if marker.isdigit() and len(first.split(maxsplit=1)) > 1:
            first = first.split(maxsplit=1)[1]
        cleaned.append("\n".join([first, *rest]).strip())
    return cleaned[:count] if cleaned else [text]


def provider_status():
    provider = os.getenv("AI_TEXT_PROVIDER", "gemini").strip().lower() or "gemini"
    return {
        "ai_text_provider": provider,
        "ai_image_provider": os.getenv("AI_IMAGE_PROVIDER", "demo"),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "github_models_configured": bool(os.getenv("GITHUB_TOKEN")),
        "gemini_text_model": os.getenv("GEMINI_TEXT_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")),
        "github_model_name": os.getenv("GITHUB_MODEL_NAME", "openai/gpt-5"),
    }


def _provider_order():
    preferred = os.getenv("AI_TEXT_PROVIDER", "gemini").strip().lower() or "gemini"
    order = [preferred]
    for item in ["gemini", "github", "demo"]:
        if item not in order:
            order.append(item)
    return order


def generate_with_gemini(topic, platform="Instagram", tone="engaging", count=3):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        return None
    prompt = build_generation_prompt(topic, platform, tone, count)
    try:
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_TEXT_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
        response = client.models.generate_content(model=model, contents=prompt)
        return parse_numbered_captions(getattr(response, "text", ""), count)
    except Exception as exc:
        print("Gemini failed, using next provider:", exc)
        return None


def generate_with_github_models(topic, platform="Instagram", tone="engaging", count=3):
    api_key = os.getenv("GITHUB_TOKEN", "")
    if not api_key:
        return None
    prompt = build_generation_prompt(topic, platform, tone, count)
    try:
        base_url = os.getenv("GITHUB_MODELS_BASE_URL", "https://models.github.ai/inference").rstrip("/")
        model = os.getenv("GITHUB_MODEL_NAME", "openai/gpt-5")
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You write concise, brand-safe social media captions."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
            },
            timeout=40,
        )
        response.raise_for_status()
        data = response.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return parse_numbered_captions(text, count)
    except Exception as exc:
        print("GitHub Models failed, using next provider:", exc)
        return None


def generate_captions(topic, platform="Instagram", tone="engaging", count=3):
    for provider in _provider_order():
        if provider == "gemini":
            result = generate_with_gemini(topic, platform, tone, count)
        elif provider == "github":
            result = generate_with_github_models(topic, platform, tone, count)
        else:
            result = None
        if result:
            return result
    return [fallback_caption(topic, platform, tone) for _ in range(count)]


def generate_caption(topic, platform="Instagram", tone="engaging"):
    return generate_captions(topic, platform, tone, count=1)[0]


def generate_multiple_captions(topic, count=3, platform="Instagram"):
    tones = ["engaging", "professional", "casual", "motivational"]
    captions = []
    for i in range(count):
        tone = tones[i % len(tones)]
        captions.append({"option": i + 1, "tone": tone, "caption": generate_caption(topic, platform, tone)})
    return captions


if __name__ == "__main__":
    for item in generate_multiple_captions("AI Social Media Automation", 3, "Instagram"):
        print("\n---", item["tone"], "---")
        print(item["caption"])
