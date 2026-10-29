"""CRM Feedback Analysis & Feature Prioritization — Streamlit dashboard (SYNTHETIC data)."""
import streamlit as st

import common

st.set_page_config(page_title="CRM Feedback & Prioritization", page_icon="📊", layout="wide")
st.markdown(common.CSS, unsafe_allow_html=True)
full = common.load()
st.session_state["_full"] = full
st.session_state["_filtered"] = common.sidebar_filters(full)

pages = [st.Page("views/overview.py", title="Customer Feedback Overview", icon="📈", url_path="overview", default=True),
         st.Page("views/pain_points.py", title="Customer Pain Points", icon="🧯", url_path="pain-points"),
         st.Page("views/prioritization.py", title="Feature Prioritization", icon="🎯", url_path="prioritization")]
st.navigation(pages).run()
