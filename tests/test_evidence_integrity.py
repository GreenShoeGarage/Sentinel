"""Evidence metadata-history and immutable-binary regression checks."""
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
        page = browser.new_page()
        page.set_default_timeout(18000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();p.settings.currentOperator='Integrity Tester';p.project.name='Integrity Validation';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence')}")
        page.click("#addEvidence")
        page.set_input_files("#m_file", IMAGE)
        page.select_option("#m_type", "PHOTO")
        page.fill("#m_caption", "Original caption")
        page.fill("#m_collector", "Integrity Tester")
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        record = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        record_id = record["id"]
        check("initial-metadata-history-empty", len(record["metadataHistory"]) == 0)

        page.locator(f'[data-evidence-edit="{record_id}"]').click()
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        unchanged = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        check("unchanged-save-no-history", len(unchanged["metadataHistory"]) == 0, unchanged["metadataHistory"])

        page.locator(f'[data-evidence-edit="{record_id}"]').click()
        page.fill("#m_caption", "Revised caption")
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        changed = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        check("changed-save-adds-history", len(changed["metadataHistory"]) == 1, changed["metadataHistory"])
        check("history-preserves-prior-caption", changed["metadataHistory"][0]["snapshot"]["photoLog"]["caption"] == "Original caption", changed["metadataHistory"])

        immutable = page.evaluate("""async id => {
          try { await __SENTINEL_TEST__.storeEvidenceBlob(id,new File([new TextEncoder().encode('different binary')],'different.txt',{type:'text/plain'})); return {ok:true}; }
          catch(error) { return {ok:false,message:error.message}; }
        }""", record_id)
        check("immutable-original-enforced", immutable["ok"] is False and ("immutable" in immutable["message"].lower() or "does not match" in immutable["message"].lower()), immutable)

        current = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        before = len(current["verificationHistory"])
        result = page.evaluate("""async () => {const e=__SENTINEL_TEST__.getData().evidence[0];const ok=await __SENTINEL_TEST__.verifyEvidenceRecord(e);return {ok,e};}""")
        check("direct-integrity-verification", result["ok"] is True and result["e"]["hashVerified"] is True, result)
        check("verification-history-appended", len(result["e"]["verificationHistory"]) == before + 1, result["e"]["verificationHistory"])
        check("integrity-state-verified", page.evaluate("__SENTINEL_TEST__.evidenceIntegrityState(__SENTINEL_TEST__.getData().evidence[0]).label") == "VERIFIED")
        check("integrity-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_integrity_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
