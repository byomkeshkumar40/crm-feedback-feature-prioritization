"""Generate markdown reports from computed results (SYNTHETIC data). Numbers are never typed by hand."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_feedback import analyse  # noqa: E402
from calculate_rice import run as run_rice  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
PRD_FEATURE = "F03"  # the PRD prose below is written for this feature; build fails if RICE rank 1 changes

SYN = "> **SYNTHETIC DATA.** Every record is randomly generated for a fictional CRM company. Nothing here describes real customers or products.\n"


def md(df, floatfmt=None):
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(f"{v:g}" if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(out)


def main():
    df, res, tabs = analyse()
    base, ranks, scores, stab, meta = run_rice()
    top = base.iloc[0]
    assert top.feature_id == PRD_FEATURE, f"RICE rank 1 is now {top.feature_id}; rewrite the PRD section for it"
    n = len(df)
    A, S = tabs["by_feature_area"], tabs["by_segment"]
    P = tabs["by_plan"]
    comp, req = tabs["top_complaints"], tabs["top_requests"]
    spread = ranks.rank_max - ranks.rank_min
    sent_plan = tabs["sentiment_by_plan_pct"]
    hs = tabs["high_sev_by_area"]
    sub = df[df.issue_theme == "contact_import"]
    imp_plan = sub.groupby("subscription_plan").agg(records=("feedback_id", "count"), accounts=("customer_id", "nunique"))
    imp_src = sub.feedback_source.value_counts()
    imp_sev = sub.severity.value_counts()
    acc_plan = P.accounts_in_base
    imp_plan["pct_of_plan_accounts"] = (imp_plan.accounts / acc_plan * 100).round(1)
    nr = ranks.loc[PRD_FEATURE]
    assert nr.rank_min == nr.rank_max == 1, "resume bullet wording assumes rank 1 in every scenario"
    mc = stab.loc[PRD_FEATURE]

    # ---------------- product_insights.md ----------------
    ins = f"""# Product Insights Report
{SYN}
Period analysed: {res['period'][0]} to {res['period'][1]} · {n:,} feedback records · {res['unique_customers']} of {res['customer_master_accounts']} accounts ({res['pct_accounts_with_feedback']}%) submitted at least one item.

Legend: **[OBSERVED]** = computed directly from the synthetic data · **[INTERPRETATION]** = analytical reading of the numbers · **[HYPOTHESIS]** = product idea to validate, not a finding.

## 1. Top customer problems
**[OBSERVED]** Most-reported complaint themes (complaints = all categories except Feature Request):

{md(comp.reset_index(drop=True)[['theme','feature_area','category','feedback_records','unique_customers','negative_pct','high_critical_pct']])}

**[INTERPRETATION]** The three largest complaint themes — {comp.theme.iloc[0]}, {comp.theme.iloc[1]}, {comp.theme.iloc[2]} — are reliability problems (imports, automations, sync), not missing capabilities. Counts are feedback *volume*; the unique-customer column is the better indicator of breadth.

## 2. Most affected feature areas
**[OBSERVED]**

{md(A.reset_index()[['feature_area','feedback_records','unique_customers','pct_of_records']])}

High/Critical severity by area:

{md(hs.reset_index())}

**[INTERPRETATION]** Volume is spread fairly evenly across areas ({A.pct_of_records.min()}%–{A.pct_of_records.max()}% each); {A.index[0]} is largest. By High/Critical share, {hs.share_of_area_records_pct.idxmax()} is highest ({hs.share_of_area_records_pct.max()}%) and {hs.share_of_area_records_pct.idxmin()} lowest ({hs.share_of_area_records_pct.min()}%).

## 3. Differences across plans and segments
**[OBSERVED]** Accounts in the base are the only known denominator (customer master of {res['customer_master_accounts']} accounts).

{md(P.reset_index()[['subscription_plan','feedback_records','accounts_in_base','records_per_account','unique_customers','pct_of_accounts_reporting']])}

{md(S.reset_index()[['customer_segment','feedback_records','accounts_in_base','records_per_account','unique_customers','pct_of_accounts_reporting']])}

**[INTERPRETATION]** Professional has the most records, but that mainly reflects having the most accounts. Per account, Enterprise submits the most ({P.loc['Enterprise','records_per_account']} records/account vs {P.loc['Starter','records_per_account']} for Starter). The share of accounts that reported at least once is similar across plans ({P.pct_of_accounts_reporting.min()}%–{P.pct_of_accounts_reporting.max()}%). Do not read raw volume as prevalence.

## 4. Sentiment patterns
**[OBSERVED]** Overall: {res['pct_negative']}% negative. By plan (% of that plan's records):

{md(sent_plan.reset_index())}

**[INTERPRETATION]** Enterprise has the lowest negative share ({sent_plan.loc['Enterprise','Negative']}%) — but the generator gives Enterprise a different issue mix (more feature requests, which skew neutral/positive), so this is a **mix effect, not evidence Enterprise customers are happier**. Compare sentiment within the same category before drawing conclusions.

## 5. Most requested features
**[OBSERVED]**

{md(req.reset_index(drop=True)[['theme','feature_area','feedback_records','unique_customers','high_critical_pct']])}

## 6. Highest-priority opportunities (RICE)
**[OBSERVED + ESTIMATES]** RICE inputs combine observed evidence (records, accounts, severity) with analyst estimates (Impact tiers, Confidence rule, Effort). Window: {meta['window']}.

{md(base[['priority_rank','feature_id','feature_name','reach','impact','confidence','effort','rice_score','recommendation']].round(2))}

Sensitivity: across {len(ranks.columns) - 3} alternative-assumption scenarios, rank movement per feature ranged from {spread.min()} to {spread.max()} places. {top.feature_name} ({top.feature_id}) had best/worst rank {nr.rank_min}/{nr.rank_max} across scenarios. In {meta['mc_trials']:,} Monte Carlo trials (±30% on every input) it ranked #1 in {mc.prob_rank1_pct}% and top-3 in {mc.prob_top3_pct}% of trials.

**[INTERPRETATION]** Top-ranked items are small-to-medium reliability fixes with high severity; large builds (Mobile App, Native Integrations) rank low mainly because of effort and lower severity signals, which is a property of the Impact rule (severity-based) — it under-values strategic feature requests.

## 7. Product recommendations (all **[HYPOTHESIS]**)
1. Start with **{base.feature_name.iloc[0]}**, then **{base.feature_name.iloc[1]}** and **{base.feature_name.iloc[2]}**; validate effort estimates with engineering first.
2. Run discovery (not build) for ranks 7–9 and keep ranks 10–12 on a watch list, re-scoring when new feedback arrives.
3. Track unique reporting accounts per theme monthly, not just ticket counts.
4. Re-estimate Impact for feature requests with customer interviews; severity alone understates their value.

## 8. Assumptions and limitations
- Data is synthetic; patterns reflect the generator's design (plan-level theme weights, a workflow-failure spike Feb 10 – Mar 3 2026 and a UI-lag spike June 2026). They show the *method*, not real customer behaviour.
- The issue-theme tagger uses the same key phrases the generator writes, so its 100% coverage is not evidence of real-world NLP accuracy.
- {meta['unmapped_records']} records ({meta['unmapped_records'] / n:.1%}) belong to themes not carried into RICE ({', '.join(meta['unmapped_themes'])}).
- Reach uses a 2.5× reporting multiplier (estimate) capped at the {meta['accounts']}-account base. Impact, Confidence, Effort are estimates. RICE ranks are decision aids, not facts.
- Single 12-month window; no revenue, churn or support-cost data, so business impact is not measured.
"""
    (REP / "product_insights.md").write_text(ins)

    # ---------------- feature_prioritization.md ----------------
    fp = f"""# Feature Prioritization (RICE)
{SYN}
RICE = Reach × Impact × Confidence ÷ Effort. All scores are computed by `scripts/calculate_rice.py` from `data/assumptions/feature_assumptions.csv` and the cleaned feedback.

## Observed vs estimated
| Input | Type | How it is set |
|---|---|---|
| Supporting feedback count, unique affected customers | **Observed** | Records / accounts tagged to the feature's themes |
| Reach | **Estimate built on observed data** | Unique reporting accounts × reporting multiplier (assumed 2.5), rounded half-up, capped at the {meta['accounts']}-account base. Time window: {meta['window']} |
| Impact (0.25–3) | **Estimate** | Share of supporting records that are High/Critical severity *or* blocking/risk impact: ≥55%→3, ≥40%→2, ≥25%→1, ≥12%→0.5, else 0.25 |
| Confidence | **Estimate** | 0.5 + 0.1 for each of: ≥50, ≥100, ≥150 records; all 4 sources; all 3 plans; minus an analyst tech-risk penalty (0–0.1) |
| Effort (person-months) | **Estimate** | Analyst judgement per feature, with low/base/high range (see assumptions file) |

## Results
{md(base[['priority_rank','feature_id','feature_name','supporting_feedback_count','unique_affected_customers','reach','impact','confidence','effort','rice_score','recommendation']].round(2))}

Per-feature rationale is in the `estimate_rationale` column of `data/processed/rice/rice_scores.csv` and in the Excel "RICE Calculations" sheet.

## Sensitivity analysis — rank under alternative assumptions
{md(ranks.reset_index().drop(columns=['feature_name']).rename(columns={'rank_min':'best','rank_max':'worst'}))}

## Monte Carlo rank stability ({meta['mc_trials']:,} trials, ±30% uniform noise on R, I, C, E)
{md(stab.reset_index())}

## Reading this honestly
- Rank-1 feature {base.feature_id.iloc[0]} holds rank {ranks.loc[base.feature_id.iloc[0],'rank_min']}–{ranks.loc[base.feature_id.iloc[0],'rank_max']} across all scenarios; rank-2 feature {base.feature_id.iloc[1]} holds {ranks.loc[base.feature_id.iloc[1],'rank_min']}–{ranks.loc[base.feature_id.iloc[1],'rank_max']}; other positions move by up to {spread.max()} places depending on assumptions.
- RICE is a structured conversation aid. Impact here is severity-based, so it favours bug-fix reliability work over strategic requests.
- {meta['unmapped_records']} records in themes not evaluated ({', '.join(meta['unmapped_themes'])}) are outside this round.
"""
    (REP / "feature_prioritization.md").write_text(fp)

    # ---------------- PRD ----------------
    ev = top
    prd = f"""# Product Requirements Document — Reliable CSV Import with Validation
{SYN}
| | |
|---|---|
| Status | **Draft proposal — not implemented, no outcome claimed** |
| Source analysis | RICE rank **#{ev.priority_rank}** (score {ev.rice_score:g}) of 12 opportunities; `reports/feature_prioritization.md` |
| Author | Product Analyst (portfolio project) |

## 1. Product Overview
Improve the contact import experience so that customers can bring spreadsheet data into the CRM with a pre-import check, remembered field mappings, and a downloadable row-level error report, instead of failing midway with a generic error.

## 2. Problem Statement
Customers report that contact CSV imports fail, scramble phone/email columns, silently skip rows, or reject files with accented characters. They find out late and cannot see which rows failed, so they clean data by hand or re-run the import.

## 3. Background and Evidence (all from the synthetic dataset)
- **{ev.supporting_feedback_count} feedback records** from **{ev.unique_affected_customers} unique accounts** ({ev.unique_affected_customers / meta['accounts']:.1%} of the {meta['accounts']}-account base) — the largest complaint theme in the dataset.
- {ev.negative_pct:.1%} negative; {ev.high_critical_pct:.1%} High/Critical severity; {ev.blocking_pct:.1%} blocking a key task or creating operations risk.
- Severity mix: {', '.join(f'{k} {v}' for k, v in imp_sev.items())}. Sources: {', '.join(f'{k} {v}' for k, v in imp_src.items())}.
- By plan (accounts reporting import issues / accounts on that plan):

{md(imp_plan.reset_index())}

- RICE: Reach {ev.reach}, Impact {ev.impact}, Confidence {ev.confidence}, Effort {ev.effort} person-months (all estimates; see `feature_prioritization.md`). Rank {nr.rank_min}–{nr.rank_max} across scenarios; #1 in {mc.prob_rank1_pct}% of Monte Carlo trials.
- *Caveat:* counts are feedback volume; the true share of customers who import data is unknown.

## 4. Target Users
Primary: CRM admins and sales-operations users who load contacts in bulk (onboarding, list purchases, event leads). Secondary: reps importing small lists; customer-success staff assisting migrations.

## 5. User Personas
- **Priya, RevOps Admin (Professional, Mid-Market):** imports 2–5k contacts monthly from marketing tools; needs confidence the data landed correctly.
- **Marcus, Founder/Office Manager (Starter, SMB):** imports a spreadsheet once at setup; has no data tooling; needs plain-language errors.
- **Elena, Enterprise Sales Ops:** migrates large regional lists with accented names; needs repeatable mappings and an audit trail.

## 6. Product Goals
1. Customers know before importing whether a file will succeed.
2. Failed rows are visible, downloadable and fixable without support.
3. Imports preserve field mapping and special characters.

## 7. Non-Goals
- Not a general ETL/integration platform; no scheduled or API-based imports in this release.
- Not duplicate detection/merge (separate opportunity F01).
- Not changing export behaviour.

## 8. User Stories
1. As an admin, I want a preview and validation before importing so I can fix problems up front.
2. As an admin, I want my column mapping remembered so repeat imports need no rework.
3. As a rep, I want an error report listing each failed row and reason so I can correct and re-upload only those rows.
4. As an enterprise user, I want names with accents and non-Latin characters imported intact.
5. As support, I want an import log per job so I can diagnose without asking for the file.

## 9. Functional Requirements
- FR1 Upload CSV (UTF-8, UTF-8 BOM, Latin-1 auto-detect) up to a stated row limit.
- FR2 Auto-suggest column mapping from headers; user can edit; mapping saved per user/workspace.
- FR3 Pre-import validation: required fields, email/phone format, duplicate rows within file, invalid dates; summary of counts by issue type.
- FR4 Import runs as a background job with progress and completion notification.
- FR5 Row-level result: imported / skipped / failed with reason; downloadable CSV of failed rows.
- FR6 Never skip a row silently; every row has a recorded outcome.
- FR7 Partial-failure policy: valid rows import; user may choose "stop on first error" instead.
- FR8 Import history page with job log retained for 90 days.

## 10. Non-Functional Requirements
- Performance: validate 10k rows in ≤30 s; import 10k rows in ≤5 min (targets to confirm with engineering).
- Reliability: job is resumable/idempotent; retry-safe.
- Security/privacy: files encrypted at rest, deleted after 30 days; role-based access to import history.
- Accessibility: WCAG 2.1 AA for the import wizard.
- Observability: metrics and error codes logged per job.

## 11. Acceptance Criteria
- Given a 5,000-row file with 50 invalid emails, validation lists exactly 50 flagged rows before import starts.
- Given a mapping saved earlier, a second import with the same headers pre-fills the mapping with no manual action.
- After import, imported + skipped + failed == rows in file (100% reconciliation).
- Names containing "é", "ñ", "ü" appear unchanged in imported records.
- A failed-row CSV can be re-uploaded and imports successfully once corrected.

## 12. User Workflow
Upload file → review auto-mapping → run validation → review issue summary (fix file or proceed) → confirm import → progress/notification → results page (counts, failed-row download) → import history.

## 13. Success Metrics
Baselines do not exist in the synthetic data; they must be measured before launch. Targets are **proposals**.
| Metric | Baseline | Target (proposal) |
|---|---|---|
| Import-related feedback records per month | {len(sub) / 12:.1f}/month in synthetic data (12-month avg) | −50% within 90 days of GA |
| Unique accounts reporting import issues per quarter | {ev.unique_affected_customers / 4:.0f} (annualised ÷ 4, rough) | −40% |
| First-attempt import success rate | to be instrumented | ≥95% of jobs with no failed rows after validation fixes |
| Share of imports using saved mapping | 0% | ≥40% of repeat imports |
| Support contacts per 100 imports | to be instrumented | −50% |
Guardrails: median import completion time not worse than current; no increase in data-loss reports.

## 14. Dependencies
Background job infrastructure; file storage; notification service; design for the import wizard; support tooling for import logs; legal/privacy review for file retention.

## 15. Risks and Assumptions
- Assumption: import is a frequent workflow; verify with product telemetry.
- Assumption: effort {ev.effort} person-months (range {int(base.loc[base.feature_id==PRD_FEATURE,'effort_low_pm'].iloc[0]*10)/10:g}–{base.loc[base.feature_id==PRD_FEATURE,'effort_high_pm'].iloc[0]:g}) is an analyst estimate pending engineering review.
- Risk: encoding edge cases; very large files; customer data variability.
- Risk: synthetic data may overstate or understate real import pain; validate with real tickets and interviews.

## 16. Open Questions
1. What is the row limit and file-size limit per plan?
2. Should Starter get the same validation depth as Enterprise?
3. Do customers need XLSX support in v1?
4. How long should failed-row files and logs be retained?
5. Which existing tickets best represent import failures for a real baseline?

## 17. Rollout Plan
1. Discovery (1–2 weeks): review real import tickets, interview 5–8 admins, confirm effort.
2. Internal alpha: validation + error report behind a flag.
3. Beta (10–20 opted-in accounts across all plans), track metrics above.
4. GA with in-app announcement and help-centre guide; monitor guardrails for 30 days.
5. Review at 90 days against success metrics; decide on follow-ups (XLSX, scheduled imports).
"""
    (REP / "product_requirements_document.md").write_text(prd)

    # ---------------- resume bullets ----------------
    pm = df[df.feedback_category != "Feature Request"]
    bl = f"""# Resume Bullets (all figures computed from the SYNTHETIC project data)

- Analyzed 1,500 synthetic CRM feedback records from {res['unique_customers']} accounts with Python/Pandas, separating feedback volume from unique affected customers and identifying {comp.theme.iloc[0].lower()} ({int(comp.feedback_records.iloc[0])} records, {int(comp.unique_customers.iloc[0])} accounts) as the top complaint theme.
- Built a RICE prioritization model for 12 CRM feature opportunities with documented estimates, scenario analysis ({len(ranks.columns) - 3} scenarios) and a {meta['mc_trials']:,}-trial Monte Carlo test; the top-ranked feature held rank #{nr.rank_min} in every scenario.
- Wrote a 17-section PRD for the top-ranked feature (reliable CSV import) with user stories, acceptance criteria and measurable success metrics, and delivered an Excel workbook and 3-page Streamlit dashboard on the same analysis.
"""
    (REP / "resume_bullets.md").write_text(bl)
    print("reports written; top feature:", top.feature_name)


if __name__ == "__main__":
    main()
