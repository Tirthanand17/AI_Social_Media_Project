from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
for p in [ROOT, ROOT / "nlp", ROOT / "ml_models", ROOT / "api", ROOT / "scheduler", ROOT / "publisher"]:
    sys.path.append(str(p))

print("[1/8] Data cleaning")
from data.clean_data import clean_social_media_data
clean_df, clean_out = clean_social_media_data()
print("  rows:", len(clean_df), "saved:", clean_out)

print("[2/8] Feature engineering")
from ml_models.feature_engineering import get_features_and_target, save_engineered_features, create_best_time_json
X, y, df = get_features_and_target()
save_engineered_features(df)
create_best_time_json()
print("  X:", X.shape, "y:", y.shape)

print("[3/8] Model training")
from ml_models.train_model import train_model
metrics = train_model()
print("  metrics:", metrics)

print("[4/8] Prediction")
from ml_models.predictor import predict_engagement
sample = {"platform":"Instagram", "content_type":"reel", "day_of_week":"Friday", "hour_posted":19, "caption":"AI automation helps creators grow", "hashtags":"#AI #Automation", "sentiment_score":0.8, "has_image":1}
print("  prediction:", predict_engagement(sample))

print("[5/8] NLP modules")
from nlp.caption_generator import generate_caption
from nlp.hashtag_generator import hashtag_strategy
from nlp.trend_analyzer import analyze_trends
from nlp.content_moderator import moderate_text
from nlp.plagiarism_checker import check_plagiarism
from nlp.image_generator import generate_prompt_package
caption = generate_caption("AI Social Media Automation", "Instagram", "engaging")
print("  caption ok:", bool(caption))
print("  hashtags:", hashtag_strategy(caption, "Instagram")["hashtag_string"])
print("  trends:", analyze_trends(5)["status"])
print("  moderation:", moderate_text(caption)["status"])
print("  plagiarism:", check_plagiarism(caption)["status"])
print("  image prompt ok:", bool(generate_prompt_package("AI Social Media Automation")["image_prompt"]))

print("[6/8] Scheduler / analytics / auth")
from scheduler.auto_scheduler import scheduler_summary, recommend_best_time
from api.analytics_fetcher import analytics_summary
from api.auth import login
print("  scheduler statuses:", scheduler_summary()["by_status"])
print("  best time:", recommend_best_time("Instagram"))
print("  analytics records:", analytics_summary()["records"])
print("  login:", login("admin_techcreate", "admin123")["success"])

print("\nAll tests completed successfully")
