"""Non-destructive image editor tool and crop regression checks."""
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


def drag(page, box, x1: float, y1: float, x2: float, y2: float) -> None:
    page.mouse.move(box["x"] + box["width"] * x1, box["y"] + box["height"] * y1)
    page.mouse.down()
    page.mouse.move(box["x"] + box["width"] * x2, box["y"] + box["height"] * y2, steps=7)
    page.mouse.up()


def prepare(page, name: str) -> None:
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
    page.evaluate(
        """name => {const p=__SENTINEL_TEST__.blankProject();p.project.name=name;p.settings.currentOperator='Editor Tester';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence')}""",
        name,
    )
    page.click("#addEvidence")
    page.select_option("#m_type", "PHOTO")
    page.set_input_files("#m_file", IMAGE)
    page.fill("#m_caption", "Editor source")
    page.click("#modalSave")
    page.wait_for_selector("[data-evidence-workbench]")
    page.click("[data-evidence-workbench]")
    page.wait_for_selector("#ew_annotate")
    page.click("#ew_annotate")
    page.wait_for_selector("#evidenceEditorCanvas")


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        # Tool suite except crop. Crop is isolated because it replaces the working canvas.
        context = browser.new_context(viewport={"width": 1600, "height": 1100})
        page = context.new_page()
        page.set_default_timeout(20000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        prepare(page, "Editor Tool Validation")
        canvas = page.locator("#evidenceEditorCanvas")
        box = canvas.bounding_box()
        check("editor-source-dimensions", page.evaluate("() => ({w:evidenceEditorCanvas.width,h:evidenceEditorCanvas.height})") == {"w": 960, "h": 640})

        page.click('[data-editor-tool="CIRCLE"]')
        drag(page, box, 0.10, 0.10, 0.28, 0.27)
        page.click('[data-editor-tool="ARROW"]')
        drag(page, box, 0.31, 0.20, 0.49, 0.34)
        page.click('[data-editor-tool="LABEL"]')
        page.fill("#editorLabelText", "Authorized Test")
        page.mouse.click(box["x"] + box["width"] * 0.20, box["y"] + box["height"] * 0.55)
        page.click('[data-editor-tool="MEASURE"]')
        drag(page, box, 0.14, 0.66, 0.45, 0.66)
        page.click('[data-editor-tool="BLUR"]')
        drag(page, box, 0.50, 0.45, 0.68, 0.62)
        page.click('[data-editor-tool="REDACT"]')
        drag(page, box, 0.72, 0.45, 0.88, 0.60)
        page.click('[data-editor-tool="BOX"]')
        drag(page, box, 0.55, 0.12, 0.82, 0.35)
        page.click("#editorRotateLeft")
        page.wait_for_timeout(250)
        page.click("#editorUndo")
        page.wait_for_timeout(250)
        page.click("#editorRotateRight")
        page.wait_for_timeout(250)

        operation_text = page.locator("#editorOpList").inner_text().upper()
        for label in ["CIRCLE", "ARROW", "LABEL", "MEASURE", "BLUR", "REDACT", "BOX", "ROTATE"]:
            check(f"editor-tool-{label.lower()}", label in operation_text, operation_text)
        check("undo-preserves-valid-history", "ROTATE" in operation_text and page.locator("#editorUndo").is_enabled(), operation_text)

        page.fill("#editorDerivation", "Validated circle, arrow, label, measurement, blur, redaction, box, rotation, and undo behavior.")
        page.fill("#editorCaption", "Extended annotated derivative")
        page.click("#modalSave")
        page.wait_for_selector("#ew_compare", timeout=20000)
        page.wait_for_timeout(400)
        data = page.evaluate("__SENTINEL_TEST__.getData()")
        check("multi-tool-derived-record", len(data["evidence"]) == 2)
        derived = data["evidence"][1]
        saved_types = [operation["type"] for operation in derived["transformations"][0]["operations"]]
        for tool in ["CIRCLE", "ARROW", "LABEL", "MEASURE", "BLUR", "REDACT", "BOX", "ROTATE"]:
            check(f"saved-operation-{tool.lower()}", tool in saved_types, saved_types)
        check("multi-tool-derived-verified", derived["hashVerified"] is True and derived["blobStored"] is True)
        check("multi-tool-runtime-clean", not errors, errors)
        context.close()

        # Isolated crop test.
        context = browser.new_context(viewport={"width": 1600, "height": 1100})
        page = context.new_page()
        page.set_default_timeout(20000)
        crop_errors: list[str] = []
        page.on("pageerror", lambda exc: crop_errors.append(str(exc)))
        page.on("console", lambda msg: crop_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        prepare(page, "Editor Crop Validation")
        canvas = page.locator("#evidenceEditorCanvas")
        original_dimensions = page.evaluate("() => ({w:evidenceEditorCanvas.width,h:evidenceEditorCanvas.height})")
        box = canvas.bounding_box()
        page.click('[data-editor-tool="CROP"]')
        page.wait_for_timeout(200)
        drag(page, box, 0.10, 0.10, 0.80, 0.80)
        page.wait_for_timeout(1000)
        cropped_dimensions = page.evaluate("() => ({w:evidenceEditorCanvas.width,h:evidenceEditorCanvas.height})")
        check("crop-changes-canvas-size", cropped_dimensions["w"] < original_dimensions["w"] and cropped_dimensions["h"] < original_dimensions["h"], {"before": original_dimensions, "after": cropped_dimensions})
        check("crop-operation-listed", "CROP" in page.locator("#editorOpList").inner_text().upper(), page.locator("#editorOpList").inner_text())
        page.fill("#editorDerivation", "Cropped derivative for validation.")
        page.fill("#editorCaption", "Cropped derivative")
        page.click("#modalSave")
        page.wait_for_selector("#ew_compare", timeout=20000)
        page.wait_for_timeout(400)
        crop_data = page.evaluate("__SENTINEL_TEST__.getData()")
        crop_derived = crop_data["evidence"][1]
        crop_types = [operation["type"] for operation in crop_derived["transformations"][0]["operations"]]
        check("saved-crop-operation", "CROP" in crop_types, crop_types)
        check("saved-crop-dimensions", crop_derived["embeddedMetadata"]["width"] == cropped_dimensions["w"] and crop_derived["embeddedMetadata"]["height"] == cropped_dimensions["h"], crop_derived["embeddedMetadata"])
        check("crop-source-unchanged", crop_data["evidence"][0]["embeddedMetadata"]["width"] == 960 and crop_data["evidence"][0]["embeddedMetadata"]["height"] == 640)
        check("crop-runtime-clean", not crop_errors, crop_errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_editor_tools_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
