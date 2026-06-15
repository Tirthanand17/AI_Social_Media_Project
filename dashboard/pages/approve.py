import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "publisher"), str(ROOT / "nlp")])

from publisher_manager import publish_post
from content_moderator import moderate_text

st.set_page_config(page_title="Approve and Publish", layout="wide")
st.title("Approve and Publish")

platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "Twitter"])
caption = st.text_area("Caption", "AI automation test caption #AI")
media_url = st.text_input("Media URL", "")

st.subheader("Moderation")
st.json(moderate_text(caption))

if st.button("Dry Run Publish"):
    st.json(publish_post(platform, caption, media_url or None, dry_run=True))
