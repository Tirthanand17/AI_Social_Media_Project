from pathlib import Path
from collections import Counter
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NLP_DATA = ROOT / "data" / "raw" / "03_nlp_captions_dataset.csv"
STOPWORDS = set("""the is are am to for and or of in on with this that your you we our it as by from be can will about using use a an at into how why what when where who their they them was were has have had do does did but not so if then than too very just all new more get it""".split())

def clean_text(text):
    text = "" if text is None else str(text).lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9#@\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_keywords(text, top_n=10):
    words = [w.strip("#@") for w in clean_text(text).split()]
    words = [w for w in words if len(w) > 2 and w not in STOPWORDS]
    return [{"keyword": w, "count": c} for w, c in Counter(words).most_common(top_n)]

def extract_hashtags(text):
    return list(dict.fromkeys(re.findall(r"#\w+", str(text or ""))))

def extract_mentions(text):
    return list(dict.fromkeys(re.findall(r"@\w+", str(text or ""))))

def dataset_top_keywords(top_n=20):
    if not NLP_DATA.exists():
        return []
    df = pd.read_csv(NLP_DATA)
    text = " ".join(df.get("caption", pd.Series(dtype=str)).dropna().astype(str).tolist())
    return extract_keywords(text, top_n)

def keyword_analysis(text, top_n=10):
    return {
        "input_text": text,
        "keywords": extract_keywords(text, top_n),
        "hashtags": extract_hashtags(text),
        "mentions": extract_mentions(text),
        "total_words": len(clean_text(text).split()),
    }

if __name__ == "__main__":
    sample = "AI social media automation helps creators save time and grow faster. #AI #Automation"
    print(keyword_analysis(sample))
    print("Dataset keywords:", dataset_top_keywords(10))
