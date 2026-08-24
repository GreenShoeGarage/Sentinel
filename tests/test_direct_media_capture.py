"""Direct camera, video, and microphone capture using Chromium fake media devices."""
from __future__ import annotations

import os
import traceback
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = launch_browser(p, [
        "--use-fake-device-for-media-stream",
        "--use-fake-ui-for-media-stream",
        "--autoplay-policy=no-user-gesture-required",
    ])
    try:
        origin_parts = urlsplit(URL)
        origin = f"{origin_parts.scheme}://{origin_parts.netloc}"
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        context.grant_permissions(["camera", "microphone"], origin=origin)
        page = context.new_page()
        page.set_default_timeout(30000)
        errors: list[str] = []
        page.on("dialog", lambda dialog: dialog.accept())
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();p.mode='advanced';p.settings.currentOperator='Capture Analyst';
          Object.assign(p.project,{name:'Direct Capture Project',client:'Client',site:'Field Site',lead:'Capture Analyst',classification:'CONTROLLED'});
          Object.assign(p.authorization,{status:'ACTIVE',reference:'AUTH-DIRECT-CAPTURE',sponsor:'Sponsor',authority:'Authority',emergencyContacts:'555',authorizedFacilities:'Field Site',authorizedAreas:'Authorized areas',excludedAreas:'Excluded areas',authorizedTechniques:'Photography and recording',prohibitedTechniques:'None',allowedHours:'Current period',photoRestrictions:'Authorized for this test',recordingRestrictions:'Authorized for this test',stopConditions:'Stop on request',escalation:'Call sponsor',evidenceHandling:'Local protected storage'});
          p.security.capture.maxVideoSeconds=10;p.security.capture.maxAudioSeconds=10;
          __SENTINEL_TEST__.setData(p);__SENTINEL_TEST__.setView('field');
        }""")

        cap = page.evaluate("__SENTINEL_TEST__.securityCapabilityState()")
        check("fake-media-capabilities-ready", cap["secureContext"] and cap["mediaDevices"] and cap["mediaRecorder"], cap)

        # Photo capture from the live local preview.
        page.click("#fieldCapturePhoto")
        page.wait_for_selector("#captureVideo")
        page.wait_for_function("document.querySelector('#captureVideo').videoWidth > 0", timeout=30000)
        dimensions = page.evaluate("({w:document.querySelector('#captureVideo').videoWidth,h:document.querySelector('#captureVideo').videoHeight})")
        check("direct-photo-preview-live", dimensions["w"] > 0 and dimensions["h"] > 0, dimensions)
        page.click("#capturePhotoNow")
        page.wait_for_selector("[data-capture-row]")
        photo = page.evaluate("""async () => {const q=await __SENTINEL_TEST__.getPendingCaptures();const x=q.find(v=>v.kind==='PHOTO');return x?{id:x.id,size:x.blob.size,mime:x.mimeType,source:x.source}:null}""")
        check("direct-photo-staged", bool(photo) and photo["size"] > 0 and photo["mime"].startswith("image/"), photo)
        page.click("#modalCancel")

        # Video capture and recording-state feedback.
        page.click("#fieldCaptureVideo")
        page.wait_for_selector("#recordStartBtn")
        page.wait_for_function("document.querySelector('#captureVideo').videoWidth > 0", timeout=30000)
        page.click("#recordStartBtn")
        page.wait_for_function("document.querySelector('#recordingIndicator .recording-dot') !== null")
        check("direct-video-recording-feedback", "Recording" in page.locator("#captureStatusText").inner_text() or page.locator("#recordingIndicator .recording-dot").count() == 1)
        page.wait_for_timeout(1400)
        page.click("#recordStopBtn")
        page.wait_for_selector("[data-capture-row]")
        video = page.evaluate("""async () => {const q=await __SENTINEL_TEST__.getPendingCaptures();const x=q.find(v=>v.kind==='VIDEO');return x?{id:x.id,size:x.blob.size,mime:x.mimeType,duration:x.duration}:null}""")
        check("direct-video-staged", bool(video) and video["size"] > 0 and video["mime"].startswith("video/") and video["duration"] > 0, video)
        page.click("#modalCancel")

        # Audio capture through MediaRecorder.
        page.click("#fieldCaptureAudio")
        page.wait_for_selector("#recordStartBtn")
        page.click("#recordStartBtn")
        page.wait_for_function("document.querySelector('#recordingIndicator .recording-dot') !== null")
        page.wait_for_timeout(1400)
        page.click("#recordStopBtn")
        page.wait_for_selector("[data-capture-row]")
        audio = page.evaluate("""async () => {const q=await __SENTINEL_TEST__.getPendingCaptures();const x=q.find(v=>v.kind==='AUDIO');return x?{id:x.id,size:x.blob.size,mime:x.mimeType,duration:x.duration}:null}""")
        check("direct-audio-staged", bool(audio) and audio["size"] > 0 and audio["mime"].startswith("audio/") and audio["duration"] > 0, audio)

        queue = page.evaluate("""async () => (await __SENTINEL_TEST__.getPendingCaptures()).map(x=>({id:x.id,kind:x.kind,size:x.blob.size,source:x.source}))""")
        check("all-direct-media-recoverable-in-queue", {x["kind"] for x in queue} == {"PHOTO", "VIDEO", "AUDIO"} and all(x["size"] > 0 for x in queue), queue)
        page.click("#modalCancel")

        committed = page.evaluate("""async () => {const q=await __SENTINEL_TEST__.getPendingCaptures(),out=[];for(const item of q)out.push(await __SENTINEL_TEST__.commitPendingCapture(item.id,{description:`Direct ${item.kind.toLowerCase()} acceptance capture`}));return out.map(x=>({kind:x.type,hash:x.hash,verified:x.hashVerified,designation:x.designation,source:x.acquisition?.sourceDescription}));}""")
        check("direct-media-commits-as-verified-originals", len(committed) == 3 and all(x["hash"] and x["verified"] is True and x["designation"] == "ORIGINAL" for x in committed), committed)
        check("direct-media-queue-cleared-after-commit", page.evaluate("__SENTINEL_TEST__.getPendingCaptures()") == [])
        audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("direct-media-project-audit", audit["ok"], audit)
        check("direct-media-runtime-clean", not errors, errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_direct_media_capture_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
