"""Security workspace, handling banner, capture controls, and responsive-layout checks."""
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
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(20000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.dismiss())
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          Object.assign(p.project,{name:'Security UI Project',classification:'CONTROLLED // CLIENT SENSITIVE'});
          p.mode='advanced';p.security.handlingBanner=true;p.security.handlingInstructions='Authorized assessment personnel only.';
          __SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('security');
        }""")
        page.wait_for_timeout(150)

        check("classification-banner-visible", page.locator("#classificationBanner").is_visible(), page.locator("#classificationBanner").inner_text())
        banner_text = page.locator("#classificationBanner").inner_text()
        check("classification-banner-content", "CONTROLLED // CLIENT SENSITIVE" in banner_text and "Authorized assessment personnel only" in banner_text, banner_text)
        security_text = page.locator("#securityView").inner_text()
        check("security-workspace-sections", all(x in security_text.lower() for x in ["workspace protection", "handling and export policy", "field capture", "operational disclosures"]), security_text)
        check("storage-meter-rendered", page.locator(".storage-meter").count() == 1 and "Storage" in security_text, security_text)
        check("browser-capabilities-rendered", all(x in security_text for x in ["Web Crypto", "IndexedDB", "Camera / microphone", "Storage estimate"]), security_text)
        check("encryption-controls-present", page.locator("#enableEncryptBtn").count() == 1 and page.locator("#securityExportEncrypted").count() == 1 and page.locator("#lockNowBtn").count() == 1)
        check("capture-controls-present-in-security", all(page.locator(selector).count() == 1 for selector in ["#secCapturePhoto", "#secCaptureVideo", "#secCaptureAudio"]))

        # Policy edits should persist in the canonical project model.
        page.fill("#sec_handlingInstructions", "Revised protected handling instructions.")
        page.dispatch_event("#sec_handlingInstructions", "change")
        page.wait_for_timeout(120)
        page.check("#sec_exportAck")
        page.wait_for_timeout(120)
        page.select_option("#sec_autoLock", "10")
        page.wait_for_timeout(120)
        page.fill("#sec_videoMax", "75")
        page.dispatch_event("#sec_videoMax", "change")
        page.wait_for_timeout(120)
        page.fill("#sec_audioMax", "180")
        page.dispatch_event("#sec_audioMax", "change")
        page.wait_for_timeout(300)
        sec = page.evaluate("__SENTINEL_TEST__.getData().security")
        check("security-policy-persists", sec["handlingInstructions"] == "Revised protected handling instructions." and sec["requireExportAcknowledgement"] is True and sec["autoLockMinutes"] == 10, sec)
        check("capture-policy-persists", sec["capture"]["maxVideoSeconds"] == 75 and sec["capture"]["maxAudioSeconds"] == 180, sec["capture"])

        page.evaluate("__SENTINEL_TEST__.setView('field')")
        field_text = page.locator("#fieldView").inner_text()
        check("field-capture-actions-present", all(x in field_text for x in ["CAPTURE PHOTO", "RECORD VIDEO", "RECORD AUDIO"]), field_text)
        page.evaluate("__SENTINEL_TEST__.setView('evidence')")
        evidence_text = page.locator("#evidenceView").inner_text()
        check("evidence-capture-actions-present", all(x in evidence_text for x in ["Capture Photo", "Record Video", "Record Audio"]), evidence_text)

        cap = page.evaluate("__SENTINEL_TEST__.securityCapabilityState()")
        check("security-capability-api", cap["secureContext"] is True and cap["webCrypto"] is True and cap["indexedDB"] is True and cap["storageEstimate"] is True, cap)
        storage = page.evaluate("__SENTINEL_TEST__.refreshStorageEstimate()")
        check("storage-estimate-api", storage["supported"] is True and storage["quota"] >= storage["usage"] >= 0, storage)

        # Mobile layout must keep field capture controls reachable without horizontal page overflow.
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("__SENTINEL_TEST__.setView('field')")
        page.wait_for_timeout(100)
        metrics = page.evaluate("({vw:document.documentElement.clientWidth,sw:document.documentElement.scrollWidth,buttons:[...document.querySelectorAll('#fieldView .capture-strip button')].map(b=>({text:b.textContent.trim(),w:b.getBoundingClientRect().width,visible:!!(b.offsetWidth||b.offsetHeight)}))})")
        check("mobile-field-capture-controls-visible", len(metrics["buttons"]) >= 3 and all(b["visible"] and b["w"] > 40 for b in metrics["buttons"]), metrics)
        check("mobile-security-layout-no-page-overflow", metrics["sw"] <= metrics["vw"] + 2, metrics)

        protected_css = page.evaluate("""() => {
          const style=[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules]}catch{return []}}).map(r=>r.cssText).join(' ');
          return style.includes('protected-preview') && style.includes('filter: blur');
        }""")
        check("protected-preview-css-present", protected_css)
        check("security-ui-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_security_ui_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
