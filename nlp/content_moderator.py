from datetime import datetime
import re

BANNED = {
    "hate": ["hate", "racist", "harass", "bully"],
    "violence": ["kill", "attack", "bomb", "weapon", "violence"],
    "spam": ["get rich quick", "free money", "buy followers", "like for like", "follow for follow"],
    "scam": ["guaranteed income", "urgent payment", "click this link"],
}
SENSITIVE = ["medical advice", "financial advice", "legal advice", "politics", "religion"]

def moderate_text(text):
    raw = str(text or "")
    lower = raw.lower()
    flags = []
    for cat, words in BANNED.items():
        for w in words:
            if w in lower:
                flags.append({"category": cat, "word": w, "risk": "high"})
    for w in SENSITIVE:
        if w in lower:
            flags.append({"category": "sensitive_topic", "word": w, "risk": "medium"})
    if len(re.findall(r"#\w+", raw)) > 12:
        flags.append({"category": "spam_pattern", "word": "too many hashtags", "risk": "medium"})
    if len(re.findall(r"@\w+", raw)) > 5:
        flags.append({"category": "spam_pattern", "word": "too many mentions", "risk": "medium"})
    risk_score = sum(40 if f["risk"] == "high" else 20 if f["risk"] == "medium" else 10 for f in flags)
    risk_score = min(risk_score, 100)
    status = "Rejected" if risk_score >= 60 else "Needs Human Review" if risk_score >= 30 else "Approved"
    return {"text": raw, "status": status, "risk_score": risk_score, "total_flags": len(flags), "flags": flags, "checked_at": datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    print(moderate_text("AI automation helps creators save time. #AI"))
