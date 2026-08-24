"""Standalone Photo Log, HTML report, and Markdown report export checks."""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, ASSETS, launch_browser

IMAGE = str(ASSETS / "sample_evidence.png")
TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp"))
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1500, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(25000)
        errors: list[str] = []
        dialogs: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject(),org=crypto.randomUUID(),site=crypto.randomUUID();
          Object.assign(p.project,{name:'Report Export Test',client:'Client',lead:'Analyst',site:'Site',startDate:'2026-08-23',endDate:'2026-08-24',purpose:'Validate reports',scope:'Authorized evidence reporting',classification:'CLIENT CONFIDENTIAL'});
          Object.assign(p.authorization,{status:'AUTHORIZED',reference:'AUTH-RPT',sponsor:'Sponsor',authority:'Authority',emergencyContacts:'555',authorizedFacilities:'Site',authorizedAreas:'Area',excludedAreas:'None',authorizedTechniques:'Documentation',prohibitedTechniques:'None',allowedHours:'All',stopConditions:'On request',escalation:'Call sponsor',evidenceHandling:'Local'});
          p.sites=[{id:org,code:'ORG-001',name:'Org',type:'ORGANIZATION',parentId:null},{id:site,code:'SITE-001',name:'Site',type:'SITE',parentId:org}];p.settings.currentOperator='Analyst';p.assurance.samplingBasis='All reportable records in the fixture were reviewed.';p.assurance.samplingLimitations='Fixture scope is limited to report export behavior.';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence');
        }""")
        page.click("#addEvidence")
        page.select_option("#m_type", "PHOTO")
        page.set_input_files("#m_file", IMAGE)
        page.fill("#m_caption", "Report photograph")
        page.fill("#m_desc", "Photographic evidence included in report.")
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        page.wait_for_timeout(500)

        page.click('[data-evidence-tab="PHOTOLOG"]')
        page.wait_for_selector("#printPhotoLog")
        with page.expect_download(timeout=30000) as info:
            page.click("#printPhotoLog")
        photo_path = TMP / info.value.suggested_filename
        info.value.save_as(str(photo_path))
        photo_html = photo_path.read_text(encoding="utf-8")
        check("photo-log-export-heading", "Photo Log Appendix" in photo_html)
        check("photo-log-export-embeds-image", "data:image/" in photo_html)
        check("photo-log-export-classification", "CLIENT CONFIDENTIAL" in photo_html)
        check("photo-log-export-hash", "SHA-256" in photo_html)

        page.click("#advancedBtn")
        page.locator('[data-view="coverage"]').click()
        page.locator('[data-assurance-panel="COMPLETENESS"]').click()
        page.click("#openSignoff")
        page.check("#m_attest")
        page.click("#modalSave")
        page.wait_for_timeout(150)
        check("assurance-signoff-current", page.evaluate("__SENTINEL_TEST__.assuranceSignOffState().state") == "CURRENT")

        page.locator('[data-view="report"]').click()
        page.wait_for_selector("#htmlReport")
        readiness = page.evaluate("__SENTINEL_TEST__.reportReadiness(__SENTINEL_TEST__.getData())")
        check("report-ready", readiness["ready"], readiness)

        with page.expect_download(timeout=30000) as info:
            page.click("#htmlReport")
        html_path = TMP / info.value.suggested_filename
        info.value.save_as(str(html_path))
        report_html = html_path.read_text(encoding="utf-8")
        check("html-report-photo-caption", "Report photograph" in report_html)
        check("html-report-embeds-image", "data:image/" in report_html)
        check("html-report-classification", "CLIENT CONFIDENTIAL" in report_html)
        check("html-report-version", "SENTINEL v0.13.5" in report_html and "Schema 13" in report_html)

        with page.expect_download(timeout=30000) as info:
            page.click("#mdReport")
        markdown_path = TMP / info.value.suggested_filename
        info.value.save_as(str(markdown_path))
        markdown = markdown_path.read_text(encoding="utf-8")
        check("markdown-photo-log-appendix", "## Photo Log Appendix" in markdown)
        check("markdown-photo-caption", "Report photograph" in markdown)
        check("markdown-classification", "CLIENT CONFIDENTIAL" in markdown)
        check("markdown-version-footer", "SENTINEL v0.13.5" in markdown and "Project Schema 13" in markdown)
        check("report-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_reports_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
