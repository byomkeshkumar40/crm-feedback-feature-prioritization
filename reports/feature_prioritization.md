# Feature Prioritization (RICE)
> **SYNTHETIC DATA.** Every record is randomly generated for a fictional CRM company. Nothing here describes real customers or products.

RICE = Reach × Impact × Confidence ÷ Effort. All scores are computed by `scripts/calculate_rice.py` from `data/assumptions/feature_assumptions.csv` and the cleaned feedback.

## Observed vs estimated
| Input | Type | How it is set |
|---|---|---|
| Supporting feedback count, unique affected customers | **Observed** | Records / accounts tagged to the feature's themes |
| Reach | **Estimate built on observed data** | Unique reporting accounts × reporting multiplier (assumed 2.5), rounded half-up, capped at the 420-account base. Time window: 2025-10-01 to 2026-09-30 (12 months) |
| Impact (0.25–3) | **Estimate** | Share of supporting records that are High/Critical severity *or* blocking/risk impact: ≥55%→3, ≥40%→2, ≥25%→1, ≥12%→0.5, else 0.25 |
| Confidence | **Estimate** | 0.5 + 0.1 for each of: ≥50, ≥100, ≥150 records; all 4 sources; all 3 plans; minus an analyst tech-risk penalty (0–0.1) |
| Effort (person-months) | **Estimate** | Analyst judgement per feature, with low/base/high range (see assumptions file) |

## Results
| priority_rank | feature_id | feature_name | supporting_feedback_count | unique_affected_customers | reach | impact | confidence | effort | rice_score | recommendation |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | F03 | Reliable CSV Import with Validation | 102 | 86 | 215 | 2 | 0.9 | 2 | 193.5 | Build now (next planning cycle) |
| 2 | F04 | Workflow Run Monitoring & Failure Alerts | 100 | 78 | 195 | 2 | 0.9 | 2.5 | 140.4 | Build now (next planning cycle) |
| 3 | F07 | Performance Tuning for Dashboards & Lists | 189 | 125 | 313 | 2 | 0.9 | 5 | 112.68 | Build now (next planning cycle) |
| 4 | F08 | Email & Calendar Sync Reliability | 88 | 74 | 185 | 2 | 0.7 | 3 | 86.33 | Plan next (validate scope) |
| 5 | F09 | API & Webhook Reliability Console | 65 | 55 | 138 | 2 | 0.7 | 2.5 | 77.28 | Plan next (validate scope) |
| 6 | F01 | Duplicate Detection & Bulk Merge | 150 | 118 | 295 | 1 | 1 | 4 | 73.75 | Plan next (validate scope) |
| 7 | F12 | Bulk Actions & Simplified Navigation | 100 | 84 | 210 | 1 | 0.9 | 3 | 63 | Investigate / discovery first |
| 8 | F05 | Guided Workflow Builder & Templates | 166 | 124 | 310 | 1 | 1 | 5 | 62 | Investigate / discovery first |
| 9 | F06 | Custom & Scheduled Reports with Reliable Export | 135 | 96 | 240 | 1 | 0.8 | 6 | 32 | Investigate / discovery first |
| 10 | F02 | Lead Scoring & Smart Routing | 114 | 90 | 225 | 0.5 | 0.8 | 5 | 18 | Defer; monitor feedback |
| 11 | F10 | Native Integrations (Accounting, Marketing, Slack) | 58 | 53 | 133 | 0.5 | 0.7 | 8 | 5.82 | Defer; monitor feedback |
| 12 | F11 | Mobile App | 82 | 68 | 170 | 0.5 | 0.7 | 12 | 4.96 | Defer; monitor feedback |

Per-feature rationale is in the `estimate_rationale` column of `data/processed/rice/rice_scores.csv` and in the Excel "RICE Calculations" sheet.

## Sensitivity analysis — rank under alternative assumptions
| feature_id | Base case | Reporting multiplier 1.5 | Reporting multiplier 4.0 | Reach capped at 250 accounts | Impact from High/Critical severity only | Confidence flat 0.8 | Optimistic effort (low estimates) | Pessimistic effort (high estimates) | best | worst |
|---|---|---|---|---|---|---|---|---|---|---|
| F03 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| F04 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 3 |
| F07 | 3 | 3 | 3 | 3 | 5 | 3 | 2 | 3 | 2 | 5 |
| F08 | 4 | 4 | 4 | 4 | 6 | 4 | 4 | 4 | 4 | 6 |
| F09 | 5 | 5 | 5 | 5 | 3 | 5 | 6 | 6 | 3 | 6 |
| F01 | 6 | 6 | 6 | 7 | 4 | 6 | 5 | 5 | 4 | 7 |
| F12 | 7 | 7 | 7 | 6 | 8 | 7 | 7 | 8 | 6 | 8 |
| F05 | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 7 | 7 | 9 |
| F06 | 9 | 9 | 9 | 9 | 7 | 9 | 9 | 9 | 7 | 9 |
| F02 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| F10 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| F11 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 |

## Monte Carlo rank stability (5,000 trials, ±30% uniform noise on R, I, C, E)
| feature_id | feature_name | base_rank | median_rank | p10_rank | p90_rank | prob_top3_pct | prob_rank1_pct |
|---|---|---|---|---|---|---|---|
| F03 | Reliable CSV Import with Validation | 1 | 1 | 1 | 3 | 96.1 | 65.8 |
| F04 | Workflow Run Monitoring & Failure Alerts | 2 | 2 | 1 | 4 | 80.6 | 22.2 |
| F07 | Performance Tuning for Dashboards & Lists | 3 | 3 | 2 | 6 | 57.6 | 8.1 |
| F08 | Email & Calendar Sync Reliability | 4 | 5 | 2 | 7 | 28.8 | 2.3 |
| F09 | API & Webhook Reliability Console | 5 | 5 | 3 | 8 | 18.6 | 1.1 |
| F01 | Duplicate Detection & Bulk Merge | 6 | 6 | 4 | 8 | 9.6 | 0.4 |
| F12 | Bulk Actions & Simplified Navigation | 7 | 7 | 4 | 8 | 5.3 | 0.1 |
| F05 | Guided Workflow Builder & Templates | 8 | 7 | 5 | 8 | 3.5 | 0 |
| F06 | Custom & Scheduled Reports with Reliable Export | 9 | 9 | 8 | 10 | 0 | 0 |
| F02 | Lead Scoring & Smart Routing | 10 | 10 | 9 | 10 | 0 | 0 |
| F10 | Native Integrations (Accounting, Marketing, Slack) | 11 | 11 | 11 | 12 | 0 | 0 |
| F11 | Mobile App | 12 | 12 | 11 | 12 | 0 | 0 |

## Reading this honestly
- Rank-1 feature F03 holds rank 1–1 across all scenarios; rank-2 feature F04 holds 2–3; other positions move by up to 3 places depending on assumptions.
- RICE is a structured conversation aid. Impact here is severity-based, so it favours bug-fix reliability work over strategic requests.
- 151 records in themes not evaluated (contact_custom, int_sso, rep_forecast, wf_approval) are outside this round.
