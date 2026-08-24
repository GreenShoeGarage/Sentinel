"""SENTINEL v0.13.5 shell consolidation, workflow, and responsive layout checks."""
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
        context = browser.new_context(viewport={"width": 1500, "height": 1000})
        page = context.new_page()
        page.set_default_timeout(20000)
        errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        check("cleanup-release-version", page.evaluate("__SENTINEL_TEST__.appVersion") == "0.13.5")
        check("four-row-shell-layout", page.evaluate("getComputedStyle(document.querySelector('.app')).gridTemplateRows.split(' ').length") == 4,
              page.evaluate("getComputedStyle(document.querySelector('.app')).gridTemplateRows"))
        geometry = page.evaluate("""() => {const b=document.querySelector('#classificationBanner').getBoundingClientRect(),w=document.querySelector('#workspace').getBoundingClientRect();return {bannerBottom:b.bottom,workspaceTop:w.top}}""")
        check("classification-workspace-no-overlap", geometry["workspaceTop"] + 1 >= geometry["bannerBottom"], geometry)
        check("desktop-mobile-menu-hidden", page.locator("#mobileMenuBtn").evaluate("e=>getComputedStyle(e).display==='none'"))
        check("inspector-collapsed-by-default", page.locator("#workspace").evaluate("e=>e.classList.contains('inspector-collapsed')"))

        # Project operations are consolidated in a single contextual menu.
        page.click("#projectMenuBtn")
        check("project-menu-opens", page.locator("#projectMenu").evaluate("e=>e.classList.contains('open')"))
        menu_text = page.locator("#projectMenu").inner_text()
        check("project-menu-complete", all(label in menu_text for label in [
            "New Project", "Open Project", "Save Now", "Save As Copy", "Export Project Package",
            "Export Encrypted Package", "Emergency Export", "Import Package", "Create Checkpoint", "Recovery"
        ]), menu_text)
        page.keyboard.press("Escape")
        check("project-menu-escape-closes", not page.locator("#projectMenu").evaluate("e=>e.classList.contains('open')"))

        # Navigation is organized by the assessment workflow rather than a flat list.
        page.click("#advancedBtn")
        group_titles = page.locator("#primaryNav .navtitle").all_inner_texts()
        check("workflow-navigation-groups", [x.upper() for x in group_titles] == ["WORKSPACE", "FIELDWORK", "ANALYSIS", "CLOSEOUT", "ADMINISTRATION"], group_titles)
        nav_text = page.locator("#primaryNav").inner_text()
        check("streamlined-navigation-labels", "Assurance" in nav_text and "Remediation & Retest" in nav_text and "Security & Storage" in nav_text, nav_text)

        # Desktop sidebar can be hidden and restored without disturbing the active view.
        before_width = page.locator("#mainContent").bounding_box()["width"]
        page.click("#sidebarToggleBtn")
        page.wait_for_timeout(200)
        check("sidebar-collapse", page.locator("#workspace").evaluate("e=>e.classList.contains('sidebar-collapsed')"))
        collapsed_width = page.locator("#mainContent").bounding_box()["width"]
        check("sidebar-collapse-reclaims-space", collapsed_width > before_width + 150, {"before": before_width, "after": collapsed_width})
        page.click("#sidebarToggleBtn")
        page.wait_for_timeout(200)
        check("sidebar-restore", not page.locator("#workspace").evaluate("e=>e.classList.contains('sidebar-collapsed')"))

        # Resizable navigation width is persisted as a device-local shell preference.
        handle = page.locator("#sidebarResize").bounding_box()
        initial_var = page.evaluate("parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width'))")
        page.mouse.move(handle["x"] + 2, handle["y"] + 120)
        page.mouse.down()
        page.mouse.move(handle["x"] + 42, handle["y"] + 120, steps=6)
        page.mouse.up()
        page.wait_for_timeout(100)
        resized_var = page.evaluate("parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-width'))")
        check("sidebar-resize", resized_var >= initial_var + 25, {"before": initial_var, "after": resized_var})
        check("sidebar-width-persisted", page.evaluate("JSON.parse(localStorage.getItem('sentinel.ui.shell.v1')).sidebarWidth") == resized_var)

        # Selecting a record opens the inspector only when it is useful.
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject(),loc=p.sites[0].id;
          p.mode='advanced'; p.project.name='UI Cleanup Validation';
          p.controls=[{id:crypto.randomUUID(),code:'CTRL-UI-001',type:'Badge reader',category:'ACCESS CONTROL',locationId:loc,location:'Main site',manufacturer:'',purpose:'Validate inspector',configuration:'Observed',condition:'SERVICEABLE',notes:'',evidenceIds:[]}];
          __SENTINEL_TEST__.setData(p); __SENTINEL_TEST__.setView('controls');
        }""")
        page.locator('tr[data-type="control"]').click()
        page.wait_for_timeout(150)
        check("record-selection-opens-inspector", not page.locator("#workspace").evaluate("e=>e.classList.contains('inspector-collapsed')"))
        check("inspector-shows-selected-record", "CTRL-UI-001" in page.locator("#inspector").inner_text(), page.locator("#inspector").inner_text())
        page.click("#modalClose")
        page.click("#inspectorCloseBtn")
        check("inspector-close-restores-workspace", page.locator("#workspace").evaluate("e=>e.classList.contains('inspector-collapsed')"))

        # Changing destinations always starts at the top instead of retaining stale scroll position.
        page.evaluate("""() => {
          __SENTINEL_TEST__.setView('project');
          const probe=document.createElement('div');probe.id='scrollProbe';probe.style.height='2600px';
          document.querySelector('#projectView').append(probe);document.querySelector('#mainContent').scrollTop=900;
        }""")
        check("scroll-probe-established", page.locator("#mainContent").evaluate("e=>e.scrollTop") > 400)
        page.locator('[data-view="evidence"]').click()
        page.wait_for_timeout(100)
        check("view-change-resets-scroll", page.locator("#mainContent").evaluate("e=>e.scrollTop") <= 1,
              page.locator("#mainContent").evaluate("e=>e.scrollTop"))

        # Blank dashboard provides lifecycle orientation and a useful next action.
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('dashboard')}")
        dash_text = page.locator("#dashboardView").inner_text()
        check("dashboard-lifecycle-orientation", all(step in dash_text for step in ["SCOPE", "PLAN", "RECON", "TEST", "OBSERVE", "EVIDENCE", "FINDINGS", "REPORT", "RETEST"]), dash_text)
        check("dashboard-next-action", page.locator("#dashNextAction").count() == 1 and page.locator("#dashNextAction").is_visible())

        # Mobile shell: no banner/content overlap, compact footer, navigable drawer, and no horizontal page overflow.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(180)
        mobile_geometry = page.evaluate("""() => {const b=document.querySelector('#classificationBanner').getBoundingClientRect(),w=document.querySelector('#workspace').getBoundingClientRect(),f=document.querySelector('.footer').getBoundingClientRect();return {bannerBottom:b.bottom,workspaceTop:w.top,footerHeight:f.height,scrollWidth:document.documentElement.scrollWidth,innerWidth:innerWidth}}""")
        check("mobile-shell-no-overlap", mobile_geometry["workspaceTop"] + 1 >= mobile_geometry["bannerBottom"], mobile_geometry)
        check("mobile-empty-inspector-closed", page.locator("#workspace").evaluate("e=>e.classList.contains('inspector-collapsed')") and not page.locator("#inspectorBackdrop").evaluate("e=>e.classList.contains('open')"))
        check("mobile-footer-compact", mobile_geometry["footerHeight"] <= 42, mobile_geometry)
        check("mobile-no-page-overflow", mobile_geometry["scrollWidth"] <= mobile_geometry["innerWidth"] + 1, mobile_geometry)
        check("mobile-menu-visible", page.locator("#mobileMenuBtn").is_visible())
        page.click("#mobileMenuBtn")
        check("mobile-drawer-opens", page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))
        check("mobile-project-files-consolidated", page.locator("#sidebarProjectMenuBtn").is_visible() and page.locator("#appSidebar .project-menu-item").count() == 0)
        page.click("#mobileMenuCloseBtn")
        check("mobile-close-control", not page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))

        check("cleanup-no-page-errors", not errors, errors)
        check("cleanup-no-console-errors", not console_errors, console_errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_ui_cleanup_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
