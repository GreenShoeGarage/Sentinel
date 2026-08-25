#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / "index.html").read_text(encoding="utf-8")
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
results: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object = "") -> None:
    results.append({"name": name, "passed": bool(condition), "detail": str(detail)[:1500]})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


check("Release Candidate 2 identity", "APP_VERSION='0.15.0-rc.2'" in SOURCE)
check("Schema remains 14", "SCHEMA_VERSION=14" in SOURCE)
check("Legacy 245 mm report cover removed", "min-height:245mm" not in SOURCE)
check("Letter-safe report cover is present", SOURCE.count("min-height:235mm") >= 4, SOURCE.count("min-height:235mm"))
check("Print headings avoid orphaning", "break-after:avoid-page" in SOURCE)
check("Print table headings repeat", "display:table-header-group" in SOURCE)
check("Print paragraphs have widow and orphan controls", "orphans:3;widows:3" in SOURCE)
check("Paged-media headers use margin boxes", '@top-center{content:"${pageHeader}"' in SOURCE)
check("Paged-media footers include Page X of Y counters", 'counter(page) " of " counter(pages)' in SOURCE)
check("Legacy fixed-footer Page 0 counter is removed", '.report-running-footer:after{content:" · Page " counter(page)}' not in SOURCE)
check("Search is an accessible modal dialog", 'id="searchBox" role="dialog" aria-modal="true"' in SOURCE)
check("Search has hidden-state semantics", 'aria-label="Search records and commands" aria-hidden="true"' in SOURCE)
check("Search results use listbox semantics", 'id="searchResults" role="listbox"' in SOURCE)
check("Reduced-motion preference is honored", "prefers-reduced-motion:reduce" in SOURCE)
check("Checkboxes and radios have usable dimensions", 'input[type="checkbox"],input[type="radio"]{width:18px;height:18px' in SOURCE)
check("Mobile checkbox targets reach 44 pixels", "min-height:44px" in SOURCE)
check("Generic select helper associates labels", '<label for="${id}">${label}</label>' in SOURCE)
check("Modal focus helper exists", "function trapFocus(event,root)" in SOURCE)
check("Search close restores focus", "window.__sentinelSearchLastFocus" in SOURCE and "function closeSearch" in SOURCE)
check("Interactive row limit is explicit", "UI_ROW_LIMIT=500" in SOURCE)
check("Large project threshold is explicit", "LARGE_PROJECT_RECORD_THRESHOLD=5000" in SOURCE)
check("Large project profile is exposed", "projectScaleProfile:p=>projectScaleProfile" in SOURCE)
check("Register guardrail is user-visible", "Showing the first ${shown.toLocaleString()}" in SOURCE)

required_aria = [
    "ev_query", "ev_type", "ev_integrity", "ev_group",
    "tf_date", "tf_actor", "tf_location", "tf_test", "tf_type",
    "ff_severity", "ff_status", "ff_remediation", "ff_owner",
    "cf_dimension", "cf_outcome", "cf_location", "cf_query",
    "gf_severity", "gf_status", "gf_type", "gf_query",
    "traceRoot", "traceDirection", "traceDepth", "traceMax",
    "rt_query", "rt_status", "rt_result", "rt_owner",
]
missing = []
for control_id in required_aria:
    pattern = rf'id="{re.escape(control_id)}"[^>]*aria-label='
    if not re.search(pattern, SOURCE):
        missing.append(control_id)
check("Known filter controls have accessible names", not missing, missing)

summary = {
    "suite": "SENTINEL Release Candidate 2 static acceptance",
    "passed": all(x["passed"] for x in results),
    "assertionCount": len(results),
    "assertions": results,
}
(OUT / "rc2_static_checks.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(OUT / "rc2_static_checks.txt").write_text(
    "\n".join([f"PASS {len(results)}/{len(results)}"] + [f"PASS {x['name']}: {x['detail']}" for x in results]),
    encoding="utf-8",
)
print(f"PASS {len(results)}/{len(results)}")
