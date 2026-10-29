# Data Quality Report

> All data is **SYNTHETIC** (randomly generated, fixed seed).

Produced by `scripts/validate_data.py`. Raw checks are expected to flag formatting noise that was injected on purpose; cleaned-data checks must all pass.

## Raw data checks

| Check | Result | Detail |
|---|---|---|
| required columns present | PASS | missing=[] |
| row count == 1500 | PASS | 1500 |
| no duplicate feedback_id | PASS | 0 |
| no fully duplicated rows | PASS | 0 |
| customer_id format CUST-#### | PASS |  |
| all customer_ids exist in customer master | PASS | 0 |
| plan matches customer master | PASS |  |
| segment matches customer master | PASS |  |
| all dates parseable | PASS | 0 |
| dates within 2025-10-01..2026-09-30 | PASS |  |
| dates not before customer signup | PASS |  |
| no missing feedback_text | PASS |  |
| feedback_source: only valid values | FAIL | invalid=[' Customer Survey', ' Feature Request', ' In-App Feedback', ' Support Ticket', 'CUSTOMER SURVEY'] |
| feedback_source: no missing | PASS | 0 |
| subscription_plan: only valid values | FAIL | invalid=[' Professional', ' Starter', 'ENTERPRISE', 'Enterprise ', 'PROFESSIONAL'] |
| subscription_plan: no missing | PASS | 0 |
| customer_segment: only valid values | FAIL | invalid=[' Enterprise', ' Mid-Market', ' SMB', 'ENTERPRISE', 'Enterprise '] |
| customer_segment: no missing | PASS | 0 |
| feature_area: only valid values | FAIL | invalid=[' Contact Management', ' User Interface', ' Workflow Automation', 'CONTACT MANAGEMENT', 'Contact Management '] |
| feature_area: no missing | PASS | 0 |
| feedback_category: only valid values | FAIL | invalid=[' Bug', ' Feature Request', ' Usability Issue', 'BUG', 'Bug '] |
| feedback_category: no missing | PASS | 0 |
| sentiment: only valid values | FAIL | invalid=[' Negative', ' Neutral', ' Positive', 'NEGATIVE', 'NEUTRAL'] |
| sentiment: no missing | PASS | 0 |
| severity: only valid values | FAIL | invalid=[' Low', ' Medium', 'Critical ', 'HIGH', 'High '] |
| severity: no missing | PASS | 0 |
| customer_impact: only valid values | PASS | invalid=[] |
| unique feedback_text share >= 95% | PASS | 98.7% |

**21/28 passed.**

## Clean data checks

| Check | Result | Detail |
|---|---|---|
| required columns present | PASS | missing=[] |
| row count == 1500 | PASS | 1500 |
| no duplicate feedback_id | PASS | 0 |
| no fully duplicated rows | PASS | 0 |
| customer_id format CUST-#### | PASS |  |
| all customer_ids exist in customer master | PASS | 0 |
| plan matches customer master | PASS |  |
| segment matches customer master | PASS |  |
| all dates parseable | PASS | 0 |
| dates within 2025-10-01..2026-09-30 | PASS |  |
| dates not before customer signup | PASS |  |
| no missing feedback_text | PASS |  |
| feedback_source: only valid values | PASS | invalid=[] |
| feedback_source: no missing | PASS | 0 |
| subscription_plan: only valid values | PASS | invalid=[] |
| subscription_plan: no missing | PASS | 0 |
| customer_segment: only valid values | PASS | invalid=[] |
| customer_segment: no missing | PASS | 0 |
| feature_area: only valid values | PASS | invalid=[] |
| feature_area: no missing | PASS | 0 |
| feedback_category: only valid values | PASS | invalid=[] |
| feedback_category: no missing | PASS | 0 |
| sentiment: only valid values | PASS | invalid=[] |
| sentiment: no missing | PASS | 0 |
| severity: only valid values | PASS | invalid=[] |
| severity: no missing | PASS | 0 |
| customer_impact: only valid values | PASS | invalid=[] |
| unique feedback_text share >= 95% | PASS | 98.7% |
| each theme maps to 1 area and 1 category | PASS |  |
| every record tagged to exactly one theme | PASS | 0 |

**30/30 passed.**

## Cleaning actions

```json
{
  "rows_in": 1500,
  "values_normalised_by_column": {
    "feedback_source": 30,
    "subscription_plan": 30,
    "customer_segment": 28,
    "feature_area": 30,
    "feedback_category": 30,
    "sentiment": 30,
    "severity": 30,
    "customer_impact": 0
  },
  "missing_customer_impact_before": 12,
  "customer_impact_imputed_as_Unknown": 12,
  "non_iso_dates_converted": 45,
  "theme_tag_unmatched": 0,
  "theme_tag_ambiguous": 0,
  "rows_out": 1500
}
```
