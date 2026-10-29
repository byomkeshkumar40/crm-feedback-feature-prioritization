"""Compute descriptive feedback metrics from the cleaned SYNTHETIC data."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from themes import T  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT = PROC / "analysis"
HIGH = ["High", "Critical"]


def load():
    df = pd.read_csv(PROC / "feedback_clean.csv", parse_dates=["submission_date"])
    cust = pd.read_csv(RAW / "customers.csv")
    return df, cust


def vol_and_customers(df, by, cust_total=None):
    g = df.groupby(by).agg(feedback_records=("feedback_id", "count"), unique_customers=("customer_id", "nunique"))
    g["pct_of_records"] = (g.feedback_records / len(df) * 100).round(1)
    if cust_total is not None:
        g["pct_of_accounts_reporting"] = (g.unique_customers / cust_total.reindex(g.index) * 100).round(1)
    return g.sort_values("feedback_records", ascending=False)


def theme_table(df):
    g = df.groupby("issue_theme").agg(
        theme=("issue_theme_label", "first"), feature_area=("feature_area", "first"),
        category=("feedback_category", "first"), feedback_records=("feedback_id", "count"),
        unique_customers=("customer_id", "nunique"),
        negative_pct=("sentiment", lambda s: round((s == "Negative").mean() * 100, 1)),
        high_critical_pct=("severity", lambda s: round(s.isin(HIGH).mean() * 100, 1)),
        n_sources=("feedback_source", "nunique"), n_plans=("subscription_plan", "nunique"))
    g["blocking_or_risk_pct"] = df.groupby("issue_theme")["customer_impact"].apply(
        lambda s: round(s.isin(["Blocks Key Task", "Revenue/Operations Risk"]).mean() * 100, 1))
    return g.sort_values("feedback_records", ascending=False)


def analyse():
    df, cust = load()
    n_cust = len(cust)
    accts_by_plan = cust.groupby("subscription_plan").size()
    accts_by_seg = cust.groupby("customer_segment").size()
    res, tabs = {}, {}
    res["total_records"] = len(df)
    res["unique_customers"] = int(df.customer_id.nunique())
    res["customer_master_accounts"] = n_cust
    res["pct_accounts_with_feedback"] = round(df.customer_id.nunique() / n_cust * 100, 1)
    tabs["by_feature_area"] = vol_and_customers(df, "feature_area")
    tabs["by_category"] = vol_and_customers(df, "feedback_category")
    tabs["sentiment"] = vol_and_customers(df, "sentiment")
    tabs["severity"] = vol_and_customers(df, "severity").reindex(["Low", "Medium", "High", "Critical"])
    tabs["by_source"] = vol_and_customers(df, "feedback_source")
    tabs["by_plan"] = vol_and_customers(df, "subscription_plan", accts_by_plan)
    tabs["by_plan"]["accounts_in_base"] = accts_by_plan
    tabs["by_plan"]["records_per_account"] = (tabs["by_plan"].feedback_records / accts_by_plan).round(2)
    tabs["by_segment"] = vol_and_customers(df, "customer_segment", accts_by_seg)
    tabs["by_segment"]["accounts_in_base"] = accts_by_seg
    tabs["by_segment"]["records_per_account"] = (tabs["by_segment"].feedback_records / accts_by_seg).round(2)
    tabs["monthly_trend"] = df.groupby("month").agg(feedback_records=("feedback_id", "count"),
                                                   unique_customers=("customer_id", "nunique"))
    tabs["monthly_by_category"] = df.pivot_table(index="month", columns="feedback_category",
                                                 values="feedback_id", aggfunc="count", fill_value=0)
    tabs["sentiment_by_plan_pct"] = (pd.crosstab(df.subscription_plan, df.sentiment, normalize="index") * 100).round(1)
    tabs["sentiment_by_plan_n"] = pd.crosstab(df.subscription_plan, df.sentiment)
    tabs["sentiment_by_area_pct"] = (pd.crosstab(df.feature_area, df.sentiment, normalize="index") * 100).round(1)
    hs = df[df.severity.isin(HIGH)]
    tabs["high_sev_by_area"] = hs.groupby("feature_area").agg(
        high_critical_records=("feedback_id", "count"), unique_customers=("customer_id", "nunique")
    ).sort_values("high_critical_records", ascending=False)
    tabs["high_sev_by_area"]["share_of_area_records_pct"] = (
        tabs["high_sev_by_area"].high_critical_records / tabs["by_feature_area"].feedback_records * 100).round(1)
    themes = theme_table(df)
    tabs["themes"] = themes
    tabs["top_complaints"] = themes[themes.category != "Feature Request"].head(10)
    tabs["top_requests"] = themes[themes.category == "Feature Request"].head(10)
    tabs["plan_x_area_pct"] = (pd.crosstab(df.subscription_plan, df.feature_area, normalize="index") * 100).round(1)
    tabs["segment_x_theme_top"] = pd.crosstab(df.customer_segment, df.issue_theme_label)
    res["pct_negative"] = round((df.sentiment == "Negative").mean() * 100, 1)
    res["pct_high_critical"] = round(df.severity.isin(HIGH).mean() * 100, 1)
    res["n_feature_requests"] = int((df.feedback_category == "Feature Request").sum())
    res["peak_month"] = tabs["monthly_trend"].feedback_records.idxmax()
    res["first_month_records"] = int(tabs["monthly_trend"].feedback_records.iloc[0])
    res["last_month_records"] = int(tabs["monthly_trend"].feedback_records.iloc[-1])
    res["period"] = [str(df.submission_date.min().date()), str(df.submission_date.max().date())]
    return df, res, tabs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df, res, tabs = analyse()
    for k, t in tabs.items():
        t.to_csv(OUT / f"{k}.csv")
    (OUT / "summary.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))
    for k in ["by_feature_area", "by_category", "sentiment", "by_plan", "by_segment", "top_complaints", "top_requests",
              "high_sev_by_area", "sentiment_by_plan_pct"]:
        print("\n==", k); print(tabs[k].to_string())


if __name__ == "__main__":
    main()
