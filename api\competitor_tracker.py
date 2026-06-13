from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "data" / "raw" / "09_competitor_tracking_data.csv"

def competitor_summary():
    df = pd.read_csv(COMP)
    alerts = df[df["alert_triggered"] == 1] if "alert_triggered" in df.columns else df.iloc[0:0]
    return {"records": int(len(df)), "alerts": int(len(alerts)), "top_competitors": df.sort_values("followers_count", ascending=False).head(5).to_dict(orient="records"), "alert_rows": alerts.to_dict(orient="records")}

if __name__ == "__main__":
    print(competitor_summary())
