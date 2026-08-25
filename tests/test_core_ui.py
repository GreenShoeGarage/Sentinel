"""Core identity, navigation, validation, and responsive-behavior checks."""
from __future__ import annotations

import os
import traceback
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(15000)
        errors: list[str] = []
        console_errors: list[str] = []
        dialogs: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        check("document-title", page.title() == "SENTINEL — Physical Security Red Team Workbench", page.title())
        check("application-version", "v0.15.0-rc.2" in page.locator(".topbar .brand small").inner_text(), page.locator(".topbar .brand small").inner_text())
        hook = page.evaluate("({v:__SENTINEL_TEST__.appVersion,s:__SENTINEL_TEST__.schemaVersion,a:__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.blankProject())})")
        check("test-interface", hook["v"] == "0.15.0-rc.2" and hook["s"] == 14, hook)
        check("blank-project-audit", hook["a"]["ok"], hook["a"])
        check("indexeddb-real-origin", "IndexedDB" in page.locator("#storageLabel").inner_text(), page.locator("#storageLabel").inner_text())

        page.click("#globalSearchBtn")
        page.wait_for_timeout(80)
        check("command-palette-opens", page.locator("#searchBox").evaluate("e=>e.classList.contains('open')"))
        labels = page.locator("#searchResults").inner_text()
        check("evidence-and-assurance-commands-present", "Open Evidence Vault" in labels and "Verify All Evidence" in labels and "Open Assessment Assurance" in labels and "Open Traceability Graph" in labels, labels)
        page.press("#searchInput", "Escape")

        page.click("#advancedBtn")
        nav_results: list[tuple[str, bool]] = []
        for element in page.locator(".navitem").all():
            view = element.get_attribute("data-view")
            element.click()
            page.wait_for_timeout(20)
            nav_results.append((view or "", "active" in (page.locator(f"#{view}View").get_attribute("class") or "")))
        check("all-navigation-views", all(item[1] for item in nav_results), nav_results)

        # Regression: the Evidence settings object must retain Photo Log state.
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          p.evidence=[{id:crypto.randomUUID(),code:'E-0001',type:'PHOTO',filename:'x.png',designation:'ORIGINAL',photoLog:{caption:'Photo',includeInReport:false},tags:[]}];
          __SENTINEL_TEST__.setData(p); __SENTINEL_TEST__.setView('evidence');
        }""")
        page.locator('[data-evidence-tab="PHOTOLOG"]').click()
        page.wait_for_timeout(80)
        check("photo-log-tab-persists", page.evaluate("__SENTINEL_TEST__.getData().settings.evidenceView.tab") == "PHOTOLOG")
        check("photo-log-renders", page.locator(".photo-log-card").count() == 1, page.locator("#evidenceView").inner_text())

        # Regression: saving unchanged metadata must not create a false history entry.
        page.locator("[data-evidence-edit]").click()
        page.wait_for_timeout(50)
        page.locator("#modalSave").click()
        page.wait_for_timeout(80)
        history_count = page.evaluate("__SENTINEL_TEST__.getData().evidence[0].metadataHistory.length")
        check("no-op-metadata-save-not-recorded", history_count == 0, history_count)

        # Blank report readiness is intentionally blocked.
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('report')}")
        before = len(dialogs)
        page.locator("#htmlReport").click()
        page.wait_for_timeout(50)
        check("report-readiness-guard", len(dialogs) > before and "blocked" in dialogs[-1].lower(), dialogs[-1] if dialogs else "")

        # Required-field validation remains active in strengthened registers.
        page.locator('[data-view="observations"]').click()
        page.locator("#addObs").click()
        before = len(dialogs)
        page.locator("#modalSave").click()
        page.wait_for_timeout(50)
        check("observation-required-field-validation", len(dialogs) > before and "description is required" in dialogs[-1].lower(), dialogs[-1] if dialogs else "")
        page.locator("#modalCancel").click()

        page.click("#advancedBtn")
        page.locator('[data-view="registers"]').click()
        page.locator("#addIssue").click()
        # Set and submit synchronously so unrelated autosave timing cannot replace modal values
        # between the field action and validation click.
        page.evaluate("""() => {
          document.querySelector('#m_desc').value='Issue';
          document.querySelector('#m_status').value='RESOLVED';
        }""")
        before = len(dialogs)
        page.evaluate("document.querySelector('#modalSave').click()")
        page.wait_for_timeout(50)
        check("issue-resolution-validation", len(dialogs) > before and "resolution" in dialogs[-1].lower(), dialogs[-1] if dialogs else "")
        page.locator("#modalCancel").click()

        pointer = page.evaluate("""() => {
          const z=document.createElement('div');z.className='map-zone';document.body.append(z);
          const q=document.createElement('div');q.className='map-path';document.body.append(q);
          return [getComputedStyle(z).pointerEvents,getComputedStyle(q).pointerEvents];
        }""")
        check("map-annotations-selectable", pointer == ["auto", "auto"], pointer)

        page.set_viewport_size({"width": 600, "height": 900})
        page.click("#mobileMenuBtn")
        page.wait_for_timeout(50)
        check("mobile-sidebar-opens", page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))
        check("mobile-menu-aria-expanded", page.locator("#mobileMenuBtn").get_attribute("aria-expanded") == "true")
        page.locator("#sidebarBackdrop").click(position={"x": 590, "y": 450})
        check("mobile-sidebar-closes", not page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))

        check("no-page-errors", not errors, errors)
        check("no-console-errors", not console_errors, console_errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_core_ui_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
