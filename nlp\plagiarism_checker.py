from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

def clean(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def load_existing_content():
    rows = []
    for file in RAW.glob("*.csv"):
        try:
            df = pd.read_csv(file)
        except Exception:
            continue
        for col in df.columns:
            if any(k in col.lower() for k in ["caption", "content", "text", "description"]):
                for value in df[col].dropna().astype(str):
                    rows.append({"source_file": file.name, "column": col, "text": value})
    return rows

def similarity(a, b):
    a, b = clean(a), clean(b)
    return SequenceMatcher(None, a, b).ratio() if a and b else 0

def check_plagiarism(input_text, threshold=0.75):
    best = {"score": 0, "text": "", "source_file": ""}
    matches = []
    for row in load_existing_content():
        s = similarity(input_text, row["text"])
        if s > best["score"]:
            best = {"score": s, "text": row["text"], "source_file": row["source_file"]}
        if s >= threshold:
            matches.append({"source_file": row["source_file"], "column": row["column"], "similarity_score": round(s*100, 2), "matched_text": row["text"]})
    percent = round(best["score"] * 100, 2)
    status = "High Similarity" if percent >= 75 else "Medium Similarity" if percent >= 45 else "Low Similarity"
    recommendation = "Rewrite the caption before posting." if percent >= 75 else "Modify some words and structure." if percent >= 45 else "Caption looks original."
    return {"input_text": input_text, "status": status, "plagiarism_percent": percent, "matches_found": len(matches), "source_file": best["source_file"], "most_similar_text": best["text"], "recommendation": recommendation, "matches": matches, "checked_at": datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    print(check_plagiarism("AI automation helps creators save time and grow their audience."))
