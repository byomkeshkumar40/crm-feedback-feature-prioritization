"""Shared data loading, filters, styling for the dashboard (SYNTHETIC data)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from calculate_rice import BASE, evidence_table, score, recommendation  # noqa: E402

PROC = ROOT / "data" / "processed"
SENT_COLORS = {"Negative": "#D64545", "Neutral": "#98A2B3", "Positive": "#2E9E6B"}
SEV_ORDER = ["Low", "Medium", "High", "Critical"]
BLUE, NAVY = "#2F6FDE", "#1F3A5F"
SEQ = ["#2F6FDE", "#1F3A5F", "#7AA7F0", "#F2A93B", "#2E9E6B", "#8E6FD8"]

CSS = """
<style>
.block-container {padding-top: 1.6rem; max-width: 1400px;}
h1, h2, h3 {letter-spacing: -0.01em;}
.kpi {background: #fff; border: 1px solid #E4E9F2; border-radius: 12px; padding: 16px 18px;
      box-shadow: 0 1px 2px rgba(16,24,40,.05);}
.kpi .label {font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: #667085; font-weight: 600;}
.kpi .value {font-size: 30px; font-weight: 700; color: #1F3A5F; line-height: 1.2;}
.kpi .sub {font-size: 12px; color: #98A2B3;}
.badge {display:inline-block; background:#FDECEC; color:#B42318; border-radius:6px; padding:2px 8px; font-size:12px; font-weight:600;}
.note {background:#F3F7FE; border-left:4px solid #2F6FDE; padding:10px 14px; border-radius:6px; font-size:14px; margin: 8px 0 16px;}
</style>
"""


@st.cache_data
def load():
    df = pd.read_csv(PROC / "feedback_clean.csv", parse_dates=["submission_date"])
    return df


@st.cache_data
def rice_base():
    return pd.read_csv(PROC / "rice" / "rice_scores.csv")


@st.cache_data
def rice_whatif(multiplier: float, effort_case: str):
    assume = pd.read_csv(ROOT / "data" / "assumptions" / "feature_assumptions.csv")
    df = load()
    ev = evidence_table(df, assume)
    n_acc = len(pd.read_csv(ROOT / "data" / "raw" / "customers.csv"))
    t = score(assume, ev, n_acc, {**BASE, "reporting_multiplier": multiplier, "effort": effort_case})
    t["recommendation"] = t.priority_rank.map(recommendation)
    return t


def kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>'
                 f'<div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def sidebar_filters(df):
    sb = st.sidebar
    sb.markdown("### Filters")
    sb.caption("Apply to feedback metrics on every page. RICE scores are NOT affected (see page 3).")
    plan = sb.multiselect("Subscription plan", ["Starter", "Professional", "Enterprise"], ["Starter", "Professional", "Enterprise"])
    area = sb.multiselect("Feature area", sorted(df.feature_area.unique()), sorted(df.feature_area.unique()))
    sent = sb.multiselect("Sentiment", ["Positive", "Neutral", "Negative"], ["Positive", "Neutral", "Negative"])
    sev = sb.multiselect("Severity", SEV_ORDER, SEV_ORDER)
    dmin, dmax = df.submission_date.min().date(), df.submission_date.max().date()
    dr = sb.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
    if not isinstance(dr, (tuple, list)) or len(dr) != 2:
        dr = (dmin, dmax)
    sb.markdown("---")
    sb.markdown('<span class="badge">SYNTHETIC DATA</span>', unsafe_allow_html=True)
    sb.caption("1,500 randomly generated records for a fictional CRM company. No real customers.")
    m = (df.subscription_plan.isin(plan) & df.feature_area.isin(area) & df.sentiment.isin(sent) & df.severity.isin(sev)
         & (df.submission_date.dt.date >= dr[0]) & (df.submission_date.dt.date <= dr[1]))
    return df[m]


def style_fig(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=40, b=10), font=dict(family="Inter, Helvetica, Arial", size=13),
                      paper_bgcolor="white", plot_bgcolor="white", legend=dict(orientation="h", y=-0.2),
                      title=dict(font=dict(size=15, color=NAVY)))
    fig.update_xaxes(gridcolor="#EEF1F6"); fig.update_yaxes(gridcolor="#EEF1F6")
    return fig


def get_filtered():
    df = st.session_state["_full"]
    f = st.session_state["_filtered"]
    return df, f


def require_data(f):
    if f.empty:
        st.warning("No feedback matches the current filters. Widen the filters in the sidebar.")
        st.stop()
