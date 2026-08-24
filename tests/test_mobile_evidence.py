"""Mobile-width Evidence Vault, Photo Log, workbench, and modal-layer checks."""
from __future__ import annotations

import os
import traceback
from playwright.sync_api import sync_playwright
from common import URL, ASSETS, launch_browser

IMAGE = str(ASSETS / "sample_evidence.png")
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.set_default_timeout(20000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();p.project.name='Mobile Evidence';p.settings.currentOperator='Analyst';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence')}")
        page.click("#addEvidence")
        page.select_option("#m_type", "PHOTO")
        page.set_input_files("#m_file", IMAGE)
        page.fill("#m_caption", "Mobile evidence photograph")
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        page.wait_for_timeout(500)

        vault_metrics = page.evaluate("() => ({innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyScroll:document.body.scrollWidth,main:document.querySelector('main').scrollWidth})")
        check("mobile-vault-no-page-overflow", vault_metrics["scrollWidth"] <= vault_metrics["innerWidth"] + 2, vault_metrics)
        check("mobile-vault-card-visible", page.locator(".evidence-card").count() == 1)
        check("mobile-filter-controls-visible", page.locator("#ev_type").is_visible() and page.locator("#ev_integrity").is_visible())

        colors = page.evaluate("() => {const s=getComputedStyle(document.querySelector('#ev_type'));return {background:s.backgroundColor,color:s.color}}")
        check("mobile-filter-dark-theme-readable", colors["background"] != colors["color"], colors)

        page.click('[data-evidence-tab="PHOTOLOG"]')
        page.wait_for_timeout(300)
        photo_metrics = page.evaluate("() => ({innerWidth,scrollWidth:document.documentElement.scrollWidth})")
        check("mobile-photo-log-no-page-overflow", photo_metrics["scrollWidth"] <= photo_metrics["innerWidth"] + 2, photo_metrics)
        check("mobile-photo-log-card-visible", page.locator(".photo-log-card").count() == 1)

        page.click("[data-evidence-workbench]")
        page.wait_for_selector("#ew_annotate")
        page.wait_for_timeout(300)
        workbench_metrics = page.evaluate("() => ({innerWidth,scrollWidth:document.documentElement.scrollWidth,modal:document.querySelector('#modalBack .modal').getBoundingClientRect().toJSON(),modalZ:Number(getComputedStyle(document.querySelector('#modalBack')).zIndex),topbarZ:Number(getComputedStyle(document.querySelector('.topbar')).zIndex)})")
        check("mobile-workbench-no-page-overflow", workbench_metrics["scrollWidth"] <= workbench_metrics["innerWidth"] + 2, workbench_metrics)
        check("modal-above-topbar", workbench_metrics["modalZ"] > workbench_metrics["topbarZ"], workbench_metrics)
        check("mobile-workbench-toolbar-visible", page.locator("#ew_annotate").is_visible())

        page.click("#modalClose")
        page.click("#mobileMenuBtn")
        check("mobile-navigation-opens", page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))
        page.locator("#sidebarBackdrop").click(position={"x": 380, "y": 420})
        check("mobile-navigation-closes", not page.locator("#appSidebar").evaluate("e=>e.classList.contains('open')"))
        check("mobile-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_mobile_evidence_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
