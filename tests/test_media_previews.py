"""Browser-supported audio, video, text, and PDF preview checks."""
from __future__ import annotations

import os
import traceback
from playwright.sync_api import sync_playwright
from common import URL, ASSETS, launch_browser

records = [
    (str(ASSETS / "sample_note.txt"), "NOTE", "Text note"),
    (str(ASSETS / "sample_audio.wav"), "AUDIO", "Audio note"),
    (str(ASSETS / "sample_video.webm"), "VIDEO", "Video note"),
    (str(ASSETS / "sample_document.pdf"), "DOCUMENT", "PDF document"),
]
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1400, "height": 950})
        page.set_default_timeout(20000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text and "404" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();p.project.name='Media Preview Validation';p.settings.currentOperator='Media Tester';__SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('evidence')}")

        for path, evidence_type, caption in records:
            page.locator("#addEvidence").click()
            page.locator("#m_file").set_input_files(path)
            page.locator("#m_type").select_option(evidence_type)
            page.locator("#m_caption").fill(caption)
            page.locator("#m_collector").fill("Media Tester")
            page.locator("#modalSave").click()
            page.locator("#modalBack").wait_for(state="hidden")

        evidence = page.evaluate("__SENTINEL_TEST__.getData().evidence")
        check("four-media-records", len(evidence) == 4, evidence)
        by_caption = {item["photoLog"]["caption"]: item for item in evidence}
        check("audio-duration-captured", (by_caption["Audio note"]["embeddedMetadata"].get("duration") or 0) > 0, by_caption["Audio note"]["embeddedMetadata"])
        video_meta = by_caption["Video note"]["embeddedMetadata"]
        check("video-duration-captured", (video_meta.get("duration") or 0) > 0, video_meta)
        check("video-dimensions-captured", video_meta.get("width") == 640 and video_meta.get("height") == 426, video_meta)

        expected = {
            "Text note": ".evidence-preview pre",
            "Audio note": ".evidence-preview audio",
            "Video note": ".evidence-preview video",
            "PDF document": ".evidence-preview iframe",
        }
        for caption, selector in expected.items():
            record_id = by_caption[caption]["id"]
            page.locator(f'[data-evidence-workbench="{record_id}"]').first.click()
            page.wait_for_selector(selector, state="attached")
            check(f"preview-{caption.lower().replace(' ', '-')}", page.locator(selector).count() == 1)
            page.locator("#modalClose").click()

        check("media-preview-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_media_previews_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
