from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHED = ROOT / "data" / "raw" / "05_scheduler_data.csv"
BEST = ROOT / "data" / "raw" / "06_best_time_dataset.csv"

def load_schedule(status=None):
    df = pd.read_csv(SCHED)
    if status:
        df = df[df["status"].astype(str).str.lower() == status.lower()]
    return df

def pending_posts():
    return load_schedule("pending").to_dict(orient="records")

def recommend_best_time(platform="Instagram"):
    df = pd.read_csv(BEST)
    df = df[df["platform"].str.lower() == platform.lower()].sort_values("peak_score", ascending=False)
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def scheduler_summary():
    df = pd.read_csv(SCHED)
    return {"total": int(len(df)), "by_status": df["status"].value_counts().to_dict(), "pending": pending_posts(), "generated_at": datetime.now().isoformat(timespec="seconds")}

if __name__ == "__main__":
    print(scheduler_summary())
    print("Best Instagram time:", recommend_best_time("Instagram"))
