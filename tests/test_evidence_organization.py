"""Evidence Vault search, filters, grouping, layout, bulk update, and history checks."""
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
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.set_default_timeout(12000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject(),org=crypto.randomUUID(),site=crypto.randomUUID(),test=crypto.randomUUID();
          p.project.name='Evidence Organization Test';
          p.sites=[{id:org,code:'ORG-1',name:'Org',type:'ORGANIZATION',parentId:null},{id:site,code:'SITE-1',name:'North Site',type:'SITE',parentId:org}];
          p.tests=[{id:test,code:'T-001',title:'Door test',result:'NOT STARTED',locationId:site,controlId:'',evidenceIds:[]}];
          p.evidence=[
            {id:crypto.randomUUID(),code:'E-0001',type:'PHOTO',filename:'north-door.png',designation:'ORIGINAL',collector:'Alice',locationId:site,tags:['door'],testIds:[test],description:'North door photograph',photoLog:{caption:'North door',includeInReport:true}},
            {id:crypto.randomUUID(),code:'E-0002',type:'DOCUMENT',filename:'guard-log.pdf',designation:'ORIGINAL',collector:'Bob',tags:['log'],description:'Guard log document',photoLog:{includeInReport:false}},
            {id:crypto.randomUUID(),code:'E-0003',type:'PHOTO',filename:'lobby.png',designation:'ORIGINAL',collector:'Alice',tags:['lobby'],description:'Lobby photograph',photoLog:{caption:'Lobby',includeInReport:true}}
          ];
          __SENTINEL_TEST__.setData(p); __SENTINEL_TEST__.setView('evidence');
        }""")

        check("initial-three-records", page.locator(".evidence-card").count() == 3)
        page.fill("#ev_query", "door")
        page.wait_for_timeout(500)
        check("search-filter", page.locator(".evidence-card").count() == 1)
        page.fill("#ev_query", "")
        page.wait_for_timeout(500)
        page.select_option("#ev_type", "PHOTO")
        page.wait_for_timeout(150)
        check("type-filter", page.locator(".evidence-card").count() == 2)
        page.select_option("#ev_group", "LOCATION")
        page.wait_for_timeout(150)
        groups = page.locator(".evidence-group-title").all_inner_texts()
        check("location-grouping", any("NORTH SITE" in group.upper() for group in groups), groups)

        page.click("#toggleEvidenceLayout")
        check("list-layout", page.locator(".tablewrap").count() >= 1)
        page.click("#toggleEvidenceLayout")
        check("grid-layout", page.locator(".evidence-grid").count() >= 1)

        page.click("#selectVisibleEvidence")
        check("bulk-button-enabled", page.locator("#bulkEvidence").is_enabled())
        page.click("#bulkEvidence")
        page.fill("#m_tags", "reviewed, field")
        page.select_option("#m_include", "EXCLUDE")
        page.select_option("#m_archive", "ARCHIVE")
        page.fill("#m_note", "Bulk organization test.")
        page.click("#modalSave")
        page.wait_for_timeout(300)
        data = page.evaluate("__SENTINEL_TEST__.getData()")
        photos = [item for item in data["evidence"] if item["type"] == "PHOTO"]
        document = next(item for item in data["evidence"] if item["type"] == "DOCUMENT")
        check("bulk-tags-applied", all("reviewed" in item["tags"] and "field" in item["tags"] for item in photos), photos)
        check("bulk-photo-log-exclusion", all(not item["photoLog"]["includeInReport"] for item in photos), photos)
        check("bulk-archive-applied", all(item["archived"] for item in photos), photos)
        check("bulk-history-preserved", all(len(item["metadataHistory"]) == 1 and item["metadataHistory"][0]["note"] == "Bulk organization test." for item in photos), photos)
        check("nonselected-record-unchanged", not document["archived"] and "reviewed" not in document["tags"], document)

        page.select_option("#ev_type", "ALL")
        page.select_option("#ev_integrity", "METADATA")
        page.wait_for_timeout(150)
        check("metadata-only-integrity-filter", page.locator(".evidence-card").count() == 3)
        page.click('[data-evidence-tab="PHOTOLOG"]')
        check("archived-photos-hidden-from-photo-log", page.locator(".photo-log-card").count() == 0)
        check("organization-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_evidence_organization_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
