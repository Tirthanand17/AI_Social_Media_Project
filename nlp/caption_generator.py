import os
import random
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_FILE = ROOT / "nlp" / "system_prompt.txt"
NLP_DATA = ROOT / "data" / "raw" / "03_nlp_captions_dataset.csv"
load_dotenv(ROOT / ".env")

try:
    from google import genai
except Exception:
    genai = None

try:
    from groq import Groq
except Exception:
    Groq = None


def _env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


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


def reference_examples(platform="Instagram", limit=5):
    """Load real repository examples without pretending an unavailable rank exists."""
    if not NLP_DATA.exists():
        return []
    try:
        df = pd.read_csv(NLP_DATA)
        if "platform" in df.columns:
            selected = df[df["platform"].astype(str).str.lower() == str(platform).lower()]
            if selected.empty:
                selected = df
        else:
            selected = df
        if "caption" not in selected.columns:
            return []
        return selected["caption"].dropna().astype(str).head(limit).tolist()
    except Exception:
        return []


def load_system_prompt(platform="Instagram"):
    if SYSTEM_PROMPT_FILE.exists():
        base = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
    else:
        base = "You are an expert, brand-safe social media copywriter."
    examples = reference_examples(platform)
    if examples:
        joined = "\n".join(f"- {item}" for item in examples)
        base += f"\n\nRepository reference examples for {platform}:\n{joined}"
    return base


def build_generation_prompt(topic, platform="Instagram", tone="engaging", count=3):
    return f"""
Generate {count} {tone} social media captions for {platform} about: {topic}

Rules:
- Return only captions, numbered 1 to {count}.
- Each caption must include a strong hook, useful value, one CTA, and relevant hashtags.
- Match the communication style and length expectations of {platform}.
- Keep it practical, brand-safe, original, and natural.
- Do not claim facts that were not supplied in the topic.
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


def _preferred_provider():
    explicit = os.getenv("AI_TEXT_PROVIDER", "").strip().lower()
    if explicit:
        return explicit
    if _env_bool("USE_GROQ", False):
        return "groq"
    if _env_bool("USE_GEMINI", False):
        return "gemini"
    return "demo"


def provider_status():
    provider = _preferred_provider()
    return {
        "ai_text_provider": provider,
        "ai_image_provider": os.getenv("AI_IMAGE_PROVIDER", "demo"),
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "github_models_configured": bool(os.getenv("GITHUB_TOKEN")),
        "groq_model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "gemini_text_model": os.getenv("GEMINI_TEXT_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")),
        "github_model_name": os.getenv("GITHUB_MODEL_NAME", "openai/gpt-5"),
        "system_prompt_file": str(SYSTEM_PROMPT_FILE),
    }


def _provider_order():
    preferred = _preferred_provider()
    order = [preferred]
    for item in ["groq", "gemini", "github", "demo"]:
        if item not in order:
            order.append(item)
    return order


def generate_with_groq(topic, platform="Instagram", tone="engaging", count=3):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or Groq is None:
        return None
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[
                {"role": "system", "content": load_system_prompt(platform)},
                {"role": "user", "content": build_generation_prompt(topic, platform, tone, count)},
            ],
            temperature=0.8,
            max_tokens=900,
        )
        text = response.choices[0].message.content or ""
        return parse_numbered_captions(text, count)
    except Exception as exc:
        print("Groq failed, using next provider:", exc)
        return None


def generate_with_gemini(topic, platform="Instagram", tone="engaging", count=3):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or genai is None:
        return None
    prompt = load_system_prompt(platform) + "\n\n" + build_generation_prompt(topic, platform, tone, count)
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
                    {"role": "system", "content": load_system_prompt(platform)},
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
        if provider == "groq":
            result = generate_with_groq(topic, platform, tone, count)
        elif provider == "gemini":
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
    print(provider_status())
    for item in generate_multiple_captions("AI Social Media Automation", 3, "Instagram"):
        print("\n---", item["tone"], "---")
        print(item["caption"])
