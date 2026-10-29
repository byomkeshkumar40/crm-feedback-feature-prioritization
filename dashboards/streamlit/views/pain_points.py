import plotly.express as px
import streamlit as st

import common as c

df, f = c.get_filtered()
st.title("Customer Pain Points")
st.caption("SYNTHETIC data · complaints = every category except Feature Request · metrics reflect the sidebar filters")
c.require_data(f)

comp = f[f.feedback_category != "Feature Request"]
l, r = st.columns(2)
if comp.empty:
    l.info("No complaint records under the current filters.")
else:
    t = comp.groupby(["issue_theme_label", "feature_area"]).agg(records=("feedback_id", "count"), customers=("customer_id", "nunique")).reset_index()
    t = t.sort_values("records", ascending=False).head(10).sort_values("records")
    fig = px.bar(t, x="records", y="issue_theme_label", color="feature_area", orientation="h", title="Most common complaints (top 10 themes)",
                 hover_data=["customers"], color_discrete_sequence=c.SEQ, category_orders={"issue_theme_label": list(t.issue_theme_label)}, labels={"records": "Feedback records", "issue_theme_label": ""})
    l.plotly_chart(c.style_fig(fig, 420), use_container_width=True)
hs = f[f.severity.isin(["High", "Critical"])].groupby(["feature_area", "severity"]).size().reset_index(name="records")
if hs.empty:
    r.info("No High/Critical records under the current filters.")
else:
    fig = px.bar(hs, y="feature_area", x="records", color="severity", orientation="h", title="High-severity issues by feature area", barmode="stack",
                 color_discrete_map={"High": "#F2A93B", "Critical": "#D64545"}, labels={"feature_area": "", "records": "Feedback records"}, category_orders={"severity": ["High", "Critical"]})
    r.plotly_chart(c.style_fig(fig, 420), use_container_width=True)

l, r = st.columns(2)
for col, key, ttl in [(l, "subscription_plan", "Feedback by subscription plan"), (r, "customer_segment", "Feedback by customer segment")]:
    g = f.groupby(key).agg(records=("feedback_id", "count"), customers=("customer_id", "nunique")).reset_index().melt(key, var_name="measure", value_name="count")
    g["measure"] = g.measure.map({"records": "Feedback records", "customers": "Unique customers"})
    fig = px.bar(g, x=key, y="count", color="measure", barmode="group", title=ttl, color_discrete_sequence=[c.BLUE, "#F2A93B"],
                 labels={key: "", "count": "Count", "measure": ""})
    col.plotly_chart(c.style_fig(fig), use_container_width=True)
st.markdown('<div class="note">Plan and segment volumes depend on how many accounts each group has. '
            'Enterprise: 74 of 420 accounts; Starter: 166. Compare per-account rates in the report, not raw counts.</div>', unsafe_allow_html=True)

sa = (f.groupby(["feature_area", "sentiment"]).size().reset_index(name="records"))
sa["pct"] = sa.records / sa.groupby("feature_area").records.transform("sum") * 100
fig = px.bar(sa, x="pct", y="feature_area", color="sentiment", orientation="h", barmode="stack", title="Sentiment by feature area (% of area records)",
             color_discrete_map=c.SENT_COLORS, category_orders={"sentiment": ["Negative", "Neutral", "Positive"]}, hover_data=["records"],
             labels={"pct": "% of records", "feature_area": ""})
st.plotly_chart(c.style_fig(fig, 380), use_container_width=True)
