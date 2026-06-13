from pathlib import Path
import re
import pandas as pd
from keyword_extractor import extract_keywords

ROOT = Path(__file__).resolve().parents[1]
NLP_DATA = ROOT / "data" / "raw" / "03_nlp_captions_dataset.csv"
TREND_DATA = ROOT / "data" / "raw" / "07_trends_data.csv"

PLATFORM_TAGS = {
    "instagram": ["#Reels", "#ExplorePage", "#InstagramGrowth"],
    "linkedin": ["#LinkedIn", "#ProfessionalGrowth", "#CareerGrowth"],
    "facebook": ["#FacebookMarketing", "#Community", "#DigitalMarketing"],
    "twitter": ["#Trending", "#XCommunity", "#SocialMedia"],
    "x": ["#Trending", "#XCommunity", "#SocialMedia"],
}

def title_hashtag(word):
    word = re.sub(r"[^a-zA-Z0-9]", "", str(word))
    return "#" + word[:1].upper() + word[1:] if word else ""

def load_trending_hashtags(limit=15):
    tags = []
    if TREND_DATA.exists():
        df = pd.read_csv(TREND_DATA).sort_values("trend_score", ascending=False)
        for value in df.get("related_hashtags", pd.Series(dtype=str)).dropna().astype(str):
            tags.extend(re.findall(r"#\w+", value))
    return list(dict.fromkeys(tags))[:limit]

def load_dataset_hashtags(limit=15):
    tags = []
    if NLP_DATA.exists():
        df = pd.read_csv(NLP_DATA)
        if "caption" in df.columns:
            for text in df["caption"].dropna().astype(str):
                tags.extend(re.findall(r"#\w+", text))
    return list(dict.fromkeys(tags))[:limit]

def generate_hashtags(text, platform="Instagram", max_hashtags=10):
    tags = []
    for item in extract_keywords(text, top_n=8):
        tag = title_hashtag(item["keyword"])
        if tag:
            tags.append(tag)
    tags.extend(PLATFORM_TAGS.get(platform.lower(), PLATFORM_TAGS["instagram"]))
    tags.extend(load_trending_hashtags(10))
    tags.extend(load_dataset_hashtags(5))
    clean = []
    seen = set()
    for tag in tags:
        key = tag.lower()
        if tag and key not in seen:
            clean.append(tag)
            seen.add(key)
    return clean[:max_hashtags]

def hashtag_strategy(text, platform="Instagram"):
    tags = generate_hashtags(text, platform)
    return {
        "platform": platform,
        "input_text": text,
        "hashtags": tags,
        "hashtag_string": " ".join(tags),
        "total_hashtags": len(tags),
        "strategy": "keywords + platform tags + 07_trends_data.csv + 03_nlp_captions_dataset.csv",
    }

if __name__ == "__main__":
    print(hashtag_strategy("AI social media automation for business growth", "Instagram"))
