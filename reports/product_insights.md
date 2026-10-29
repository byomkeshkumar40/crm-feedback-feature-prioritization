# Product Insights Report
> **SYNTHETIC DATA.** Every record is randomly generated for a fictional CRM company. Nothing here describes real customers or products.

Period analysed: 2025-10-01 to 2026-09-30 · 1,500 feedback records · 326 of 420 accounts (77.6%) submitted at least one item.

Legend: **[OBSERVED]** = computed directly from the synthetic data · **[INTERPRETATION]** = analytical reading of the numbers · **[HYPOTHESIS]** = product idea to validate, not a finding.

## 1. Top customer problems
**[OBSERVED]** Most-reported complaint themes (complaints = all categories except Feature Request):

| theme | feature_area | category | feedback_records | unique_customers | negative_pct | high_critical_pct |
|---|---|---|---|---|---|---|
| Unreliable contact imports | Contact Management | Bug | 102 | 86 | 74.5 | 42.2 |
| Workflows failing silently | Workflow Automation | Bug | 100 | 78 | 73 | 40 |
| Email and calendar sync drops | Integrations | Integration Issue | 88 | 74 | 69.3 | 39.8 |
| Confusing workflow builder | Workflow Automation | Usability Issue | 86 | 72 | 53.5 | 23.3 |
| Duplicate leads created | Lead Management | Bug | 77 | 69 | 75.3 | 41.6 |
| API limits and webhook failures | Integrations | Integration Issue | 65 | 55 | 73.8 | 43.1 |
| Slow dashboards | Reporting | Performance Issue | 61 | 50 | 65.6 | 31.1 |
| Cluttered navigation | User Interface | Usability Issue | 60 | 56 | 61.7 | 21.7 |
| Broken report exports | Reporting | Bug | 59 | 55 | 67.8 | 49.2 |
| Slow lead lists and pipeline board | Lead Management | Performance Issue | 48 | 44 | 75 | 35.4 |

**[INTERPRETATION]** The three largest complaint themes — Unreliable contact imports, Workflows failing silently, Email and calendar sync drops — are reliability problems (imports, automations, sync), not missing capabilities. Counts are feedback *volume*; the unique-customer column is the better indicator of breadth.

## 2. Most affected feature areas
**[OBSERVED]**

| feature_area | feedback_records | unique_customers | pct_of_records |
|---|---|---|---|
| Workflow Automation | 301 | 175 | 20.1 |
| Integrations | 258 | 147 | 17.2 |
| Contact Management | 257 | 160 | 17.1 |
| Lead Management | 239 | 153 | 15.9 |
| Reporting | 224 | 138 | 14.9 |
| User Interface | 221 | 140 | 14.7 |

High/Critical severity by area:

| feature_area | high_critical_records | unique_customers | share_of_area_records_pct |
|---|---|---|---|
| Integrations | 76 | 62 | 29.5 |
| Workflow Automation | 73 | 60 | 24.3 |
| Contact Management | 69 | 56 | 26.8 |
| Reporting | 69 | 52 | 30.8 |
| Lead Management | 64 | 58 | 26.8 |
| User Interface | 35 | 32 | 15.8 |

**[INTERPRETATION]** Volume is spread fairly evenly across areas (14.7%–20.1% each); Workflow Automation is largest. By High/Critical share, Reporting is highest (30.8%) and User Interface lowest (15.8%).

## 3. Differences across plans and segments
**[OBSERVED]** Accounts in the base are the only known denominator (customer master of 420 accounts).

| subscription_plan | feedback_records | accounts_in_base | records_per_account | unique_customers | pct_of_accounts_reporting |
|---|---|---|---|---|---|
| Professional | 651 | 180 | 3.62 | 145 | 80.6 |
| Starter | 471 | 166 | 2.84 | 122 | 73.5 |
| Enterprise | 378 | 74 | 5.11 | 59 | 79.7 |

| customer_segment | feedback_records | accounts_in_base | records_per_account | unique_customers | pct_of_accounts_reporting |
|---|---|---|---|---|---|
| Mid-Market | 609 | 168 | 3.62 | 133 | 79.2 |
| SMB | 589 | 183 | 3.22 | 140 | 76.5 |
| Enterprise | 302 | 69 | 4.38 | 53 | 76.8 |

**[INTERPRETATION]** Professional has the most records, but that mainly reflects having the most accounts. Per account, Enterprise submits the most (5.11 records/account vs 2.84 for Starter). The share of accounts that reported at least once is similar across plans (73.5%–80.6%). Do not read raw volume as prevalence.

## 4. Sentiment patterns
**[OBSERVED]** Overall: 44.1% negative. By plan (% of that plan's records):

| subscription_plan | Negative | Neutral | Positive |
|---|---|---|---|
| Enterprise | 38.9 | 40.2 | 20.9 |
| Professional | 44.9 | 41.8 | 13.4 |
| Starter | 47.3 | 39.9 | 12.7 |

**[INTERPRETATION]** Enterprise has the lowest negative share (38.9%) — but the generator gives Enterprise a different issue mix (more feature requests, which skew neutral/positive), so this is a **mix effect, not evidence Enterprise customers are happier**. Compare sentiment within the same category before drawing conclusions.

## 5. Most requested features
**[OBSERVED]**

| theme | feature_area | feedback_records | unique_customers | high_critical_pct |
|---|---|---|---|---|
| Mobile app | User Interface | 82 | 68 | 9.8 |
| Workflow templates | Workflow Automation | 80 | 69 | 11.2 |
| Custom and scheduled reports | Reporting | 76 | 59 | 19.7 |
| Bulk contact merge | Contact Management | 73 | 63 | 9.6 |
| Automated lead scoring | Lead Management | 69 | 57 | 7.2 |
| Native integrations | Integrations | 58 | 53 | 13.8 |
| SSO and provisioning | Integrations | 47 | 33 | 10.6 |
| Custom fields and hierarchy | Contact Management | 41 | 35 | 9.8 |
| Bulk actions | User Interface | 40 | 36 | 7.5 |
| Approval steps in workflows | Workflow Automation | 35 | 29 | 11.4 |

## 6. Highest-priority opportunities (RICE)
**[OBSERVED + ESTIMATES]** RICE inputs combine observed evidence (records, accounts, severity) with analyst estimates (Impact tiers, Confidence rule, Effort). Window: 2025-10-01 to 2026-09-30 (12 months).

| priority_rank | feature_id | feature_name | reach | impact | confidence | effort | rice_score | recommendation |
|---|---|---|---|---|---|---|---|---|
| 1 | F03 | Reliable CSV Import with Validation | 215 | 2 | 0.9 | 2 | 193.5 | Build now (next planning cycle) |
| 2 | F04 | Workflow Run Monitoring & Failure Alerts | 195 | 2 | 0.9 | 2.5 | 140.4 | Build now (next planning cycle) |
| 3 | F07 | Performance Tuning for Dashboards & Lists | 313 | 2 | 0.9 | 5 | 112.68 | Build now (next planning cycle) |
| 4 | F08 | Email & Calendar Sync Reliability | 185 | 2 | 0.7 | 3 | 86.33 | Plan next (validate scope) |
| 5 | F09 | API & Webhook Reliability Console | 138 | 2 | 0.7 | 2.5 | 77.28 | Plan next (validate scope) |
| 6 | F01 | Duplicate Detection & Bulk Merge | 295 | 1 | 1 | 4 | 73.75 | Plan next (validate scope) |
| 7 | F12 | Bulk Actions & Simplified Navigation | 210 | 1 | 0.9 | 3 | 63 | Investigate / discovery first |
| 8 | F05 | Guided Workflow Builder & Templates | 310 | 1 | 1 | 5 | 62 | Investigate / discovery first |
| 9 | F06 | Custom & Scheduled Reports with Reliable Export | 240 | 1 | 0.8 | 6 | 32 | Investigate / discovery first |
| 10 | F02 | Lead Scoring & Smart Routing | 225 | 0.5 | 0.8 | 5 | 18 | Defer; monitor feedback |
| 11 | F10 | Native Integrations (Accounting, Marketing, Slack) | 133 | 0.5 | 0.7 | 8 | 5.82 | Defer; monitor feedback |
| 12 | F11 | Mobile App | 170 | 0.5 | 0.7 | 12 | 4.96 | Defer; monitor feedback |

Sensitivity: across 8 alternative-assumption scenarios, rank movement per feature ranged from 0 to 3 places. Reliable CSV Import with Validation (F03) had best/worst rank 1/1 across scenarios. In 5,000 Monte Carlo trials (±30% on every input) it ranked #1 in 65.8% and top-3 in 96.1% of trials.

**[INTERPRETATION]** Top-ranked items are small-to-medium reliability fixes with high severity; large builds (Mobile App, Native Integrations) rank low mainly because of effort and lower severity signals, which is a property of the Impact rule (severity-based) — it under-values strategic feature requests.

## 7. Product recommendations (all **[HYPOTHESIS]**)
1. Start with **Reliable CSV Import with Validation**, then **Workflow Run Monitoring & Failure Alerts** and **Performance Tuning for Dashboards & Lists**; validate effort estimates with engineering first.
2. Run discovery (not build) for ranks 7–9 and keep ranks 10–12 on a watch list, re-scoring when new feedback arrives.
3. Track unique reporting accounts per theme monthly, not just ticket counts.
4. Re-estimate Impact for feature requests with customer interviews; severity alone understates their value.

## 8. Assumptions and limitations
- Data is synthetic; patterns reflect the generator's design (plan-level theme weights, a workflow-failure spike Feb 10 – Mar 3 2026 and a UI-lag spike June 2026). They show the *method*, not real customer behaviour.
- The issue-theme tagger uses the same key phrases the generator writes, so its 100% coverage is not evidence of real-world NLP accuracy.
- 151 records (10.1%) belong to themes not carried into RICE (contact_custom, int_sso, rep_forecast, wf_approval).
- Reach uses a 2.5× reporting multiplier (estimate) capped at the 420-account base. Impact, Confidence, Effort are estimates. RICE ranks are decision aids, not facts.
- Single 12-month window; no revenue, churn or support-cost data, so business impact is not measured.
