from pathlib import Path
import os
import random
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
NLP_DATA = ROOT / "data" / "raw" / "03_nlp_captions_dataset.csv"
AB_DATA = ROOT / "data" / "raw" / "08_ab_testing_data.csv"
load_dotenv(ROOT / ".env")

try:
    from google import genai
except Exception:
    genai = None

try:
    from groq import Groq
except Exception:
    Groq = None

def load_caption_examples(platform="Instagram", limit=5):
    examples = []
    if NLP_DATA.exists():
        df = pd.read_csv(NLP_DATA)
        if "platform" in df.columns:
            df = df[df["platform"].astype(str).str.lower() == platform.lower()]
        score_cols = [c for c in ["nlp_sentiment", "has_cta", "has_question", "has_emoji"] if c in df.columns]
        if score_cols:
            df["_score"] = df[score_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
            df = df.sort_values("_score", ascending=False)
        examples = df.get("caption", pd.Series(dtype=str)).dropna().astype(str).head(limit).tolist()
    return examples

def load_ab_insights(limit=5):
    if not AB_DATA.exists():
        return []
    df = pd.read_csv(AB_DATA)
    if "status" in df.columns:
        df = df[df["status"].astype(str).str.lower() == "completed"]
    return df.get("insight", pd.Series(dtype=str)).dropna().astype(str).head(limit).tolist()

def fallback_caption(topic, platform="Instagram", tone="engaging"):
    hooks = [
        f"Want to grow faster with {topic}?",
        f"Here is a smart way to use {topic}.",
        f"{topic} is changing how creators and brands work.",
        f"Let's talk about {topic}.",
    ]
    body_by_tone = {
        "professional": f"With the right strategy, {topic} can save time, improve planning, and create measurable growth.",
        "casual": f"If you are trying to improve your content, {topic} can make the process easier and smarter.",
        "engaging": f"Use {topic} to create better content, understand your audience, and post with confidence.",
        "motivational": f"Start small with {topic}, stay consistent, and build results step by step.",
    }
    ctas = ["Save this for later.", "Comment your thoughts below.", "Share this with someone who needs it.", "Follow for more practical tips."]
    hashtags = "#AI #SocialMedia #Automation #ContentCreation #Growth"
    return f"{random.choice(hooks)}\n\n{body_by_tone.get(tone.lower(), body_by_tone['engaging'])}\n\n{random.choice(ctas)}\n\n{hashtags}"

def build_generation_prompt(topic, platform="Instagram", tone="engaging", count=3):
    examples = "\n".join([f"- {x}" for x in load_caption_examples(platform, 5)])
    insights = "\n".join([f"- {x}" for x in load_ab_insights(5)])
    return f"""
Generate {count} {tone} social media captions for {platform} about: {topic}

Use these dataset examples as style reference:
{examples}

Use these A/B testing insights:
{insights}

Rules:
- Return only captions, numbered 1 to {count}.
- Each caption should include a hook, value, CTA, and hashtags.
- Keep it realistic and safe for brand posting.
"""

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

def generate_with_gemini(topic, platform="Instagram", tone="engaging", count=3):
    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not use_gemini or not api_key or genai is None:
        return None
    prompt = build_generation_prompt(topic, platform, tone, count)
    try:
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = client.models.generate_content(model=model, contents=prompt)
        return parse_numbered_captions(response.text, count)
    except Exception as e:
        print("Gemini failed, using local fallback:", e)
        return None

def generate_with_groq(topic, platform="Instagram", tone="engaging", count=3):
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
    api_key = os.getenv("GROQ_API_KEY", "")
    if not use_groq or not api_key or Groq is None:
        return None
    prompt = build_generation_prompt(topic, platform, tone, count)
    try:
        client = Groq(api_key=api_key)
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You write concise, brand-safe social media captions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=700,
        )
        text = response.choices[0].message.content
        return parse_numbered_captions(text, count)
    except Exception as e:
        print("Groq failed, using local fallback:", e)
        return None

def generate_captions(topic, platform="Instagram", tone="engaging", count=3):
    gemini_result = generate_with_gemini(topic, platform, tone, count)
    if gemini_result:
        return gemini_result
    groq_result = generate_with_groq(topic, platform, tone, count)
    if groq_result:
        return groq_result
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
