"""Published-schema migration, normalization, type inference, and package-snapshot checks."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, FIXTURES, ROOT, launch_browser

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
        page.set_default_timeout(15000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text and not any(term in msg.text.lower() for term in ["indexeddb","browser storage rejected","securityerror"]) else None)
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=10000)
        except Exception:
            try: page.close()
            except Exception: pass
            page = browser.new_page()
            page.set_default_timeout(15000)
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and not any(term in msg.text.lower() for term in ["indexeddb","browser storage rejected","securityerror"]) else None)
            page.goto("about:blank")
            page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14")

        fixtures = sorted(FIXTURES.glob("schema*.json"))
        check("thirteen-historical-fixtures", len(fixtures) == 13, [path.name for path in fixtures])
        for path in fixtures:
            raw = json.loads(path.read_text(encoding="utf-8"))
            result = page.evaluate("""project => {
              const migrated=__SENTINEL_TEST__.migrateProject(project);
              return {schema:migrated.schemaVersion,app:migrated.appVersion,audit:__SENTINEL_TEST__.auditProject(migrated),evidence:migrated.evidence};
            }""", raw)
            check(f"{path.stem}-migrates-to-schema14", result["schema"] == 14 and result["app"] == "0.15.0-rc.2", result)
            check(f"{path.stem}-audit-clean", result["audit"]["ok"], result["audit"])
            check(
                f"{path.stem}-evidence-provenance-normalized",
                all(
                    isinstance(record.get("verificationHistory"), list)
                    and isinstance(record.get("custody"), list)
                    and isinstance(record.get("transformations"), list)
                    and isinstance(record.get("metadataHistory"), list)
                    and isinstance(record.get("photoLog"), dict)
                    for record in result["evidence"]
                ),
                result["evidence"],
            )

        schema14 = page.evaluate("() => {const p=__SENTINEL_TEST__.blankProject();const m=__SENTINEL_TEST__.migrateProject(p);return {schema:m.schemaVersion,audit:__SENTINEL_TEST__.auditProject(m)}}")
        check("schema14-roundtrip", schema14["schema"] == 14 and schema14["audit"]["ok"], schema14)

        newer = page.evaluate("""() => {try{__SENTINEL_TEST__.migrateProject({schemaVersion:99});return '';}catch(error){return error.message;}}""")
        check("newer-schema-rejected", "newer" in newer.lower(), newer)

        normalized = page.evaluate("""() => __SENTINEL_TEST__.normalizeEvidence({
          id:'legacy',code:'E-1',type:'PHOTO',testId:'t1',observationId:'o1',findingId:'f1',positiveObservationId:'p1',parentEvidenceId:'source',caption:'Legacy caption',direction:'North',photographer:'Legacy Analyst',tags:'one, two'
        })""")
        check("legacy-single-relations-normalized", normalized["testIds"] == ["t1"] and normalized["observationIds"] == ["o1"] and normalized["findingIds"] == ["f1"] and normalized["positiveObservationIds"] == ["p1"], normalized)
        check("legacy-lineage-normalized", normalized["designation"] == "DERIVED" and normalized["originalEvidenceId"] == "source" and normalized["parentEvidenceId"] == "source", normalized)
        check("legacy-photo-log-normalized", normalized["photoLog"]["caption"] == "Legacy caption" and normalized["photoLog"]["direction"] == "North" and normalized["photoLog"]["photographer"] == "Legacy Analyst", normalized["photoLog"])
        check("legacy-tags-normalized", normalized["tags"] == ["one", "two"], normalized["tags"])

        inferred = page.evaluate("""() => {
          const file=(name,type)=>new File([new Uint8Array([1,2,3])],name,{type});
          return [
            __SENTINEL_TEST__.fileTypeFromUpload(file('photo.png','image/png')),
            __SENTINEL_TEST__.fileTypeFromUpload(file('clip.webm','video/webm')),
            __SENTINEL_TEST__.fileTypeFromUpload(file('note.wav','audio/wav')),
            __SENTINEL_TEST__.fileTypeFromUpload(file('note.txt','text/plain')),
            __SENTINEL_TEST__.fileTypeFromUpload(file('report.pdf','application/pdf')),
            __SENTINEL_TEST__.fileTypeFromUpload(file('screen.png','image/png'),'SCREENSHOT')
          ];
        }""")
        check("evidence-type-inference", inferred == ["PHOTO", "VIDEO", "AUDIO", "NOTE", "DOCUMENT", "SCREENSHOT"], inferred)

        cycle = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          p.evidence=[{id:'o',code:'E-1',designation:'ORIGINAL'},{id:'d',code:'E-2',designation:'DERIVED',originalEvidenceId:'o',parentEvidenceId:'o',derivationNote:'test'}];
          __SENTINEL_TEST__.setData(p);
          return {forward:__SENTINEL_TEST__.evidenceWouldCycle('d','o'),reverse:__SENTINEL_TEST__.evidenceWouldCycle('o','d'),self:__SENTINEL_TEST__.evidenceWouldCycle('o','o')};
        }""")
        check("lineage-cycle-detection", cycle == {"forward": False, "reverse": True, "self": True}, cycle)

        snapshot = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.blankProject();
          p.map.plans=[{id:'plan',name:'Plan',dataUrl:'data:image/png;base64,AAAA',markers:[],zones:[],paths:[]}];
          const s=__SENTINEL_TEST__.packageProjectSnapshot(p);
          return {source:p.map.plans[0].dataUrl,snapshot:s.map.plans[0].dataUrl};
        }""")
        check("package-snapshot-omits-inline-plan-binary", snapshot["source"].startswith("data:") and snapshot["snapshot"] == "", snapshot)
        check("migration-runtime-clean", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_migrations_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
