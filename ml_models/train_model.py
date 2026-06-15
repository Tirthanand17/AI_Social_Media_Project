from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN, ML_DATA, OUT, get_features_and_target, save_engineered_features, create_best_time_json

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml_models" / "engagement_model.pkl"
FEATURES_PATH = ROOT / "ml_models" / "feature_list.json"
METRICS_PATH = ROOT / "ml_models" / "model_metrics.json"

def load_data():
    if OUT.exists():
        df = pd.read_csv(OUT)
        return df[FEATURE_COLUMNS], df[TARGET_COLUMN], df
    X, y, df = get_features_and_target(ML_DATA)
    save_engineered_features(df)
    return X, y, df

def train_model():
    X, y, df = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metrics = {
        "model": "RandomForestRegressor",
        "rows": int(len(df)),
        "features": FEATURE_COLUMNS,
        "mae": round(float(mean_absolute_error(y_test, pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, pred))), 4),
        "r2_score": round(float(r2_score(y_test, pred)), 4),
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    FEATURES_PATH.write_text(json.dumps(FEATURE_COLUMNS, indent=2), encoding="utf-8")
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    create_best_time_json()
    return metrics

if __name__ == "__main__":
    m = train_model()
    print("Model training completed")
    print(json.dumps(m, indent=2))
    print("Saved:", MODEL_PATH)
