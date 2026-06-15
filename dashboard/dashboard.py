import sys
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for p in [ROOT, ROOT / "nlp", ROOT / "ml_models", ROOT / "api", ROOT / "scheduler"]:
    sys.path.append(str(p))

from caption_generator import generate_caption, generate_multiple_captions
from hashtag_generator import hashtag_strategy
from predictor import predict_engagement
from trend_analyzer import analyze_trends, suggest_content_ideas
from analytics_fetcher import analytics_summary
from auto_scheduler import recommend_best_time
from content_moderator import moderate_text
from plagiarism_checker import check_plagiarism
from image_generator import generate_prompt_package

st.set_page_config(page_title="AI Social Media Automation", layout="wide")
st.title("AI Social Media Automation - Free Prototype")

tab1, tab2, tab3, tab4 = st.tabs(["Generate", "Predict", "Trends", "Analytics"])

with tab1:
    topic = st.text_input("Topic", "AI Social Media Automation for creators")
    platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "Twitter"])
    tone = st.selectbox("Tone", ["engaging", "professional", "casual", "motivational"])
    if st.button("Generate Content"):
        caption = generate_caption(topic, platform, tone)
        st.subheader("Caption")
        st.write(caption)
        st.subheader("Hashtags")
        st.write(hashtag_strategy(caption, platform)["hashtag_string"])
        st.subheader("Moderation")
        st.json(moderate_text(caption))
        st.subheader("Plagiarism")
        st.json(check_plagiarism(caption))
        st.subheader("Image/Video Prompt")
        st.json(generate_prompt_package(topic, platform))

with tab2:
    cap = st.text_area("Caption for prediction", "Want to save 5 hours every week? Try AI automation today. #AI #Automation")
    if st.button("Predict Engagement"):
        data = {"platform":"Instagram", "content_type":"reel", "day_of_week":"Friday", "hour_posted":19, "caption":cap, "hashtags":"#AI #Automation", "sentiment_score":0.7, "has_image":1}
        st.json(predict_engagement(data))
        st.write("Best time:", recommend_best_time("Instagram"))

with tab3:
    res = analyze_trends(20)
    if res.get("status") == "success":
        st.dataframe(pd.DataFrame(res["trending_keywords"]))
        st.write("Content Ideas")
        st.json(suggest_content_ideas(res["trending_keywords"]))

with tab4:
    st.json(analytics_summary())
