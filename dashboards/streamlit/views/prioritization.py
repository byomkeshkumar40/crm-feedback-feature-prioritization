import pandas as pd
import plotly.express as px
import streamlit as st

import common as c

df, f = c.get_filtered()
st.title("Feature Prioritization")
st.caption("SYNTHETIC data · RICE = Reach × Impact × Confidence ÷ Effort")
c.require_data(f)
st.markdown('<div class="note"><b>RICE scores do not change with the sidebar filters.</b> They use the full 12-month dataset and fixed, documented '
            'assumptions (Impact, Confidence, Effort are analyst <i>estimates</i>, not facts). Only the "In filters" column responds to filters. '
            'Use the what-if controls below to test assumptions.</div>', unsafe_allow_html=True)

w1, w2, _ = st.columns([1, 1, 2])
mult = w1.slider("Reporting multiplier (estimate)", 1.0, 5.0, 2.5, 0.5, help="Affected accounts represented by each account that reported.")
case = w2.selectbox("Effort scenario (estimate)", ["base", "low", "high"], help="Which person-month estimate to use.")
t = c.rice_whatif(mult, case)
base_case = abs(mult - 2.5) < 1e-9 and case == "base"
st.caption("Showing base-case assumptions." if base_case else f"What-if: multiplier {mult}, effort '{case}'. Ranks below are NOT the published base case.")

assume = pd.read_csv(c.ROOT / "data" / "assumptions" / "feature_assumptions.csv").set_index("feature_id")
cur = {fid: int(f.issue_theme.isin(assume.loc[fid, "themes"].split("|")).sum()) for fid in t.feature_id}
t["feedback_in_current_filters"] = t.feature_id.map(cur)
show = t[["priority_rank", "feature_id", "feature_name", "supporting_feedback_count", "unique_affected_customers", "reach", "impact",
          "confidence", "effort", "rice_score", "recommendation", "feedback_in_current_filters"]].rename(columns={
    "priority_rank": "Rank", "feature_id": "ID", "feature_name": "Feature", "supporting_feedback_count": "Feedback",
    "unique_affected_customers": "Customers", "reach": "Reach*", "impact": "Impact*",
    "confidence": "Conf.*", "effort": "Effort pm*", "rice_score": "RICE score", "recommendation": "Recommendation",
    "feedback_in_current_filters": "In filters"})
st.caption("Columns marked with an asterisk are analyst estimates. 'Feedback' and 'Customers' are observed over the full dataset; 'In filters' follows the sidebar filters.")
show = show.drop(columns="ID").assign(Feature=show["ID"] + " " + show["Feature"])
st.dataframe(show, hide_index=True, use_container_width=True, height=500,
             column_config={"Rank": st.column_config.NumberColumn("Rank", width="small"), "Feature": st.column_config.TextColumn("Feature", width=300), "RICE score": st.column_config.NumberColumn("RICE score", format="%.1f", width="small"), "Recommendation": st.column_config.TextColumn("Recommendation", width=210), "In filters": st.column_config.NumberColumn("In filters", width="small")})

l, r = st.columns(2)
fig = px.scatter(t, x="effort", y="reach", size="rice_score", color="recommendation", text="feature_id", title="Reach vs Effort (bubble size = RICE score)",
                 color_discrete_sequence=c.SEQ, labels={"effort": "Effort (person-months, estimate)", "reach": "Reach (accounts / 12 mo, estimate)"})
fig.update_traces(textposition="top center")
l.plotly_chart(c.style_fig(fig, 420), use_container_width=True)
top = t.sort_values("rice_score").tail(6)
fig = px.bar(top, x="rice_score", y="feature_name", orientation="h", title="Top recommended features by RICE score", text="rice_score",
             color_discrete_sequence=[c.BLUE], labels={"rice_score": "RICE score", "feature_name": ""})
fig.update_traces(texttemplate="%{text:.1f}")
r.plotly_chart(c.style_fig(fig, 420), use_container_width=True)

st.subheader("How to read the sensitivity of these ranks")
stab = pd.read_csv(c.PROC / "rice" / "rank_stability.csv")
stab = stab.rename(columns={"feature_id": "ID", "feature_name": "Feature", "base_rank": "Base rank", "median_rank": "Median rank (MC)",
                            "p10_rank": "P10", "p90_rank": "P90", "prob_top3_pct": "% trials in top 3", "prob_rank1_pct": "% trials ranked #1"})
st.caption("Monte Carlo: 5,000 trials with Reach, Impact, Confidence and Effort each perturbed ±30% (base assumptions, full data).")
st.dataframe(stab, hide_index=True, use_container_width=True, height=470)
