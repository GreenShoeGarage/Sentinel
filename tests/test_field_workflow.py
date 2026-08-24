"""Authorized Field Mode completion and abort workflow regression tests."""
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
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(15000)
        errors: list[str] = []
        dialogs: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        audit = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          const ids={org:crypto.randomUUID(),site:crypto.randomUUID(),zone:crypto.randomUUID(),ctrl:crypto.randomUUID(),t1:crypto.randomUUID(),t2:crypto.randomUUID()};
          Object.assign(p.project,{name:'Field Workflow Test',client:'Test Client',lead:'Analyst One',site:'Test Site',startDate:'2026-08-23',endDate:'2026-08-24',purpose:'Authorized workflow test',scope:'Controlled test scope'});
          Object.assign(p.authorization,{status:'AUTHORIZED',reference:'AUTH-001',sponsor:'Sponsor',authority:'Authorizer',emergencyContacts:'555-0100',authorizedFacilities:'Test Site',authorizedAreas:'Zone A',excludedAreas:'None',authorizedTechniques:'Documented test actions',prohibitedTechniques:'None',allowedHours:'All test hours',stopConditions:'Stop on request',escalation:'Call sponsor',evidenceHandling:'Local controlled device'});
          p.sites=[{id:ids.org,code:'ORG-001',name:'Test Org',type:'ORGANIZATION',parentId:null},{id:ids.site,code:'SITE-001',name:'Test Site',type:'SITE',parentId:ids.org},{id:ids.zone,code:'ZONE-001',name:'Zone A',type:'ZONE',parentId:ids.site}];
          p.controls=[{id:ids.ctrl,code:'CTRL-001',type:'ACCESS CONTROL',locationId:ids.zone,location:'Zone A',evidenceIds:[]}];
          const base={objective:'Verify expected secure behavior',controlId:ids.ctrl,locationId:ids.zone,location:'Zone A',authorizationRequirement:'AUTH-001',plannedMethod:'Observe authorized control response',expected:'Access remains controlled',successCriteria:'Control behaves as expected',failureCriteria:'Control does not behave as expected',safety:'Stop on request',personnel:'Analyst',equipment:'None',scheduled:'2026-08-23T18:00',actualStart:'',actualEnd:'',result:'NOT STARTED'};
          p.tests=[{...base,id:ids.t1,code:'T-001',title:'End workflow test'},{...base,id:ids.t2,code:'T-002',title:'Abort workflow test'}];
          p.settings.currentOperator='Analyst One';
          return __SENTINEL_TEST__.setData(p);
        }""")
        check("authorized-fixture-audit", audit["ok"], audit)

        page.locator('[data-view="field"]').click()
        page.locator("#startTest").click()
        page.locator("#m_ack").check()
        page.locator("#m_actor").fill("Analyst One")
        page.locator("#modalSave").click()
        page.wait_for_selector("#endTest")
        active = page.evaluate("__SENTINEL_TEST__.getData()")
        check("first-test-started", active["tests"][0]["result"] == "IN PROGRESS" and bool(active["tests"][0]["actualStart"]), active["tests"][0])
        check("engagement-becomes-active", active["authorization"]["status"] == "ACTIVE", active["authorization"]["status"])
        check("only-one-test-in-progress", sum(1 for test in active["tests"] if test["result"] == "IN PROGRESS") == 1)

        page.locator('[data-event="APPROACH"]').click()
        page.locator("#endTest").click()
        page.locator("#m_result").select_option("PASSED")
        page.locator("#m_note").fill("Control behaved as expected.")
        page.locator("#modalSave").click()
        page.wait_for_selector("#startTest")
        state1 = page.evaluate("__SENTINEL_TEST__.getData()")
        check("normal-end-result", state1["tests"][0]["result"] == "PASSED", state1["tests"][0])
        check("normal-end-timestamp", bool(state1["tests"][0]["actualEnd"]), state1["tests"][0])
        check("normal-end-event", any(event["type"] == "TEST ENDED" and event["testId"] == state1["tests"][0]["id"] for event in state1["events"]))
        check("status-returns-authorized", state1["authorization"]["status"] == "AUTHORIZED", state1["authorization"]["status"])

        page.locator("#startTest").click()
        page.locator("#m_test").select_option(state1["tests"][1]["id"])
        page.locator("#m_ack").check()
        page.locator("#modalSave").click()
        page.wait_for_selector("#abortTest")
        page.locator("#abortTest").click()
        page.locator("#m_note").fill("Safety stop condition exercised.")
        page.locator("#modalSave").click()
        page.wait_for_selector("#startTest")
        state2 = page.evaluate("__SENTINEL_TEST__.getData()")
        check("abort-result", state2["tests"][1]["result"] == "ABORTED", state2["tests"][1])
        check("abort-timestamp", bool(state2["tests"][1]["actualEnd"]), state2["tests"][1])
        check("abort-event", any(event["type"] == "TEST ABORTED" and event["testId"] == state2["tests"][1]["id"] for event in state2["events"]))
        check("no-active-tests-after-close", not any(test["result"] == "IN PROGRESS" for test in state2["tests"]))
        check("authorization-history-recorded", len(state2["authorization"]["statusHistory"]) >= 4, state2["authorization"]["statusHistory"])
        final_audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("final-project-audit", final_audit["ok"], final_audit)
        check("field-workflow-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_field_workflow_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
