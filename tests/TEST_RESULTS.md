# Test results (executed 2026-10-29, pre-publication audit)

## pytest
```
tests/test_pipeline.py::test_exactly_1500_records PASSED                 [  6%]
tests/test_pipeline.py::test_generator_deterministic PASSED              [ 12%]
tests/test_pipeline.py::test_no_duplicate_ids PASSED                     [ 18%]
tests/test_pipeline.py::test_customer_relationships PASSED               [ 25%]
tests/test_pipeline.py::test_categorical_validity PASSED                 [ 31%]
tests/test_pipeline.py::test_area_category_consistency PASSED            [ 37%]
tests/test_pipeline.py::test_text_variety PASSED                         [ 43%]
tests/test_pipeline.py::test_theme_keys_unambiguous PASSED               [ 50%]
tests/test_pipeline.py::test_cleaning_fixes_noise PASSED                 [ 56%]
tests/test_pipeline.py::test_validator_flags_bad_data PASSED             [ 62%]
tests/test_pipeline.py::test_counts_match_pandas PASSED                  [ 68%]
tests/test_pipeline.py::test_rice_math_and_ranks PASSED                  [ 75%]
tests/test_pipeline.py::test_rice_rounding_half_up PASSED                [ 81%]
tests/test_pipeline.py::test_rice_files_consistent_with_assumptions PASSED [ 87%]
tests/test_pipeline.py::test_excel_workbook PASSED                       [ 93%]
tests/test_pipeline.py::test_reports_consistent_with_results PASSED      [100%]
============================== 16 passed in 3.19s ==============================
```

## Excel formula recalculation (independent 'formulas' library vs Python)
```
PASS sheet names/order ['Executive Summary', 'Raw Feedback', 'Cleaned Feedback', 'Feedback Analysis', 'Feature Prioritization', 'RICE Calculations', 'Product Recommendations']
PASS Raw Feedback: 1500 data rows 1501
PASS Cleaned Feedback: 1500 data rows 1501
PASS Raw Feedback: filter + frozen header ('A1:L1501', 'A2')
PASS Cleaned Feedback: filter + frozen header ('A1:O1501', 'A2')
PASS Feature Prioritization: filter + frozen header ('A5:L17', 'C6')
PASS RICE Calculations: filter + frozen header ('A8:L20', 'C9')
PASS Product Recommendations: filter + frozen header ('A5:E17', 'A6')
PASS Feature Prioritization: conditional formatting 1
PASS RICE Calculations: conditional formatting 1
PASS contains working formulas 242
PASS KPI total feedback excel=1500 python=1500
PASS KPI negative % excel=0.44133333333333336 python=0.44133333333333336
PASS KPI high/critical % excel=0.25733333333333336 python=0.25733333333333336
PASS KPI feature requests excel=629 python=629
PASS RICE score F03 excel=193.5 python=193.5
PASS RICE rank F03 excel=1.0 python=1
PASS Reach F03 excel=215.0 python=215
PASS RICE score F04 excel=140.4 python=140.4
PASS RICE rank F04 excel=2.0 python=2
PASS Reach F04 excel=195.0 python=195
PASS RICE score F07 excel=112.68 python=112.68
PASS RICE rank F07 excel=3.0 python=3
PASS Reach F07 excel=313.0 python=313
PASS RICE score F08 excel=86.33 python=86.33
PASS RICE rank F08 excel=4.0 python=4
PASS Reach F08 excel=185.0 python=185
PASS RICE score F09 excel=77.28 python=77.28
PASS RICE rank F09 excel=5.0 python=5
PASS Reach F09 excel=138.0 python=138
PASS RICE score F01 excel=73.75 python=73.75
PASS RICE rank F01 excel=6.0 python=6
PASS Reach F01 excel=295.0 python=295
PASS RICE score F12 excel=63.0 python=63.0
PASS RICE rank F12 excel=7.0 python=7
PASS Reach F12 excel=210.0 python=210
PASS RICE score F05 excel=62.0 python=62.0
PASS RICE rank F05 excel=8.0 python=8
PASS Reach F05 excel=310.0 python=310
PASS RICE score F06 excel=32.0 python=32.0
PASS RICE rank F06 excel=9.0 python=9
PASS Reach F06 excel=240.0 python=240
PASS RICE score F02 excel=18.0 python=18.0
PASS RICE rank F02 excel=10.0 python=10
PASS Reach F02 excel=225.0 python=225
PASS RICE score F10 excel=5.82 python=5.82
PASS RICE rank F10 excel=11.0 python=11
PASS Reach F10 excel=133.0 python=133
PASS RICE score F11 excel=4.96 python=4.96
PASS RICE rank F11 excel=12.0 python=12
PASS Reach F11 excel=170.0 python=170
PASS Exec summary top-1 name matches Reliable CSV Import with Validation
PASS COUNTIF feature_area Workflow Automation excel=301 python=301
PASS COUNTIF feature_area Integrations excel=258 python=258
PASS COUNTIF feature_area Contact Management excel=257 python=257
PASS COUNTIF feature_area Lead Management excel=239 python=239
PASS COUNTIF feature_area Reporting excel=224 python=224
PASS COUNTIF feature_area User Interface excel=221 python=221
```

## Excel formulas in Microsoft Excel for Mac (AppleScript read-back, 2026-10-29)
Opened the workbook in Excel; calculated values matched Python: KPIs 1500 / 326 / 0.4413 / 0.2573 / 629; RICE F03 193.5 (rank 1), F04 140.4 (rank 2), F01 73.75 (rank 6), F02 18 (rank 10); Executive Summary top-3 names/scores = F03 193.5, F04 140.4, F07 112.68. Only a sample of cells was read back in Excel; the full comparison is the library check above.

## Dashboard end-to-end (Playwright)
```
PASS overview: no exception/dialog 
PASS : charts rendered 4 plotly charts
PASS pain-points: no exception/dialog 
PASS pain-points: charts rendered 5 plotly charts
PASS prioritization: no exception/dialog 
PASS prioritization: charts rendered 2 plotly charts
PASS overview KPIs unfiltered match pandas ['1,500', '326', '44.1%', '25.7%', '629']
PASS plan filter -> Enterprise: all 5 KPIs equal pandas dashboard=['378', '59', '38.9%', '29.1%', '192'] pandas=['378', '59', '38.9%', '29.1%', '192']
PASS prioritization page loads after filter 
PASS prioritization shows RICE caption about fixed assumptions 
PASS screenshot exists & non-trivial: feedback_overview.png 188245 bytes
PASS screenshot exists & non-trivial: customer_pain_points.png 200275 bytes
PASS screenshot exists & non-trivial: feature_prioritization.png 371854 bytes
```
