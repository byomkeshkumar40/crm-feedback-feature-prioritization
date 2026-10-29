#!/usr/bin/env bash
# Reproduce everything: data -> clean -> validate -> analyse -> RICE -> Excel -> reports -> tests.
set -euo pipefail
cd "$(dirname "$0")"
python scripts/generate_data.py
python scripts/clean_data.py > /dev/null
python scripts/validate_data.py
python scripts/analyze_feedback.py > /dev/null
python scripts/calculate_rice.py > /dev/null
python scripts/build_excel.py
python scripts/build_reports.py
pytest -q
python scripts/validate_excel.py | tail -1
echo "Pipeline OK. Dashboard: streamlit run dashboards/streamlit/app.py"
echo "Screenshots (dashboard must be running on :8599): python scripts/capture_screenshots.py"
