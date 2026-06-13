from pathlib import Path
import pandas as pd
from predictor import predict_engagement

ROOT = Path(__file__).resolve().parents[1]
AB_DATA = ROOT / "data" / "raw" / "08_ab_testing_data.csv"

def caption_rule_score(caption):
    text = str(caption)
    lower = text.lower()
    score = 0
    reasons = []
    if "?" in text:
        score += 8; reasons.append("Question CTA can increase comments")
    if any(ch.isdigit() for ch in text):
        score += 7; reasons.append("Specific numbers can improve saves/shares")
    if any(w in lower for w in ["comment", "save", "share", "follow", "try"]):
        score += 5; reasons.append("Clear CTA present")
    if 60 <= len(text) <= 220:
        score += 4; reasons.append("Caption length suitable")
    if text.count("#") > 10:
        score -= 3; reasons.append("Too many hashtags")
    return score, reasons

def post_data(caption, platform="Instagram", content_type="reel", day_of_week="Friday", hour_posted=19):
    return {"platform":platform, "content_type":content_type, "day_of_week":day_of_week, "hour_posted":hour_posted, "caption":caption, "hashtags":"#AI #SocialMedia #Growth", "sentiment_score":0.7, "has_image":1}

def compare_two_captions(caption_a, caption_b, platform="Instagram", content_type="reel", day_of_week="Friday", hour_posted=19):
    pa = predict_engagement(post_data(caption_a, platform, content_type, day_of_week, hour_posted))
    pb = predict_engagement(post_data(caption_b, platform, content_type, day_of_week, hour_posted))
    ra, why_a = caption_rule_score(caption_a)
    rb, why_b = caption_rule_score(caption_b)
    fa, fb = pa["predicted_engagement_score"] + ra, pb["predicted_engagement_score"] + rb
    winner = "A" if fa >= fb else "B"
    return {"caption_a": caption_a, "caption_b": caption_b, "ml_score_a": pa["predicted_engagement_score"], "ml_score_b": pb["predicted_engagement_score"], "rule_score_a": ra, "rule_score_b": rb, "final_score_a": round(fa,2), "final_score_b": round(fb,2), "winner": winner, "winning_caption": caption_a if winner=="A" else caption_b, "reasons_a": why_a, "reasons_b": why_b}

def historical_ab_insights(limit=5):
    if not AB_DATA.exists():
        return []
    df = pd.read_csv(AB_DATA)
    return df.get("insight", pd.Series(dtype=str)).dropna().astype(str).head(limit).tolist()

if __name__ == "__main__":
    print("Historical insights:", historical_ab_insights())
    print(compare_two_captions("AI automation saves time. #AI", "Want to save 5 hours every week? Try AI automation today and comment YES. #AI"))
