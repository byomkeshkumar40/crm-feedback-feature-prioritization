"""RICE prioritisation on SYNTHETIC feedback with documented assumptions and sensitivity analysis.

OBSERVED (computed from data): supporting feedback count, unique reporting accounts,
share of High/Critical severity, share of blocking customer_impact, source/plan coverage.
ESTIMATES (assumptions): reporting multiplier, Impact scale mapping, Confidence rule, Effort (person-months),
tech-risk penalty. RICE scores are decision aids, not objective facts.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
ASSUME = ROOT / "data" / "assumptions" / "feature_assumptions.csv"
OUT = PROC / "rice"

WINDOW = "2025-10-01 to 2026-09-30 (12 months)"
BASE = dict(reporting_multiplier=2.5, reach_cap=None, impact_mode="combined", confidence_mode="rule", effort="base")
IMPACT_STEPS = [(0.55, 3.0), (0.40, 2.0), (0.25, 1.0), (0.12, 0.5), (0.0, 0.25)]


def impact_from_signal(x):
    for thr, val in IMPACT_STEPS:
        if x >= thr:
            return val


def confidence_rule(n, sources, plans):
    pts = 0.5 + 0.1 * (n >= 50) + 0.1 * (n >= 100) + 0.1 * (n >= 150) + 0.1 * (sources == 4) + 0.1 * (plans == 3)
    return round(min(pts, 1.0), 2)


def evidence_table(df, assume):
    rows = []
    for _, a in assume.iterrows():
        themes = a.themes.split("|")
        sub = df[df.issue_theme.isin(themes)]
        sev = sub.severity.isin(["High", "Critical"])
        blk = sub.customer_impact.isin(["Blocks Key Task", "Revenue/Operations Risk"])
        rows.append(dict(
            feature_id=a.feature_id, supporting_feedback_count=len(sub),
            unique_affected_customers=int(sub.customer_id.nunique()),
            high_critical_pct=sev.mean(), blocking_pct=blk.mean(), combined_signal=(sev | blk).mean(),
            n_sources=sub.feedback_source.nunique(), n_plans=sub.subscription_plan.nunique(),
            negative_pct=(sub.sentiment == "Negative").mean(),
            categories="; ".join(sorted(sub.feedback_category.unique())),
            feature_areas="; ".join(sorted(sub.feature_area.unique()))))
    return pd.DataFrame(rows)


def score(assume, ev, n_accounts, p):
    t = assume.merge(ev, on="feature_id")
    cap = p["reach_cap"] or n_accounts
    t["reach"] = np.minimum(cap, np.floor(t.unique_affected_customers * p["reporting_multiplier"] + 0.5)).astype(int)
    sig = t.combined_signal if p["impact_mode"] == "combined" else t.high_critical_pct
    t["impact"] = sig.map(impact_from_signal)
    conf = [confidence_rule(n, s, pl) for n, s, pl in zip(t.supporting_feedback_count, t.n_sources, t.n_plans)]
    t["confidence"] = (np.array(conf) - t.tech_risk_penalty).round(2) if p["confidence_mode"] == "rule" else 0.8
    t["effort"] = t[{"base": "effort_base_pm", "low": "effort_low_pm", "high": "effort_high_pm"}[p["effort"]]]
    t["rice_score"] = (t.reach * t.impact * t.confidence / t.effort).round(2)
    t["priority_rank"] = t.rice_score.rank(ascending=False, method="min").astype(int)
    return t.sort_values(["priority_rank", "feature_id"]).reset_index(drop=True)


def recommendation(rank):
    return ("Build now (next planning cycle)" if rank <= 3 else "Plan next (validate scope)" if rank <= 6
            else "Investigate / discovery first" if rank <= 9 else "Defer; monitor feedback")


def rationale(r):
    return (f"Impact {r.impact}: {r.combined_signal:.0%} of supporting records are High/Critical severity or "
            f"blocking/risk impact (thresholds: >=55%->3, >=40%->2, >=25%->1, >=12%->0.5, else 0.25). "
            f"Confidence {r.confidence:.2f}: {r.supporting_feedback_count} records, {r.n_sources}/4 sources, "
            f"{r.n_plans}/3 plans (rule: 0.5 base +0.1 per evidence criterion) minus tech-risk penalty {r.tech_risk_penalty}. "
            f"Reach {r.reach}: {r.unique_affected_customers} reporting accounts x 2.5 reporting multiplier, "
            f"capped at the 420-account base. Effort {r.effort} person-months: {r.effort_rationale}")


SCENARIOS = {
    "Base case": {},
    "Reporting multiplier 1.5": dict(reporting_multiplier=1.5),
    "Reporting multiplier 4.0": dict(reporting_multiplier=4.0),
    "Reach capped at 250 accounts": dict(reach_cap=250),
    "Impact from High/Critical severity only": dict(impact_mode="severity"),
    "Confidence flat 0.8": dict(confidence_mode="flat"),
    "Optimistic effort (low estimates)": dict(effort="low"),
    "Pessimistic effort (high estimates)": dict(effort="high"),
}


def run():
    df = pd.read_csv(PROC / "feedback_clean.csv", parse_dates=["submission_date"])
    assume = pd.read_csv(ASSUME)
    n_acc = len(pd.read_csv(RAW / "customers.csv"))
    ev = evidence_table(df, assume)
    base = score(assume, ev, n_acc, BASE)
    base["recommendation"] = base.priority_rank.map(recommendation)
    base["estimate_rationale"] = base.apply(rationale, axis=1)
    ranks = pd.DataFrame({"feature_id": base.feature_id, "feature_name": base.feature_name}).set_index("feature_id")
    scores = pd.DataFrame(index=ranks.index)
    for name, ov in SCENARIOS.items():
        s = score(assume, ev, n_acc, {**BASE, **ov}).set_index("feature_id")
        ranks[name], scores[name] = s.priority_rank, s.rice_score
    ranks["rank_min"] = ranks[list(SCENARIOS)].min(axis=1)
    ranks["rank_max"] = ranks[list(SCENARIOS)].max(axis=1)
    # Monte Carlo: +/-30% uniform noise on Reach, Impact, Confidence, Effort
    rng = np.random.default_rng(7)
    b = base.set_index("feature_id").loc[ranks.index]
    N = 5000
    noise = lambda: rng.uniform(0.7, 1.3, (N, len(b)))  # noqa: E731
    sim = (b.reach.values * noise()) * (b.impact.values * noise()) * np.minimum(1, b.confidence.values * noise()) / (b.effort.values * noise())
    sim_rank = (-sim).argsort(axis=1).argsort(axis=1) + 1
    stab = pd.DataFrame({"feature_name": b.feature_name, "base_rank": b.priority_rank,
                         "median_rank": np.median(sim_rank, axis=0), "p10_rank": np.percentile(sim_rank, 10, axis=0),
                         "p90_rank": np.percentile(sim_rank, 90, axis=0),
                         "prob_top3_pct": (sim_rank <= 3).mean(axis=0) * 100,
                         "prob_rank1_pct": (sim_rank == 1).mean(axis=0) * 100}, index=b.index).round(1)
    stab = stab.sort_values("base_rank")
    unmapped = sorted(set(df.issue_theme.unique()) - set("|".join(assume.themes).split("|")))
    meta = dict(window=WINDOW, accounts=n_acc, mapped_records=int(df.issue_theme.isin("|".join(assume.themes).split("|")).sum()),
                unmapped_themes=unmapped, unmapped_records=int(df.issue_theme.isin(unmapped).sum()), mc_trials=N)
    return base, ranks, scores, stab, meta


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base, ranks, scores, stab, meta = run()
    base.to_csv(OUT / "rice_scores.csv", index=False)
    ranks.to_csv(OUT / "sensitivity_ranks.csv")
    scores.to_csv(OUT / "sensitivity_scores.csv")
    stab.to_csv(OUT / "rank_stability.csv")
    (OUT / "rice_meta.json").write_text(json.dumps(meta, indent=2))
    pd.set_option("display.width", 250)
    print(base[["priority_rank", "feature_id", "feature_name", "supporting_feedback_count", "unique_affected_customers",
                "reach", "impact", "confidence", "effort", "rice_score", "recommendation"]].to_string(index=False))
    print(); print(ranks.drop(columns="feature_name").to_string())
    print(); print(stab.to_string()); print(meta)


if __name__ == "__main__":
    main()
