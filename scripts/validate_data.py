"""Validate raw and cleaned SYNTHETIC feedback and write a data quality report."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clean_data import CANON  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, REP = ROOT / "data" / "raw", ROOT / "data" / "processed", ROOT / "reports"
EXPECTED_ROWS = 1500
COLS = ["feedback_id", "customer_id", "submission_date", "feedback_source", "subscription_plan",
        "customer_segment", "feature_area", "feedback_category", "feedback_text", "sentiment",
        "severity", "customer_impact"]


def run_checks(df, customers, stage):
    """Return list of (check, passed, detail)."""
    r = []
    add = lambda n, ok, d="": r.append((n, bool(ok), str(d)))  # noqa: E731
    add("required columns present", set(COLS) <= set(df.columns), f"missing={sorted(set(COLS) - set(df.columns))}")
    add(f"row count == {EXPECTED_ROWS}", len(df) == EXPECTED_ROWS, len(df))
    add("no duplicate feedback_id", not df["feedback_id"].duplicated().any(), int(df["feedback_id"].duplicated().sum()))
    add("no fully duplicated rows", not df.duplicated().any(), int(df.duplicated().sum()))
    add("customer_id format CUST-####", df["customer_id"].astype(str).str.match(r"^CUST-\d{4}$").all())
    add("all customer_ids exist in customer master", df["customer_id"].isin(customers["customer_id"]).all(),
        int((~df["customer_id"].isin(customers["customer_id"])).sum()))
    m = df.merge(customers, on="customer_id", how="left", suffixes=("", "_c"))
    add("plan matches customer master", (m["subscription_plan"].astype(str).str.strip().str.lower()
                                         == m["subscription_plan_c"].str.lower()).all())
    add("segment matches customer master", (m["customer_segment"].astype(str).str.strip().str.lower()
                                            == m["customer_segment_c"].str.lower()).all())
    d = pd.to_datetime(df["submission_date"], errors="coerce", format="mixed") if stage == "raw" else df["submission_date"]
    add("all dates parseable", d.notna().all(), int(d.isna().sum()))
    add("dates within 2025-10-01..2026-09-30", d.between("2025-10-01", "2026-09-30").all())
    add("dates not before customer signup", (d.reset_index(drop=True) >= pd.to_datetime(m["signup_date"])).all())
    add("no missing feedback_text", df["feedback_text"].notna().all() and (df["feedback_text"].astype(str).str.len() > 10).all())
    for col, allowed in CANON.items():
        vals = df[col].dropna().astype(str)
        extra = set(vals) - set(allowed) - ({"Unknown"} if col == "customer_impact" and stage == "clean" else set())
        add(f"{col}: only valid values", not extra, f"invalid={sorted(extra)[:5]}")
        if col != "customer_impact":
            add(f"{col}: no missing", df[col].notna().all(), int(df[col].isna().sum()))
    add("unique feedback_text share >= 95%", df["feedback_text"].nunique() / len(df) >= .95,
        f"{df['feedback_text'].nunique() / len(df):.1%}")
    if stage == "clean":
        cat_area = df.groupby("issue_theme")[["feature_area", "feedback_category"]].nunique().max().max()
        add("each theme maps to 1 area and 1 category", cat_area == 1)
        add("every record tagged to exactly one theme", df["issue_theme"].notna().all(), int(df["issue_theme"].isna().sum()))
    return r


def main():
    cust = pd.read_csv(RAW / "customers.csv", dtype=str)
    raw = pd.read_csv(RAW / "feedback_raw.csv", dtype=str)
    clean = pd.read_csv(PROC / "feedback_clean.csv", dtype=str, parse_dates=["submission_date"])
    res = {"raw": run_checks(raw, cust, "raw"), "clean": run_checks(clean, cust, "clean")}
    log = json.loads((PROC / "cleaning_log.json").read_text())
    lines = ["# Data Quality Report", "", "> All data is **SYNTHETIC** (randomly generated, fixed seed).", "",
             "Produced by `scripts/validate_data.py`. Raw checks are expected to flag formatting noise that was "
             "injected on purpose; cleaned-data checks must all pass.", ""]
    for stage in ("raw", "clean"):
        lines += [f"## {stage.title()} data checks", "", "| Check | Result | Detail |", "|---|---|---|"]
        lines += [f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n, ok, d in res[stage]]
        lines += [f"", f"**{sum(o for _, o, _ in res[stage])}/{len(res[stage])} passed.**", ""]
    lines += ["## Cleaning actions", "", "```json", json.dumps(log, indent=2), "```", ""]
    REP.mkdir(exist_ok=True)
    (REP / "data_quality_report.md").write_text("\n".join(lines))
    failed = [n for n, ok, _ in res["clean"] if not ok]
    print("raw failures (expected, noise):", [n for n, ok, _ in res["raw"] if not ok])
    print("clean failures:", failed)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
