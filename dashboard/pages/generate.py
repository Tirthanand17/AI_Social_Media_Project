import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "nlp"), str(ROOT / "api")])

from caption_generator import generate_caption
from hashtag_generator import hashtag_strategy
from content_moderator import moderate_text
from plagiarism_checker import check_plagiarism
from image_generator import generate_prompt_package

st.set_page_config(page_title="Generate Content", layout="wide")
st.title("Generate Content")

topic = st.text_input("Topic", "AI Social Media Automation for creators")
platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "Twitter"])
tone = st.selectbox("Tone", ["engaging", "professional", "casual", "motivational"])

if st.button("Generate"):
    caption = generate_caption(topic, platform, tone)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Caption")
        st.write(caption)
        st.subheader("Hashtags")
        st.write(hashtag_strategy(caption, platform)["hashtag_string"])
    with col2:
        st.subheader("Checks")
        st.json({"moderation": moderate_text(caption), "plagiarism": check_plagiarism(caption)})
        st.subheader("Creative Prompt")
        st.json(generate_prompt_package(topic, platform))
