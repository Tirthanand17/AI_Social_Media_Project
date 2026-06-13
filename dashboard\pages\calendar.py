import sys
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([str(ROOT / "scheduler")])

from auto_scheduler import scheduler_summary, recommend_best_time

st.set_page_config(page_title="Content Calendar", layout="wide")
st.title("Content Calendar")

summary = scheduler_summary()
cols = st.columns(3)
cols[0].metric("Total", summary["total"])
cols[1].metric("Pending", summary["by_status"].get("pending", 0))
cols[2].metric("Published", summary["by_status"].get("published", 0))

st.subheader("Pending Queue")
st.dataframe(pd.DataFrame(summary["pending"]), use_container_width=True)

st.subheader("Best Time")
platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Facebook", "Twitter"])
st.json(recommend_best_time(platform))
