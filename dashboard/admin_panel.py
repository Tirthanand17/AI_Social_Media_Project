import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.extend([str(ROOT / "api"), str(ROOT / "scheduler")])
from auth import login
from competitor_tracker import competitor_summary
from auto_scheduler import scheduler_summary

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("Admin Panel")
username = st.text_input("Username", "admin_techcreate")
password = st.text_input("Password", "admin123", type="password")
if st.button("Login"):
    st.session_state["login"] = login(username, password)

if st.session_state.get("login", {}).get("success"):
    st.success("Logged in")
    st.json(st.session_state["login"]["user"])
    st.subheader("Scheduler")
    st.json(scheduler_summary())
    st.subheader("Competitors")
    st.json(competitor_summary())
else:
    st.info("Test users from 10_users_data.csv: admin_techcreate/admin123, editor_techcreate/editor123, viewer_techcreate/viewer123")
