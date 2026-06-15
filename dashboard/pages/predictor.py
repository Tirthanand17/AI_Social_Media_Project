import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "ml_models"), str(ROOT / "scheduler")])

from predictor import predict_engagement
from auto_scheduler import recommend_best_time

st.set_page_config(page_title="Performance Predictor", layout="wide")
st.title("Performance Predictor")

caption = st.text_area("Caption", "Want to save 5 hours every week? Try AI automation today. #AI #Automation")
col1, col2, col3, col4 = st.columns(4)
platform = col1.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "Twitter"])
content_type = col2.selectbox("Format", ["reel", "carousel", "image", "video", "text"])
day = col3.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=4)
hour = col4.number_input("Hour", min_value=0, max_value=23, value=19)

if st.button("Score Post"):
    payload = {
        "platform": platform,
        "content_type": content_type,
        "day_of_week": day,
        "hour_posted": int(hour),
        "caption": caption,
        "hashtags": " ".join([word for word in caption.split() if word.startswith("#")]),
        "sentiment_score": 0.7,
        "has_image": 1,
    }
    st.json(predict_engagement(payload))
    st.subheader("Best Time")
    st.json(recommend_best_time(platform))
