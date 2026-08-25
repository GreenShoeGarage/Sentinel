#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import traceback
from pathlib import Path

import fitz
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
PDF_PATH = OUT / "rc2_representative_letter_report.pdf"
SCREENSHOT_PATH = OUT / "rc2_accessibility_and_limits.png"
RESULT = {
    "suite": "SENTINEL Release Candidate 2 accessibility, performance, and PDF acceptance",
    "started": dt.datetime.now(dt.timezone.utc).isoformat(),
    "assertions": [],
}


def check(name: str, condition: bool, detail: object = "") -> None:
    RESULT["assertions"].append({"name": name, "passed": bool(condition), "detail": str(detail)[:3000]})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def accessible_name_failures(page) -> list[dict[str, str]]:
    return page.evaluate(
        """()=>[...document.querySelectorAll('input:not([type="hidden"]),select,textarea')]
          .filter(el=>el.offsetParent!==null&&!el.disabled)
          .map(el=>{
            const labels=el.labels?[...el.labels].map(x=>x.textContent.trim()).filter(Boolean):[];
            const ancestor=el.closest('label')?.textContent.trim()||'';
            const aria=el.getAttribute('aria-label')||'';
            const labelledby=el.getAttribute('aria-labelledby')||'';
            return {id:el.id||'',tag:el.tagName,type:el.type||'',labels:labels.join(' | '),ancestor,aria,labelledby};
          })
          .filter(x=>!x.labels&&!x.ancestor&&!x.aria&&!x.labelledby)"""
    )


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
        page.evaluate(
            """()=>Object.defineProperty(window.crypto,'subtle',{configurable:true,value:{digest:async(_a,d)=>Uint8Array.from(await window.__sentinelTestSha256(Array.from(new Uint8Array(d)))).buffer}})"""
        )
        page.set_content(html, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(350)

        identity = page.evaluate("()=>({version:__SENTINEL_TEST__.appVersion,schema:__SENTINEL_TEST__.schemaVersion,rowLimit:__SENTINEL_TEST__.uiRowLimit})")
        check("Release identity and row limit", identity == {"version": "0.15.0-rc.2", "schema": 14, "rowLimit": 500}, identity)

        page.evaluate("""()=>{const p=__SENTINEL_TEST__.blankProject();p.mode='advanced';p.project.name='RC2 Acceptance';p.project.client='Validation Client';p.project.site='Validation Site';__SENTINEL_TEST__.setData(p);}""")
        page.locator("#advancedBtn").click()
        page.wait_for_timeout(100)

        # Visit the workspaces containing the filters found in the final audit.
        views = ["project", "evidence", "timeline", "findings", "coverage", "trace", "security"]
        failures: dict[str, list[dict[str, str]]] = {}
        for view in views:
            page.evaluate("view=>__SENTINEL_TEST__.setView(view)", view)
            page.wait_for_timeout(50)
            bad = accessible_name_failures(page)
            if bad:
                failures[view] = bad
        page.evaluate("()=>__SENTINEL_TEST__.setView('retest')")
        page.locator('[data-retest-tab="SUBMISSIONS"]').click()
        page.wait_for_timeout(50)
        bad = accessible_name_failures(page)
        if bad:
            failures["retest"] = bad
        page.evaluate("()=>__SENTINEL_TEST__.setView('coverage')")
        page.locator('[data-assurance-panel="GAPS"]').click()
        page.wait_for_timeout(50)
        bad = accessible_name_failures(page)
        if bad:
            failures["coverage-gaps"] = bad
        check("Visible form controls have accessible names", not failures, failures)

        # Command palette dialog semantics and focus restoration.
        page.evaluate("()=>__SENTINEL_TEST__.setView('dashboard')")
        origin = page.locator("#globalSearchBtn")
        origin.focus()
        origin.click()
        page.wait_for_timeout(50)
        search_state = page.evaluate("()=>({open:searchBox.classList.contains('open'),hidden:searchBox.getAttribute('aria-hidden'),active:document.activeElement.id,role:searchBox.getAttribute('role')})")
        check("Search opens as an accessible focused dialog", search_state == {"open": True, "hidden": "false", "active": "searchInput", "role": "dialog"}, search_state)
        page.keyboard.press("Tab")
        check("Search focus remains contained", page.evaluate("()=>searchBox.contains(document.activeElement)"), page.evaluate("()=>document.activeElement.id"))
        page.keyboard.press("Escape")
        page.wait_for_timeout(80)
        search_closed = page.evaluate("()=>({open:searchBox.classList.contains('open'),hidden:searchBox.getAttribute('aria-hidden'),active:document.activeElement.id})")
        check("Search closes and restores focus", search_closed == {"open": False, "hidden": "true", "active": "globalSearchBtn"}, search_closed)

        # Modal focus loop and restoration.
        trigger = page.locator("#dashQuickTest")
        trigger.focus()
        trigger.click()
        page.wait_for_timeout(80)
        check("Record modal opens", page.locator("#modalBack").evaluate("el=>el.classList.contains('open')"))
        page.locator("#modalSave").focus()
        page.keyboard.press("Tab")
        check("Forward Tab wraps inside the modal", page.evaluate("()=>document.activeElement.id==='modalClose'"), page.evaluate("()=>document.activeElement.id"))
        page.keyboard.press("Shift+Tab")
        check("Reverse Tab wraps inside the modal", page.evaluate("()=>document.activeElement.id==='modalSave'"), page.evaluate("()=>document.activeElement.id"))
        page.locator("#modalCancel").click()
        page.wait_for_timeout(80)
        check("Closing the modal restores trigger focus", page.evaluate("()=>document.activeElement.id==='dashQuickTest'"), page.evaluate("()=>document.activeElement.id"))

        # Large register guardrail: complete data retained, first 500 rows rendered.
        page.evaluate(
            """()=>{
              const p=__SENTINEL_TEST__.blankProject();p.mode='advanced';p.project.name='Register Limit Acceptance';p.project.client='Validation Client';
              p.assumptions=Array.from({length:600},(_,i)=>({id:`asm-${i}`,code:`ASM-${String(i+1).padStart(4,'0')}`,description:`Assumption ${i+1}`,basis:'Synthetic scale acceptance',owner:'Validation Analyst',impact:'Review',status:'UNVERIFIED',testIds:[],findingIds:[]}));
              __SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('registers');
            }"""
        )
        page.wait_for_timeout(180)
        rendered = page.locator('tr[data-type="assumption"]').count()
        note = page.locator("#registersView .render-limit-note").first.inner_text()
        retained = page.evaluate("()=>__SENTINEL_TEST__.getData().assumptions.length")
        check("Large register retains all records", retained == 600, retained)
        check("Large register renders the first 500 rows", rendered == 500, rendered)
        check("Large register clearly discloses the limit", "500" in note and "600" in note and "export" in note.lower(), note)
        profile = page.evaluate("()=>{const p=__SENTINEL_TEST__.blankProject();p.notes=Array.from({length:5001},(_,i)=>({id:String(i)}));return __SENTINEL_TEST__.projectScaleProfile(p)}")
        check("Large-project profile activates above 5,000 records", profile["large"] is True and profile["total"] >= 5001, profile)
        page.screenshot(path=str(SCREENSHOT_PATH), full_page=True)

        # Build and paginate a representative governed report at Letter size.
        report_html = page.evaluate("""async()=>{__SENTINEL_TEST__.seedReportDemoProject();return await __SENTINEL_TEST__.buildStandaloneReportHtml();}""")
        report_page = context.new_page()
        report_page.set_content(report_html, wait_until="load", timeout=30000)
        report_page.pdf(path=str(PDF_PATH), format="Letter", print_background=True, prefer_css_page_size=True)
        report_page.close()
        doc = fitz.open(PDF_PATH)
        page_text = [p.get_text("text").strip() for p in doc]
        check("Representative Letter report has multiple pages", len(page_text) >= 3, len(page_text))
        check("Letter report page 2 is not blank", len(page_text[1]) > 50, page_text[1][:500])
        check("Executive Summary begins on page 2", "Executive Summary" in page_text[1], page_text[1][:1000])
        check("Report PDF contains no Page 0 footer", all("Page 0" not in t for t in page_text), [i + 1 for i, t in enumerate(page_text) if "Page 0" in t])
        check("Report PDF uses Page X of Y numbering", all(f"Page {i + 1} of {len(page_text)}" in t for i, t in enumerate(page_text)), [i + 1 for i, t in enumerate(page_text) if f"Page {i + 1} of {len(page_text)}" not in t])
        check("Report PDF has no accidental blank pages", all(len(t) > 20 for t in page_text), [i + 1 for i, t in enumerate(page_text) if len(t) <= 20])
        doc.close()

        material_console = [x for x in console_errors if not any(k in x.lower() for k in ["indexeddb", "localstorage", "securityerror", "storage"])]
        check("No uncaught browser exceptions", not errors, errors)
        check("No material console errors", not material_console, material_console)
        browser.close()


try:
    run()
except Exception as exc:
    RESULT["fatal"] = str(exc)
    RESULT["traceback"] = traceback.format_exc()
finally:
    RESULT["completed"] = dt.datetime.now(dt.timezone.utc).isoformat()
    RESULT["passed"] = bool(RESULT["assertions"]) and all(a["passed"] for a in RESULT["assertions"]) and "fatal" not in RESULT
    (OUT / "rc2_acceptance.json").write_text(json.dumps(RESULT, indent=2), encoding="utf-8")
    lines = [f"{'PASS' if RESULT['passed'] else 'FAIL'} {sum(a['passed'] for a in RESULT['assertions'])}/{len(RESULT['assertions'])}"]
    lines += [f"{'PASS' if a['passed'] else 'FAIL'} {a['name']}: {a['detail']}" for a in RESULT["assertions"]]
    if RESULT.get("fatal"):
        lines += ["FATAL " + RESULT["fatal"], RESULT.get("traceback", "")]
    (OUT / "rc2_acceptance.txt").write_text("\n".join(lines), encoding="utf-8")
    print(lines[0])
    if not RESULT["passed"]:
        raise SystemExit(1)
