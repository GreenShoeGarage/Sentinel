"""IndexedDB reload, Save As Copy, and complete project-package round-trip checks."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, ASSETS, launch_browser

IMAGE = str(ASSETS / "sample_evidence.png")
TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp"))
PACKAGE = TMP / "sentinel-package-roundtrip.sentinel"
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        context = browser.new_context(viewport={"width": 1500, "height": 1000}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(25000)
        errors: list[str] = []
        dialogs: list[tuple[str, str]] = []

        def handle_dialog(dialog):
            dialogs.append((dialog.type, dialog.message))
            if dialog.type == "prompt":
                dialog.accept("Persistence Copy")
            else:
                dialog.accept()

        page.on("dialog", handle_dialog)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        original_id = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          Object.assign(p.project,{name:'Persistence Original',client:'Client',lead:'Analyst',site:'Site',startDate:'2026-08-23',endDate:'2026-08-24',purpose:'Persistence validation',scope:'Authorized',classification:'CONTROLLED'});
          Object.assign(p.authorization,{status:'AUTHORIZED',reference:'AUTH-PERSIST',sponsor:'Sponsor',authority:'Authority',emergencyContacts:'555',authorizedFacilities:'Site',authorizedAreas:'Area',excludedAreas:'None',authorizedTechniques:'Documentation',prohibitedTechniques:'None',allowedHours:'All',stopConditions:'Stop',escalation:'Call',evidenceHandling:'Local'});
          p.settings.currentOperator='Analyst';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence');return p.id;
        }""")
        page.click("#addEvidence")
        page.select_option("#m_type", "PHOTO")
        page.set_input_files("#m_file", IMAGE)
        page.fill("#m_desc", "Persistence source")
        page.fill("#m_caption", "Persistence photograph")
        page.click("#modalSave")
        page.wait_for_selector("[data-evidence-workbench]")
        page.wait_for_timeout(500)
        source_before = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        page.evaluate("__SENTINEL_TEST__.save()")
        page.wait_for_function("document.querySelector('#autosaveText').textContent==='SAVED'")

        # Normal-origin reload must restore structured data and the binary.
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.wait_for_timeout(600)
        restored = page.evaluate("__SENTINEL_TEST__.getData()")
        check("project-restored-after-reload", restored["id"] == original_id and restored["project"]["name"] == "Persistence Original", restored["project"])
        check("evidence-metadata-restored", len(restored["evidence"]) == 1 and restored["evidence"][0]["hash"] == source_before["hash"], restored["evidence"])
        blob = page.evaluate("""async id => {const r=await __SENTINEL_TEST__.getEvidenceBlob(id);return r?{size:r.blob.size,filename:r.filename,sha:r.sha256}:null}""", restored["evidence"][0]["id"])
        check("evidence-binary-restored", bool(blob) and blob["size"] == source_before["size"] and blob["sha"] == source_before["hash"], blob)

        # Save As Copy must remap identifiers while preserving hashes and binaries.
        page.click("#projectMenuBtn")
        page.click("#saveAsBtn")
        page.wait_for_timeout(1800)
        copied = page.evaluate("__SENTINEL_TEST__.getData()")
        check("save-as-copy-project-id-remapped", copied["id"] != original_id, {"original": original_id, "copy": copied["id"]})
        check("save-as-copy-name", copied["project"]["name"] == "Persistence Copy", copied["project"]["name"])
        check("save-as-copy-evidence-id-remapped", copied["evidence"][0]["id"] != source_before["id"], copied["evidence"][0])
        check("save-as-copy-hash-preserved", copied["evidence"][0]["hash"] == source_before["hash"])
        copy_blob = page.evaluate("""async id => {const r=await __SENTINEL_TEST__.getEvidenceBlob(id);return r?{size:r.blob.size,sha:r.sha256}:null}""", copied["evidence"][0]["id"])
        check("save-as-copy-binary-copied", bool(copy_blob) and copy_blob["size"] == source_before["size"] and copy_blob["sha"] == source_before["hash"], copy_blob)

        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.wait_for_timeout(700)
        copied_reload = page.evaluate("__SENTINEL_TEST__.getData()")
        check("copy-restored-after-reload", copied_reload["id"] == copied["id"] and copied_reload["evidence"][0]["id"] == copied["evidence"][0]["id"], copied_reload)

        # Export a complete portable package from the copy.
        page.click("#projectMenuBtn")
        page.click("#exportBtn")
        page.check("#export_ack")
        with page.expect_download(timeout=30000) as download_info:
            page.locator(".secret-prompt button.primary").click()
        download = download_info.value
        download.save_as(str(PACKAGE))
        package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        check("package-format", package["format"] == "SENTINEL_PROJECT_PACKAGE" and package["formatVersion"] == 3 and package["schemaVersion"] == 13, {key: package.get(key) for key in ["format", "formatVersion", "schemaVersion"]})
        check("package-has-evidence-binary", len(package["evidence"]) == 1 and bool(package["evidence"][0]["data"]), package["evidence"])
        check("package-hash-matches-record", package["evidence"][0]["sha256"] == copied_reload["evidence"][0]["hash"])

        # Replace in memory, then import the package and verify restoration.
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();p.project.name='Temporary Import Target';__SENTINEL_TEST__.setData(p)}")
        page.set_input_files("#importInput", str(PACKAGE))
        page.wait_for_function("__SENTINEL_TEST__.getData().project.name==='Persistence Copy'", timeout=30000)
        page.wait_for_function("document.querySelector('#autosaveText').textContent==='SAVED'", timeout=15000)
        imported = page.evaluate("__SENTINEL_TEST__.getData()")
        check("package-project-restored", imported["id"] == copied_reload["id"] and imported["project"]["name"] == "Persistence Copy", imported["project"])
        imported_blob = page.evaluate("""async () => {const e=__SENTINEL_TEST__.getData().evidence[0],s=await __SENTINEL_TEST__.getEvidenceBlob(e.id);return {stored:!!s?.blob,size:s?.blob?.size,sha:s?.sha256,recordHash:e.hash,verified:e.hashVerified,binaryAvailable:e.binaryAvailable}}""")
        check("package-binary-verified-after-import", imported_blob["stored"] and imported_blob["sha"] == imported_blob["recordHash"] and imported_blob["verified"] is True and imported_blob["binaryAvailable"] is True, imported_blob)
        page.locator('[data-view="evidence"]').click()
        page.wait_for_timeout(900)
        check("thumbnail-regenerated-after-import", page.locator('[data-evidence-thumb] img').count() >= 1)
        audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("package-roundtrip-audit", audit["ok"], audit)
        check("persistence-runtime-clean", not errors, errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_package_persistence_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
