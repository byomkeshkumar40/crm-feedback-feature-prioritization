"""Drive the running Streamlit dashboard with Playwright: smoke-test 3 pages + filters, capture screenshots.

Usage: python scripts/capture_screenshots.py [base_url]   (dashboard must already be running)
"""
import sys
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "dashboards" / "screenshots"
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599"
PAGES = [("", "feedback_overview.png", 4), ("pain-points", "customer_pain_points.png", 5),
         ("prioritization", "feature_prioritization.png", 2)]
results = []


def record(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name, detail)


def wait_ready(page, min_charts):
    page.wait_for_selector('[data-testid="stMain"]', timeout=30000)
    page.wait_for_function(f"document.querySelectorAll('.js-plotly-plot .main-svg').length >= {min_charts}", timeout=30000)
    page.wait_for_timeout(2500)


def errors(page):
    return page.locator('[data-testid="stException"], [data-testid="stDialog"]').count()


def kpi_values(page):
    return page.locator(".kpi .value").all_inner_texts()


def remove_tag(page, label_index, tag_text):
    """Remove a selected option from the n-th sidebar multiselect."""
    ms = page.locator('[data-testid="stSidebar"] [data-testid="stMultiSelect"]').nth(label_index)
    ms.locator(f'button[aria-label="Remove {tag_text}"]').first.click()
    page.wait_for_timeout(2500)


def main():
    SHOTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(ROOT / "data" / "processed" / "feedback_clean.csv")
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
        for slug, fname, n in PAGES:
            page.goto(f"{BASE}/{slug}")
            wait_ready(page, n)
            record(f"{slug or 'overview'}: no exception/dialog", errors(page) == 0)
            record(f"{slug}: charts rendered", page.locator(".js-plotly-plot").count() >= n, f"{page.locator('.js-plotly-plot').count()} plotly charts")
            h = page.evaluate("document.querySelector('[data-testid=\"stMain\"]').scrollHeight")
            page.set_viewport_size({"width": 1600, "height": min(h + 60, 5000)})
            page.wait_for_timeout(2500)
            page.screenshot(path=str(SHOTS / fname), full_page=True)
            page.set_viewport_size({"width": 1600, "height": 1000})
        # ---- filter test on the overview page ----
        page.goto(f"{BASE}/"); wait_ready(page, 4)
        vals = kpi_values(page)
        record("overview KPIs unfiltered match pandas", vals[0] == f"{len(df):,}" and vals[1] == f"{df.customer_id.nunique():,}", str(vals))
        remove_tag(page, 0, "Starter"); remove_tag(page, 0, "Professional")   # plan = Enterprise only
        ent = df[df.subscription_plan == "Enterprise"]
        vals = kpi_values(page)
        exp = [f"{len(ent):,}", f"{ent.customer_id.nunique():,}", f"{(ent.sentiment == 'Negative').mean():.1%}",
               f"{ent.severity.isin(['High', 'Critical']).mean():.1%}", f"{(ent.feedback_category == 'Feature Request').sum():,}"]
        record("plan filter -> Enterprise: all 5 KPIs equal pandas", vals == exp, f"dashboard={vals} pandas={exp}")
        page.goto(f"{BASE}/prioritization"); wait_ready(page, 2)
        record("prioritization page loads after filter", errors(page) == 0)
        rank1 = page.locator('[data-testid="stDataFrame"]').first
        record("prioritization shows RICE caption about fixed assumptions", "do not change with the sidebar filters" in page.content())
        b.close()
    for fname in [f for _, f, _ in PAGES]:
        path = SHOTS / fname
        ok = path.exists() and path.stat().st_size > 30_000
        record(f"screenshot exists & non-trivial: {fname}", ok, f"{path.stat().st_size if path.exists() else 0} bytes")
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)


if __name__ == "__main__":
    main()
