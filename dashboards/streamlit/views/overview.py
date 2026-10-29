import plotly.express as px
import streamlit as st

import common as c

df, f = c.get_filtered()
st.title("Customer Feedback Overview")
st.caption("Fictional CRM company · SYNTHETIC data · Oct 2025 – Sep 2026 · metrics reflect the sidebar filters")
c.require_data(f)

cols = st.columns(5)
c.kpi(cols[0], "Total feedback", f"{len(f):,}", f"of {len(df):,} total")
c.kpi(cols[1], "Unique customers", f"{f.customer_id.nunique():,}", "accounts submitting feedback")
c.kpi(cols[2], "Negative feedback", f"{(f.sentiment == 'Negative').mean():.1%}", "share of filtered records")
c.kpi(cols[3], "High/Critical severity", f"{f.severity.isin(['High', 'Critical']).mean():.1%}", "share of filtered records")
c.kpi(cols[4], "Feature requests", f"{(f.feedback_category == 'Feature Request').sum():,}", "records categorised as requests")
st.markdown('<div class="note">Counts are <b>feedback volume</b>, not customer prevalence. Unique customers are shown where available; '
            'the account base (420) is the only known denominator.</div>', unsafe_allow_html=True)

l, r = st.columns([3, 2])
trend = f.groupby(["month", "feedback_category"]).size().reset_index(name="records")
fig = px.bar(trend, x="month", y="records", color="feedback_category", title="Feedback trend by month", color_discrete_sequence=c.SEQ,
             labels={"month": "Month", "records": "Feedback records", "feedback_category": "Category"})
l.plotly_chart(c.style_fig(fig), use_container_width=True)
s = f.sentiment.value_counts().reindex(["Negative", "Neutral", "Positive"]).fillna(0).reset_index()
s.columns = ["sentiment", "records"]
fig = px.pie(s, names="sentiment", values="records", hole=.55, title="Sentiment distribution", color="sentiment", color_discrete_map=c.SENT_COLORS)
r.plotly_chart(c.style_fig(fig), use_container_width=True)

l, r = st.columns(2)
cat = f.feedback_category.value_counts().reset_index(); cat.columns = ["category", "records"]
fig = px.bar(cat.sort_values("records"), x="records", y="category", orientation="h", title="Feedback by category", text="records",
             color_discrete_sequence=[c.BLUE], labels={"records": "Feedback records", "category": ""})
l.plotly_chart(c.style_fig(fig), use_container_width=True)
ar = f.groupby("feature_area").agg(records=("feedback_id", "count"), customers=("customer_id", "nunique")).reset_index()
fig = px.bar(ar.sort_values("records"), x="records", y="feature_area", orientation="h", title="Feedback by feature area", text="records",
             color_discrete_sequence=[c.NAVY], hover_data=["customers"], labels={"records": "Feedback records", "feature_area": ""})
r.plotly_chart(c.style_fig(fig), use_container_width=True)
