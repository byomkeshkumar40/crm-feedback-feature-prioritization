"""Generate the SYNTHETIC CRM feedback dataset (1,500 records, 420 accounts).

All data is fictional and randomly generated with a fixed seed. No real customer
data is used. A small amount of formatting noise is injected into the raw file
(whitespace, casing, alternate date format, a few blanks) so that clean_data.py
has something realistic to fix; no rows are duplicated or dropped.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from themes import T, THEME_ORDER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEED = 20260930
N_RECORDS = 1500
N_CUSTOMERS = 420
START, END = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-30")
PLANS = ["Starter", "Professional", "Enterprise"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
SOURCES = ["Support Ticket", "Customer Survey", "Feature Request", "In-App Feedback"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
IMPACTS = ["Minor Inconvenience", "Workflow Slowdown", "Blocks Key Task", "Revenue/Operations Risk"]

SOURCE_BY_CAT = {  # P(source | category) in SOURCES order
    "Bug": [.62, .08, .02, .28], "Feature Request": [.08, .27, .50, .15],
    "Usability Issue": [.25, .35, .05, .35], "Performance Issue": [.45, .15, .02, .38],
    "Integration Issue": [.60, .12, .03, .25]}
SENT_BY_CAT = {  # Negative, Neutral, Positive
    "Bug": [.74, .22, .04], "Feature Request": [.12, .58, .30], "Usability Issue": [.50, .38, .12],
    "Performance Issue": [.68, .27, .05], "Integration Issue": [.66, .28, .06]}
SEV_BY_CAT = {"Bug": [.20, .38, .27, .15], "Feature Request": [.55, .33, .10, .02],
              "Usability Issue": [.40, .40, .17, .03], "Performance Issue": [.22, .40, .28, .10],
              "Integration Issue": [.18, .38, .30, .14]}
SEV_PLAN = {"Starter": [1.1, 1, .9, .8], "Professional": [1, 1, 1, 1], "Enterprise": [.85, 1, 1.2, 1.4]}
SEV_POS = [1.6, 1, .5, .2]
IMPACT_BY_SEV = {"Low": [.70, .26, .04, 0], "Medium": [.25, .50, .22, .03],
                 "High": [.05, .27, .53, .15], "Critical": [0, .08, .42, .50]}

OPEN = {"Negative": ["Frustrated with this one.", "This has been a recurring problem for us.",
                     "Raising this again after our last business review.", "Our team keeps running into this.",
                     "Escalating on behalf of our ops lead.", "Not what we expected for the price.", "", "", ""],
        "Neutral": ["Quick note from our admin.", "Feedback from our monthly review.", "Sharing this from our team.",
                    "FYI for the product team.", "Noting this during onboarding.", "", "", ""],
        "Positive": ["Overall we like the product.", "Great support experience recently.",
                     "Happy with most of the product.", "Recent updates have been a nice improvement.", "", ""]}
ROLES = ["sales manager", "RevOps lead", "admin", "customer success lead", "marketing ops owner", "finance analyst"]
PROCS = ["quarterly planning", "month-end reporting", "lead handoff", "renewal", "onboarding", "weekly pipeline review"]
DETAIL = ["It happens about {n} times a week for our team of {m}.",
          "We estimate we lose roughly {h} hours a month on this.",
          "Our {role} flagged it while onboarding {m} new users.",
          "So far {m} people on our side have reported it.",
          "It affects our {proc} process every cycle.", "", ""]
CLOSE = {"Negative": ["Please look into it soon.", "We need a fix before renewal.", "Is there a workaround?",
                      "Support suggested logging it here.", "", ""],
         "Neutral": ["Let us know if you need examples.", "Happy to join a feedback call.", "", ""],
         "Positive": ["Thanks to the team.", "Keep up the good work.", "Happy to beta test.", "", ""]}


def build_customers(rng):
    plan = rng.choice(PLANS, N_CUSTOMERS, p=[.45, .38, .17])
    seg_p = {"Starter": [.80, .18, .02], "Professional": [.30, .60, .10], "Enterprise": [.02, .28, .70]}
    seg = [rng.choice(SEGMENTS, p=seg_p[p]) for p in plan]
    lo_hi = {"Starter": (3, 15), "Professional": (10, 80), "Enterprise": (50, 600)}
    seats = [int(rng.integers(*lo_hi[p])) for p in plan]
    industries = rng.choice(["Software", "Healthcare", "Manufacturing", "Retail", "Financial Services",
                             "Education", "Logistics", "Professional Services"], N_CUSTOMERS)
    signup = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 1004, N_CUSTOMERS), unit="D")
    return pd.DataFrame({"customer_id": [f"CUST-{i:04d}" for i in range(1, N_CUSTOMERS + 1)],
                         "subscription_plan": plan, "customer_segment": seg, "seats": seats,
                         "industry": industries, "signup_date": signup.strftime("%Y-%m-%d")})


def day_weights(tid):
    days = pd.date_range(START, END)
    w = 1 + 0.5 * np.arange(len(days)) / len(days)  # gradual growth in feedback volume
    # Documented synthetic release incidents (disclosed in README)
    if tid == "wf_fail":
        w = w * np.where((days >= "2026-02-10") & (days <= "2026-03-03"), 4.0, 1.0)
    if tid == "ui_perf":
        w = w * np.where((days >= "2026-06-01") & (days <= "2026-06-28"), 3.0, 1.0)
    return days, w / w.sum()


def make_text(rng, tid, sentiment):
    th = T[tid]
    key = th["keys"][rng.integers(len(th["keys"]))]
    core = th["cores"][rng.integers(len(th["cores"]))].format(k=key)
    core = core[0].upper() + core[1:]
    pick = lambda lst: lst[rng.integers(len(lst))]  # noqa: E731
    det = pick(DETAIL).format(n=int(rng.integers(2, 40)), m=int(rng.integers(3, 120)),
                              h=int(rng.integers(3, 60)), role=pick(ROLES), proc=pick(PROCS))
    parts = [pick(OPEN[sentiment]), core, det, pick(CLOSE[sentiment])]
    return " ".join(p for p in parts if p)


def generate(with_truth=False, seed=SEED):
    rng = np.random.default_rng(seed)
    cust = build_customers(rng)
    w_c = rng.gamma(1.1, 1.0, N_CUSTOMERS) * cust["subscription_plan"].map(
        {"Starter": 0.9, "Professional": 1.0, "Enterprise": 1.4}).to_numpy()
    cids = rng.choice(N_CUSTOMERS, N_RECORDS, p=w_c / w_c.sum())
    rows = []
    for i, ci in enumerate(cids):
        c = cust.iloc[ci]
        pm = {"Starter": 0, "Professional": 1, "Enterprise": 2}[c.subscription_plan]
        tw = np.array([T[t]["weight"] * T[t]["mult"][pm] for t in THEME_ORDER])
        tid = THEME_ORDER[rng.choice(len(tw), p=tw / tw.sum())]
        th = T[tid]
        days, dw = day_weights(tid)
        date = days[rng.choice(len(days), p=dw)]
        cat = th["category"]
        source = rng.choice(SOURCES, p=SOURCE_BY_CAT[cat])
        sent = rng.choice(["Negative", "Neutral", "Positive"], p=SENT_BY_CAT[cat])
        sp = np.array(SEV_BY_CAT[cat]) * SEV_PLAN[c.subscription_plan]
        if sent == "Positive":
            sp = sp * SEV_POS
        sev = rng.choice(SEVERITIES, p=sp / sp.sum())
        impact = rng.choice(IMPACTS, p=IMPACT_BY_SEV[sev])
        rows.append(dict(feedback_id="", customer_id=c.customer_id,
                         submission_date=date.strftime("%Y-%m-%d"), feedback_source=source,
                         subscription_plan=c.subscription_plan, customer_segment=c.customer_segment,
                         feature_area=th["area"], feedback_category=cat,
                         feedback_text=make_text(rng, tid, sent), sentiment=sent, severity=sev,
                         customer_impact=impact, _theme=tid))
    df = pd.DataFrame(rows).sort_values("submission_date", kind="stable").reset_index(drop=True)
    df["feedback_id"] = [f"FB-{i + 1:05d}" for i in range(len(df))]  # IDs follow chronological order
    return (df, cust) if with_truth else (df.drop(columns="_theme"), cust)


def inject_noise(df, seed=SEED + 1):
    """Realistic formatting noise for the raw extract. Does not add/remove rows."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    for col in ["feedback_source", "subscription_plan", "customer_segment", "feature_area",
                "feedback_category", "sentiment", "severity"]:
        idx = rng.choice(len(out), int(0.02 * len(out)), replace=False)
        for j, ix in enumerate(idx):
            v = out.at[ix, col]
            out.at[ix, col] = [f" {v}", f"{v} ", v.lower(), v.upper()][j % 4]
    idx = rng.choice(len(out), int(0.03 * len(out)), replace=False)
    out.loc[idx, "submission_date"] = pd.to_datetime(out.loc[idx, "submission_date"]).dt.strftime("%d-%b-%Y")
    out.loc[rng.choice(len(out), 12, replace=False), "customer_impact"] = np.nan
    return out


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    df, cust = generate()
    inject_noise(df).to_csv(RAW / "feedback_raw.csv", index=False)
    cust.to_csv(RAW / "customers.csv", index=False)
    (RAW / "README_SYNTHETIC.txt").write_text(
        "ALL DATA IN THIS PROJECT IS SYNTHETIC (randomly generated, fixed seed). "
        "No real customers, companies or feedback are represented.\n")
    print(f"Wrote {len(df)} feedback rows and {len(cust)} customers to {RAW}")


if __name__ == "__main__":
    main()
