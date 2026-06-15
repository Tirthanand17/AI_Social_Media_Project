import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "api"), str(ROOT / "nlp")])

from analytics_fetcher import analytics_summary
from trend_analyzer import analyze_trends

st.set_page_config(page_title="Analytics", layout="wide")
st.title("Analytics")

platform = st.selectbox("Platform filter", ["All", "Instagram", "LinkedIn", "Facebook", "Twitter"])
summary = analytics_summary(None if platform == "All" else platform)

cols = st.columns(4)
cols[0].metric("Posts", summary["records"])
cols[1].metric("Reach", summary["total_reach"])
cols[2].metric("Likes", summary["total_likes"])
cols[3].metric("Avg ER", summary["avg_engagement_rate"])

st.subheader("Top Posts")
st.dataframe(pd.DataFrame(summary["top_posts"]), use_container_width=True)

st.subheader("Trends")
trends = analyze_trends(20, None if platform == "All" else platform)
st.dataframe(pd.DataFrame(trends.get("trending_keywords", [])), use_container_width=True)
