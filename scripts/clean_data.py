"""Clean raw SYNTHETIC feedback: normalise text fields, parse dates, impute blanks, tag themes."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from themes import T, tag_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"

CANON = {
    "feedback_source": ["Support Ticket", "Customer Survey", "Feature Request", "In-App Feedback"],
    "subscription_plan": ["Starter", "Professional", "Enterprise"],
    "customer_segment": ["SMB", "Mid-Market", "Enterprise"],
    "feature_area": ["Lead Management", "Contact Management", "Workflow Automation",
                     "Reporting", "Integrations", "User Interface"],
    "feedback_category": ["Bug", "Feature Request", "Usability Issue", "Performance Issue", "Integration Issue"],
    "sentiment": ["Positive", "Neutral", "Negative"],
    "severity": ["Low", "Medium", "High", "Critical"],
    "customer_impact": ["Minor Inconvenience", "Workflow Slowdown", "Blocks Key Task", "Revenue/Operations Risk"],
}


def parse_dates(s):
    iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    alt = pd.to_datetime(s, format="%d-%b-%Y", errors="coerce")
    return iso.fillna(alt)


def clean(raw):
    log = {"rows_in": len(raw)}
    df = raw.copy()
    changed = {}
    for col, allowed in CANON.items():
        lookup = {a.lower(): a for a in allowed}
        stripped = df[col].astype("string").str.strip()
        mapped = stripped.str.lower().map(lookup)
        changed[col] = int(((mapped != df[col]) & mapped.notna()).sum())
        df[col] = mapped
    log["values_normalised_by_column"] = changed
    log["missing_customer_impact_before"] = int(df["customer_impact"].isna().sum())
    df["customer_impact"] = df["customer_impact"].fillna("Unknown")
    log["customer_impact_imputed_as_Unknown"] = log["missing_customer_impact_before"]
    raw_dates = df["submission_date"].astype(str)
    log["non_iso_dates_converted"] = int((~raw_dates.str.match(r"^\d{4}-\d{2}-\d{2}$")).sum())
    df["submission_date"] = parse_dates(raw_dates)
    df["feedback_text"] = df["feedback_text"].astype(str).str.strip()
    tags = df["feedback_text"].map(tag_text)
    df["issue_theme"] = tags.map(lambda t: t[0] if len(t) == 1 else None)
    df["issue_theme_label"] = df["issue_theme"].map(lambda t: T[t]["label"] if t else None)
    log["theme_tag_unmatched"] = int(df["issue_theme"].isna().sum())
    log["theme_tag_ambiguous"] = int(tags.map(len).gt(1).sum())
    df["month"] = df["submission_date"].dt.to_period("M").astype(str)
    log["rows_out"] = len(df)
    return df, log


def main():
    PROC.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW / "feedback_raw.csv", dtype=str)
    df, log = clean(raw)
    out = df.copy()
    out["submission_date"] = out["submission_date"].dt.strftime("%Y-%m-%d")
    out.to_csv(PROC / "feedback_clean.csv", index=False)
    (PROC / "cleaning_log.json").write_text(json.dumps(log, indent=2))
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
