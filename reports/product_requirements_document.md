# Product Requirements Document — Reliable CSV Import with Validation
> **SYNTHETIC DATA.** Every record is randomly generated for a fictional CRM company. Nothing here describes real customers or products.

| | |
|---|---|
| Status | **Draft proposal — not implemented, no outcome claimed** |
| Source analysis | RICE rank **#1** (score 193.5) of 12 opportunities; `reports/feature_prioritization.md` |
| Author | Product Analyst (portfolio project) |

## 1. Product Overview
Improve the contact import experience so that customers can bring spreadsheet data into the CRM with a pre-import check, remembered field mappings, and a downloadable row-level error report, instead of failing midway with a generic error.

## 2. Problem Statement
Customers report that contact CSV imports fail, scramble phone/email columns, silently skip rows, or reject files with accented characters. They find out late and cannot see which rows failed, so they clean data by hand or re-run the import.

## 3. Background and Evidence (all from the synthetic dataset)
- **102 feedback records** from **86 unique accounts** (20.5% of the 420-account base) — the largest complaint theme in the dataset.
- 74.5% negative; 42.2% High/Critical severity; 37.3% blocking a key task or creating operations risk.
- Severity mix: Medium 39, High 28, Low 20, Critical 15. Sources: Support Ticket 52, In-App Feedback 32, Customer Survey 16, Feature Request 2.
- By plan (accounts reporting import issues / accounts on that plan):

| subscription_plan | records | accounts | pct_of_plan_accounts |
|---|---|---|---|
| Enterprise | 10 | 7 | 9.5 |
| Professional | 41 | 38 | 21.1 |
| Starter | 51 | 41 | 24.7 |

- RICE: Reach 215, Impact 2.0, Confidence 0.9, Effort 2.0 person-months (all estimates; see `feature_prioritization.md`). Rank 1–1 across scenarios; #1 in 65.8% of Monte Carlo trials.
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
| Import-related feedback records per month | 8.5/month in synthetic data (12-month avg) | −50% within 90 days of GA |
| Unique accounts reporting import issues per quarter | 22 (annualised ÷ 4, rough) | −40% |
| First-attempt import success rate | to be instrumented | ≥95% of jobs with no failed rows after validation fixes |
| Share of imports using saved mapping | 0% | ≥40% of repeat imports |
| Support contacts per 100 imports | to be instrumented | −50% |
Guardrails: median import completion time not worse than current; no increase in data-loss reports.

## 14. Dependencies
Background job infrastructure; file storage; notification service; design for the import wizard; support tooling for import logs; legal/privacy review for file retention.

## 15. Risks and Assumptions
- Assumption: import is a frequent workflow; verify with product telemetry.
- Assumption: effort 2.0 person-months (range 1.5–3) is an analyst estimate pending engineering review.
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
