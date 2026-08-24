"""Encrypted offline capture-queue recovery and immutable evidence commit checks."""
from __future__ import annotations

import os
import traceback
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

PASS = "Capture-queue-passphrase-2026"
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


def submit_secret(page, value: str, confirmation: str | None = None) -> None:
    page.wait_for_selector(".secret-prompt-back")
    page.fill("#sp_one", value)
    if confirmation is not None:
        page.fill("#sp_two", confirmation)
    page.locator(".secret-prompt button.primary").click()


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.set_default_timeout(30000)
        errors: list[str] = []
        page.on("dialog", lambda dialog: dialog.accept())
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        seed = page.evaluate("""async () => {
          const p=__SENTINEL_TEST__.blankProject();
          Object.assign(p.project,{name:'Capture Recovery Project',client:'Client',site:'Field Site',lead:'Field Analyst',classification:'CONTROLLED'});
          Object.assign(p.authorization,{status:'ACTIVE',reference:'AUTH-CAPTURE',sponsor:'Sponsor',authority:'Authority',emergencyContacts:'555',authorizedFacilities:'Site',authorizedAreas:'Area',excludedAreas:'None',authorizedTechniques:'Authorized documentation',prohibitedTechniques:'None',allowedHours:'All',photoRestrictions:'Authorized',recordingRestrictions:'Authorized',stopConditions:'Stop',escalation:'Call',evidenceHandling:'Local encrypted storage'});
          p.mode='advanced';p.settings.currentOperator='Field Analyst';
          const controlId=crypto.randomUUID(),testId=crypto.randomUUID();
          p.controls=[{id:controlId,code:'CTRL-001',name:'Reception control',type:'Reception',domain:'Reception',locationId:'',location:'Lobby',purpose:'Challenge visitors',configuration:'Observed',condition:'Operational'}];
          p.tests=[{id:testId,code:'T-001',title:'Authorized field capture test',objective:'Document response',controlId,locationId:'',location:'Lobby',preconditions:'Authorization confirmed',authorizationRequirement:'Authorized documentation',method:'Observe only',expected:'Visitor challenged',successCriteria:'Control functions',failureCriteria:'Control does not function',safety:'Stop on request',personnel:'Field Analyst',equipment:'SENTINEL device',scheduled:'',actualStart:new Date().toISOString(),actualEnd:'',result:'IN PROGRESS'}];
          __SENTINEL_TEST__.setData(p);await __SENTINEL_TEST__.save();return {projectId:p.id,testId};
        }""")
        page.evaluate("__SENTINEL_TEST__.setView('security')")
        page.click("#enableEncryptBtn")
        submit_secret(page, PASS, PASS)
        page.wait_for_function("__SENTINEL_TEST__.projectStorageEncrypted() === true", timeout=60000)

        staged = page.evaluate("""async () => {
          const first=await __SENTINEL_TEST__.stageCapture(new Blob(['recoverable-photo-bytes'],{type:'image/png'}),{kind:'PHOTO',filename:'recoverable.png',actor:'Field Analyst',notes:'Queued while offline'});
          const second=await __SENTINEL_TEST__.stageCapture(new Blob(['recoverable-audio-bytes'],{type:'audio/webm'}),{kind:'AUDIO',filename:'recoverable.webm',actor:'Field Analyst',notes:'Second queued capture'});
          return {first:first.id,second:second.id};
        }""")
        queue_state = page.evaluate("""async id => ({
          logical:(await __SENTINEL_TEST__.getPendingCaptures()).map(x=>({id:x.id,kind:x.kind,size:x.blob?.size,testId:x.testId})),
          plain:(await __SENTINEL_TEST__.rawIdbAll('captureQueue')).filter(x=>x.projectId===id).length,
          secure:(await __SENTINEL_TEST__.rawIdbAll('secureCaptureQueue')).filter(x=>x.projectId===id).length
        })""", seed["projectId"])
        check("encrypted-captures-staged", len(queue_state["logical"]) == 2 and all(x["size"] > 0 for x in queue_state["logical"]), queue_state)
        check("capture-queue-has-no-plaintext-copy", queue_state["plain"] == 0 and queue_state["secure"] == 2, queue_state)
        check("captures-auto-link-active-test", all(x["testId"] == seed["testId"] for x in queue_state["logical"]), queue_state["logical"])

        page.evaluate("__SENTINEL_TEST__.lockWorkspace('Capture recovery reload')")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.fill("#unlockPassphrase", PASS)
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#lockScreen').classList.contains('open')", timeout=60000)
        recovered = page.evaluate("__SENTINEL_TEST__.getPendingCaptures()")
        check("capture-queue-survives-lock-and-reload", len(recovered) == 2 and {x["id"] for x in recovered} == {staged["first"], staged["second"]}, [x["id"] for x in recovered])

        committed = page.evaluate("""async id => {
          const e=await __SENTINEL_TEST__.commitPendingCapture(id,{description:'Recovered field photograph',caption:'Recovered capture'});
          const stored=await __SENTINEL_TEST__.getEvidenceBlob(e.id);
          return {id:e.id,code:e.code,hash:e.hash,storedHash:stored?.sha256,size:stored?.blob?.size,designation:e.designation,verified:e.hashVerified,custody:e.custody.length,verification:e.verificationHistory.length,testIds:e.testIds};
        }""", staged["first"])
        check("recovered-capture-committed-immutably", committed["designation"] == "ORIGINAL" and committed["verified"] is True and committed["hash"] == committed["storedHash"] and committed["size"] > 0, committed)
        check("recovered-capture-provenance-created", committed["custody"] >= 2 and committed["verification"] >= 1 and committed["testIds"] == [seed["testId"]], committed)
        post_commit = page.evaluate("""async id => ({
          pending:(await __SENTINEL_TEST__.getPendingCaptures()).map(x=>x.id),
          plainEvidence:(await __SENTINEL_TEST__.rawIdbAll('evidence')).filter(x=>x.projectId===id).length,
          secureEvidence:(await __SENTINEL_TEST__.rawIdbAll('secureEvidence')).filter(x=>x.projectId===id).length,
          secureQueue:(await __SENTINEL_TEST__.rawIdbAll('secureCaptureQueue')).filter(x=>x.projectId===id).length,
          events:__SENTINEL_TEST__.getData().events.filter(x=>x.type.includes('CAPTURED')).length
        })""", seed["projectId"])
        check("committed-item-removed-only-after-save", post_commit["pending"] == [staged["second"]] and post_commit["secureQueue"] == 1, post_commit)
        check("committed-binary-remains-encrypted-at-rest", post_commit["plainEvidence"] == 0 and post_commit["secureEvidence"] == 1, post_commit)
        check("capture-commit-adds-timeline-event", post_commit["events"] == 1, post_commit)

        await_discard = page.evaluate("""async id => {await __SENTINEL_TEST__.deletePendingCapture(id);return (await __SENTINEL_TEST__.getPendingCaptures()).length}""", staged["second"])
        check("queued-capture-can-be-explicitly-discarded", await_discard == 0, await_discard)
        audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("capture-recovery-project-audit", audit["ok"], audit)
        check("capture-recovery-runtime-clean", not errors, errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_capture_recovery_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
