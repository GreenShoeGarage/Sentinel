#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
RESULT = {
    "suite": "SENTINEL release-candidate browser smoke",
    "started": dt.datetime.now(dt.timezone.utc).isoformat(),
    "assertions": [],
}


def check(name: str, condition: bool, detail="", *, advisory: bool = False) -> None:
    RESULT["assertions"].append({"name": name, "passed": bool(condition), "advisory": advisory, "detail": str(detail)[:3000]})
    if not condition and not advisory:
        raise AssertionError(f"{name}: {detail}")


def run() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    errors: list[str] = []
    console_errors: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.expose_function("__sentinelTestSha256", lambda values: list(hashlib.sha256(bytes(values)).digest()))
        page.goto("about:blank")
        page.evaluate("""()=>Object.defineProperty(window.crypto,'subtle',{configurable:true,value:{digest:async(_a,d)=>Uint8Array.from(await window.__sentinelTestSha256(Array.from(new Uint8Array(d)))).buffer}})""")
        page.set_content(html, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(350)

        check("Application title", page.title() == "SENTINEL — Physical Security Red Team Workbench", page.title())
        identity = page.evaluate("()=>({version:__SENTINEL_TEST__.appVersion,schema:__SENTINEL_TEST__.schemaVersion})")
        check("Release identity", identity == {"version": "0.15.0-rc.2", "schema": 14}, identity)
        audit = page.evaluate("()=>__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.blankProject())")
        check("Blank Schema 14 project audits clean", audit.get("ok") is True, audit)

        page.evaluate("""()=>{const p=__SENTINEL_TEST__.blankProject();p.mode='advanced';p.project.name='Release Candidate Smoke';p.project.client='Validation Client';p.project.site='Validation Site';__SENTINEL_TEST__.setData(p);}""")
        page.locator("#advancedBtn").click()
        page.wait_for_timeout(100)

        nav = page.locator(".navitem:visible")
        view_ids: list[str] = []
        for i in range(nav.count()):
            view = nav.nth(i).get_attribute("data-view")
            if view and view not in view_ids:
                view_ids.append(view)
        check("Advanced workflow exposes substantial navigation", len(view_ids) >= 20, view_ids)
        nav_failures: list[dict[str, str]] = []
        for view in view_ids:
            item = page.locator(f'.navitem[data-view="{view}"]:visible').first
            item.click()
            page.wait_for_timeout(25)
            target = page.locator(f"#{view}View")
            active = target.count() == 1 and "active" in (target.get_attribute("class") or "")
            text = target.inner_text().strip() if target.count() else ""
            if not active or len(text) < 10:
                nav_failures.append({"view": view, "active": str(active), "text": text[:100]})
        check("Every visible workflow destination opens", not nav_failures, nav_failures)
        check("Report destination is included", "report" in view_ids, view_ids)
        check("Assessment Assurance destination is included", "coverage" in view_ids, view_ids)
        check("Remediation and Retest destination is included", "retest" in view_ids, view_ids)

        page.locator("#globalSearchBtn").click()
        page.wait_for_timeout(50)
        check("Command palette opens", page.locator("#searchBox").evaluate("el=>el.classList.contains('open')"))
        command_text = page.locator("#searchResults").inner_text()
        check("Command palette includes report and evidence actions", "Open Report Builder" in command_text and "Open Evidence Vault" in command_text, command_text[:1000])
        page.locator("#searchInput").press("Escape")

        project_button = page.locator("#projectMenuBtn")
        check("Consolidated Project menu is present", project_button.count() == 1)
        project_button.click()
        page.wait_for_timeout(60)
        project_menu_text = page.locator("#projectMenu").inner_text()
        check("Project menu contains recovery and package operations", all(x in project_menu_text for x in ["Open Project", "Export Project Package", "Recovery"]), project_menu_text)
        page.keyboard.press("Escape")

        before = page.locator("#mainContent").bounding_box()
        page.locator("#sidebarToggleBtn").click()
        page.wait_for_timeout(100)
        after = page.locator("#mainContent").bounding_box()
        check("Desktop sidebar collapse preserves workspace width", bool(before and after and after["width"] > 600), {"before": before, "after": after})
        page.locator("#sidebarToggleBtn").click()

        page.locator('[data-view="report"]').click()
        page.wait_for_timeout(50)
        check("Professional Report Builder 2.0 renders in full application", "PROFESSIONAL REPORT BUILDER 2.0" in page.locator("#reportView").inner_text().upper())
        check("Report Builder exposes composition through governance", page.locator("[data-report-tab]").count() == 5)
        page.screenshot(path=str(OUT / "rc_desktop_smoke.png"), full_page=True)

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(120)
        page.locator("#mobileMenuBtn").click()
        page.wait_for_timeout(60)
        check("Mobile navigation drawer opens", page.locator("#appSidebar").evaluate("el=>el.classList.contains('open')"))
        check("Mobile menu reports expanded state", page.locator("#mobileMenuBtn").get_attribute("aria-expanded") == "true")
        page.locator("#sidebarBackdrop").click(position={"x": 385, "y": 420})
        page.wait_for_timeout(240)
        check("Mobile navigation drawer closes", not page.locator("#appSidebar").evaluate("el=>el.classList.contains('open')"))
        dimensions = page.evaluate("()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,footer:document.querySelector('.footer')?.getBoundingClientRect().height})")
        check("Mobile shell avoids page-level horizontal overflow", dimensions["scroll"] <= dimensions["client"] + 8, dimensions)
        check("Mobile footer remains visible and compact", 0 < dimensions["footer"] < 90, dimensions)
        page.screenshot(path=str(OUT / "rc_mobile_smoke.png"), full_page=True)

        material_console = [x for x in console_errors if not re.search(r"indexeddb|localstorage|securityerror|storage", x, re.I)]
        check("No uncaught browser exceptions", not errors, errors)
        check("No material console errors", not material_console, material_console)
        if console_errors:
            check("Opaque-origin storage notes documented", True, console_errors, advisory=True)
        browser.close()


try:
    run()
except Exception as exc:
    RESULT["fatal"] = str(exc)
    RESULT["traceback"] = traceback.format_exc()
finally:
    RESULT["completed"] = dt.datetime.now(dt.timezone.utc).isoformat()
    required = [a for a in RESULT["assertions"] if not a.get("advisory")]
    RESULT["passed"] = bool(required) and all(a["passed"] for a in required) and "fatal" not in RESULT
    (OUT / "rc_browser_smoke.json").write_text(json.dumps(RESULT, indent=2), encoding="utf-8")
    lines = [f"{'PASS' if RESULT['passed'] else 'FAIL'} {sum(a['passed'] for a in RESULT['assertions'])}/{len(RESULT['assertions'])}"]
    lines += [f"{'PASS' if a['passed'] else 'FAIL'}{' (advisory)' if a.get('advisory') else ''} {a['name']}: {a['detail']}" for a in RESULT["assertions"]]
    if RESULT.get("fatal"):
        lines += ["FATAL " + RESULT["fatal"], RESULT.get("traceback", "")]
    (OUT / "rc_browser_smoke.txt").write_text("\n".join(lines), encoding="utf-8")
    if not RESULT["passed"]:
        raise SystemExit(1)
