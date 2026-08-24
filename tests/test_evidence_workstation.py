"""Evidence ingestion, provenance, derivation, comparison, Photo Log, and immutability checks."""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, ASSETS, launch_browser

IMAGE = str(ASSETS / "sample_evidence.png")
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


def drag(page, box, x1: float, y1: float, x2: float, y2: float) -> None:
    page.mouse.move(box["x"] + box["width"] * x1, box["y"] + box["height"] * y1)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] * x2, box["y"] + box["height"] * y2, steps=6)
    page.mouse.up()


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1500, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(20000)
        errors: list[str] = []
        dialogs: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        audit = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject(),org=crypto.randomUUID(),site=crypto.randomUUID(),asset=crypto.randomUUID(),control=crypto.randomUUID();
          Object.assign(p.project,{name:'Evidence Workstation Test',client:'Test Client',lead:'Analyst One',site:'Lab',startDate:'2026-08-23',endDate:'2026-08-24',classification:'CLIENT CONFIDENTIAL',purpose:'Validate evidence workbench',scope:'Authorized local test'});
          Object.assign(p.authorization,{status:'AUTHORIZED',reference:'AUTH-EV-001',sponsor:'Sponsor',authority:'Authority',emergencyContacts:'555-0100',authorizedFacilities:'Lab',authorizedAreas:'Test area',excludedAreas:'None',authorizedTechniques:'Evidence documentation',prohibitedTechniques:'None',allowedHours:'All',stopConditions:'On request',escalation:'Call sponsor',evidenceHandling:'Local vault'});
          p.sites=[{id:org,code:'ORG-001',name:'Org',type:'ORGANIZATION',parentId:null},{id:site,code:'SITE-001',name:'Lab',type:'SITE',parentId:org},{id:asset,code:'ASSET-001',name:'Test Door',type:'ASSET',parentId:site}];
          p.controls=[{id:control,code:'CTRL-001',type:'Badge reader',locationId:asset,intended:'Restrict entry',configuration:'Test configuration',condition:'GOOD',evidenceIds:[]}];
          p.settings.currentOperator='Analyst One'; return __SENTINEL_TEST__.setData(p);
        }""")
        check("evidence-fixture-audit", audit["ok"], audit)

        page.locator('[data-view="evidence"]').click()
        page.locator("#addEvidence").click()
        page.locator("#m_type").select_option("PHOTO")
        page.locator("#m_control").select_option(label="CTRL-001")
        page.locator("#m_file").set_input_files(IMAGE)
        page.locator("#m_desc").fill("Original evidence image for workstation validation.")
        page.locator("#m_caption").fill("Original test image")
        page.locator("#m_photographer").fill("Analyst One")
        page.locator("#m_source_device").fill("Test Camera")
        page.locator("#m_source_desc").fill("Controlled evidence acquisition")
        page.locator("#m_tags").fill("door, validation")
        page.locator("#modalSave").click()
        page.wait_for_selector("[data-evidence-workbench]")
        page.wait_for_timeout(500)

        original = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        check("original-binary-stored", original["blobStored"] is True and original["binaryAvailable"] is True, original)
        check("original-sha256", len(original["hash"]) == 64, original["hash"])
        check("embedded-image-dimensions", original["embeddedMetadata"].get("width") == 960 and original["embeddedMetadata"].get("height") == 640, original["embeddedMetadata"])
        check("acquisition-metadata", original["acquisition"].get("sourceDevice") == "Test Camera" and original["acquisition"].get("sourceDescription") == "Controlled evidence acquisition", original["acquisition"])
        check("initial-verification-history", len(original["verificationHistory"]) == 1 and original["verificationHistory"][0]["result"] == "VERIFIED", original["verificationHistory"])
        check("initial-custody-entry", len(original["custody"]) == 1 and original["custody"][0]["action"] == "COLLECTED", original["custody"])
        check("photo-log-default-inclusion", original["photoLog"]["includeInReport"] is True)
        check("thumbnail-rendered", page.locator('[data-evidence-thumb] img').count() == 1)

        original_id = original["id"]
        original_hash = original["hash"]
        page.locator("[data-evidence-workbench]").first.click()
        page.wait_for_selector("#ew_annotate")
        check("image-preview-rendered", page.locator(".evidence-preview img").count() == 1)
        check("control-relationship-displayed", original["controlId"] and "CTRL-001" in page.locator(".evidence-detail-grid").inner_text())

        before_verify = len(original["verificationHistory"])
        page.locator("#ew_verify").click()
        page.wait_for_timeout(700)
        verified = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        check("manual-verification-appended", len(verified["verificationHistory"]) == before_verify + 1, verified["verificationHistory"])
        check("manual-verification-passes", verified["hashVerified"] is True and verified["verificationHistory"][-1]["result"] == "VERIFIED")

        page.locator("#ew_custody").click()
        page.locator("#m_action").select_option("REVIEWED")
        page.locator("#m_from").fill("Analyst One")
        page.locator("#m_to").fill("Quality Reviewer")
        page.locator("#m_note").fill("Reviewed for report inclusion.")
        page.locator("#modalSave").click()
        page.wait_for_selector("#ew_custody")
        page.wait_for_timeout(300)
        custody_record = page.evaluate("__SENTINEL_TEST__.getData().evidence[0]")
        check("custody-entry-appended", any(entry["action"] == "REVIEWED" and entry["to"] == "Quality Reviewer" for entry in custody_record["custody"]), custody_record["custody"])
        check("current-custodian-display", "Quality Reviewer" in page.locator(".evidence-detail-grid").inner_text())

        page.locator("#ew_annotate").click()
        page.wait_for_selector("#evidenceEditorCanvas")
        canvas = page.locator("#evidenceEditorCanvas")
        box = canvas.bounding_box()
        check("editor-canvas-visible", bool(box) and box["width"] > 300 and box["height"] > 200, box)
        drag(page, box, 0.12, 0.14, 0.42, 0.43)  # default BOX
        page.locator('[data-editor-tool="REDACT"]').click()
        drag(page, box, 0.48, 0.36, 0.68, 0.53)
        page.locator("#editorRotateRight").click()
        page.wait_for_timeout(250)
        page.locator("#editorUndo").click()
        page.wait_for_timeout(250)
        page.locator("#editorRotateRight").click()
        page.wait_for_timeout(250)
        check("editor-operation-list", page.locator("#editorOpList .editor-op").count() >= 3, page.locator("#editorOpList").inner_text())
        page.locator("#editorDerivation").fill("Box callout, opaque redaction, and clockwise rotation for report use.")
        page.locator("#editorCaption").fill("Annotated and redacted test image")
        page.locator("#modalSave").click()
        page.wait_for_selector("#ew_compare", timeout=20000)
        page.wait_for_timeout(500)

        all_evidence = page.evaluate("__SENTINEL_TEST__.getData().evidence")
        check("derived-record-created", len(all_evidence) == 2, all_evidence)
        source = next(item for item in all_evidence if item["id"] == original_id)
        derived = next(item for item in all_evidence if item["id"] != original_id)
        check("source-hash-unchanged", source["hash"] == original_hash, source["hash"])
        check("derived-lineage", derived["designation"] == "DERIVED" and derived["originalEvidenceId"] == original_id, derived)
        check("derived-hash-distinct", len(derived["hash"]) == 64 and derived["hash"] != original_hash, derived["hash"])
        check("derived-binary-verified", derived["blobStored"] is True and derived["hashVerified"] is True)
        operations = [operation.get("type") for operation in derived["transformations"][0]["operations"]]
        check("transformation-history", all(tool in operations for tool in ["BOX", "REDACT", "ROTATE"]), operations)
        check("derived-provenance", len(derived["verificationHistory"]) >= 1 and len(derived["custody"]) >= 1, derived)

        page.locator("#ew_compare").click()
        page.wait_for_selector("#compareSlider")
        page.locator("#compareSlider").fill("72")
        page.wait_for_timeout(150)
        check("lineage-comparison-rendered", page.locator(".compare-stage img").count() == 2)
        page.locator("#modalClose").click()
        page.wait_for_timeout(150)

        page.locator('[data-evidence-tab="PHOTOLOG"]').click()
        page.wait_for_timeout(500)
        check("photo-log-has-original-and-derived", page.locator(".photo-log-card").count() == 2)
        standalone = page.evaluate("__SENTINEL_TEST__.buildStandaloneReportHtml()")
        check("standalone-report-photo-log", "Photo Log Appendix" in standalone and "Annotated and redacted test image" in standalone)
        check("standalone-report-embeds-image", "data:image/" in standalone)
        check("standalone-report-classification", "CLIENT CONFIDENTIAL" in standalone)

        immutable = page.evaluate("""async id => {
          const f=new File([new Uint8Array([1,2,3,4])],'different.bin',{type:'application/octet-stream'});
          try { await __SENTINEL_TEST__.storeEvidenceBlob(id,f); return 'ALLOWED'; }
          catch (error) { return error.message; }
        }""", original_id)
        check("immutable-original-enforced", immutable != "ALLOWED" and ("immutable" in immutable.lower() or "does not match" in immutable.lower()), immutable)

        audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("evidence-project-audit", audit["ok"], audit)
        check("evidence-workstation-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_evidence_workstation_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
