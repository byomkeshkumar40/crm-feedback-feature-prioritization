# Methodology, Assumptions and Limitations
> **All data is SYNTHETIC** (fixed seed 20260930; fictional CRM company; no real customers).

## Data generation
`scripts/generate_data.py` draws 420 accounts (plan/segment correlated), then 1,500 feedback records. Each record: account (weighted by plan) → issue theme (base weight × plan multiplier, see `scripts/themes.py`) → date (gradual volume growth; incidents: workflow failures 2026-02-10..03-03 ×4, UI lag 2026-06-01..06-28 ×3) → source, sentiment, severity and impact (conditional on category, plan and sentiment) → text (phrase templates). Weights were set up front for realism and **not** adjusted after seeing results. The raw file has deliberate noise (casing/whitespace in ~2% of categorical fields, 45 `DD-Mon-YYYY` dates, 12 blank `customer_impact`).

## Circular issue tagger
`clean_data.py` tags each record's theme by matching key phrases from `themes.py` — the same phrases the generator inserts into the text. Result: 0 unmatched, 0 ambiguous records, and tests assert tag == generator theme. This verifies internal consistency only; on real free-text feedback a keyword or ML classifier would be imperfect and needs its own evaluation.

## Records not included in RICE
The 12 opportunities map to 20 of 24 themes (1,349 records). Four themes are **not** scored (151 records, 10.1%): `contact_custom` (custom fields & hierarchy), `int_sso` (SSO/SCIM), `rep_forecast` (sales forecasting), `wf_approval` (approval steps). They appear in the descriptive analysis (top requests) but cannot win a RICE rank. SSO in particular is Enterprise-heavy and could matter commercially.

## RICE inputs
| Input | Observed or estimate | Rule |
|---|---|---|
| Supporting feedback, unique accounts | Observed | Records/accounts tagged to the feature's themes |
| Reach | Estimate on observed data | unique accounts × 2.5 reporting multiplier, rounded half-up, capped at 420 accounts; window 2025-10-01..2026-09-30 |
| Impact | Estimate | share High/Critical **or** blocking/risk impact: ≥55%→3, ≥40%→2, ≥25%→1, ≥12%→0.5, else 0.25 |
| Confidence | Estimate | 0.5 +0.1 each for ≥50/≥100/≥150 records, 4 sources, 3 plans; minus tech-risk penalty 0–0.1 |
| Effort | Estimate | analyst person-months with low/base/high in `data/assumptions/feature_assumptions.csv` |

Sensitivity: 8 deterministic scenarios (multiplier 1.5/4.0, reach cap 250, severity-only impact, flat confidence 0.8, low/high effort) and 5,000 Monte Carlo trials (±30% uniform on R, I, C, E; seed 7). Rank-1 F03 holds #1 in all scenarios; maximum rank movement for any feature is 3 places.

## Other limitations
Volume ≠ prevalence; plan/segment sentiment differences are partly issue-mix effects; Impact (severity-based) under-values strategic requests such as Mobile App; Excel Reach/Impact/Confidence/Effort are inputs you can edit, but Impact/Confidence are not re-derived by formula; no revenue, churn or ticket-cost data.

## Change log for this audit
- RICE reach rounding changed earlier from NumPy half-even to half-up to match Excel (ranks unchanged). No other methodology change in the publication audit.
