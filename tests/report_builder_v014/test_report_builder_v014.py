#!/usr/bin/env python3
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
import sys
import traceback
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "test-results"
OUT.mkdir(exist_ok=True)
RESULT = {
    "suite": "Professional Report Builder 2.0 browser acceptance",
    "started": dt.datetime.now(dt.timezone.utc).isoformat(),
    "assertions": [],
    "downloads": [],
}


def record(name: str, passed: bool, detail="", *, advisory: bool = False) -> None:
    RESULT["assertions"].append(
        {
            "name": name,
            "passed": bool(passed),
            "advisory": advisory,
            "detail": str(detail)[:3000],
        }
    )
    if not passed and not advisory:
        raise AssertionError(f"{name}: {detail}")


def wait_status(page, status: str, timeout: int = 10000) -> None:
    page.wait_for_function(
        "expected => window.__SENTINEL_TEST__.activeReportRevision().status === expected",
        arg=status,
        timeout=timeout,
    )


def save_modal(page) -> None:
    page.locator("#modalSave").click()
    page.wait_for_timeout(120)


def download_button(page, selector: str, label: str) -> Path:
    with page.expect_download(timeout=12000) as info:
        page.locator(selector).click()
    dl = info.value
    dest = OUT / dl.suggested_filename
    dl.save_as(dest)
    record(label, dest.exists() and dest.stat().st_size > 0, {"file": dest.name, "bytes": dest.stat().st_size})
    RESULT["downloads"].append({"type": label, "file": dest.name, "bytes": dest.stat().st_size})
    return dest


def run() -> None:
    from playwright.sync_api import sync_playwright

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    evidence_bytes = (ROOT / "tests" / "assets" / "sample_evidence.png").read_bytes()
    unrelated_evidence_bytes = (ROOT / "tests" / "assets" / "sample_unrelated.png").read_bytes()
    evidence_payload = {
        "selected": {
            "b64": base64.b64encode(evidence_bytes).decode("ascii"),
            "sha256": hashlib.sha256(evidence_bytes).hexdigest(),
            "size": len(evidence_bytes),
        },
        "unrelated": {
            "b64": base64.b64encode(unrelated_evidence_bytes).decode("ascii"),
            "sha256": hashlib.sha256(unrelated_evidence_bytes).hexdigest(),
            "size": len(unrelated_evidence_bytes),
        },
    }
    browser_errors: list[str] = []
    console_errors: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("pageerror", lambda e: browser_errors.append(str(e)))
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        # This environment blocks navigation to ordinary and local origins. Install a test-only
        # SHA-256 bridge before loading the app into about:blank so Final Issue hashing can still
        # be exercised. Production code continues to call the native Web Crypto API.
        page.expose_function(
            "__sentinelTestSha256",
            lambda values: list(hashlib.sha256(bytes(values)).digest()),
        )
        page.goto("about:blank", wait_until="domcontentloaded")
        page.evaluate(
            """()=>{
              Object.defineProperty(window.crypto,'subtle',{
                configurable:true,
                value:{digest:async(_algorithm,data)=>{
                  const bytes=Array.from(new Uint8Array(data));
                  const out=await window.__sentinelTestSha256(bytes);
                  return Uint8Array.from(out).buffer;
                }}
              });
            }"""
        )
        page.set_content(html, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(500)
        record(
            "Browser host uses documented SHA-256 bridge",
            True,
            "Navigation is administratively blocked in this environment; report lifecycle logic ran with a test-only digest bridge on about:blank.",
            advisory=True,
        )
        record("Application loads", "SENTINEL" in page.locator("body").inner_text().upper())
        identity = page.evaluate(
            "()=>({version:window.__SENTINEL_TEST__.appVersion,schema:window.__SENTINEL_TEST__.schemaVersion})"
        )
        record("Release identity is reconciled", identity == {"version": "0.15.0-rc.1", "schema": 14}, identity)

        page.evaluate(
            """payload=>{
              window.__SENTINEL_TEST__.seedReportDemoProject();
              const project=window.__SENTINEL_TEST__.getData();
              const createdAt=new Date().toISOString();
              const evidenceBase={
                type:'PHOTO',mimeType:'image/png',
                blobStored:true,binaryAvailable:true,hashVerified:true,designation:'ORIGINAL',
                collector:'Validation Analyst',location:'Validation Site',createdAt,importedAt:createdAt,
                verificationHistory:[],custody:[],transformations:[],metadataHistory:[],tags:['report-validation'],
                acquisition:{acquiredAt:createdAt,sourceDevice:'Validation fixture',sourceDescription:'Report-package boundary test',originalMimeType:'image/png',originalSize:payload.size,originalLastModified:createdAt},
                archived:false
              };
              project.evidence.push({
                ...evidenceBase,id:'report-evidence-selected',code:'EV-SEL-001',filename:'selected-report-evidence.png',
                size:payload.selected.size,hash:payload.selected.sha256,
                description:'Selected evidence for the governed report.',
                photoLog:{caption:'Selected report photograph',direction:'North',photographer:'Validation Analyst',relatedAssetId:'',includeInReport:true,reportOrder:1},
                acquisition:{...evidenceBase.acquisition,originalFilename:'selected-report-evidence.png',originalSize:payload.selected.size}
              });
              project.evidence.push({
                ...evidenceBase,id:'report-evidence-unrelated',code:'EV-UNRELATED-002',filename:'unrelated-project-evidence.png',
                size:payload.unrelated.size,hash:payload.unrelated.sha256,
                description:'Unrelated project evidence that must not enter the controlled report package.',
                photoLog:{caption:'Unrelated project photograph',direction:'South',photographer:'Validation Analyst',relatedAssetId:'',includeInReport:false,reportOrder:2},
                acquisition:{...evidenceBase.acquisition,originalFilename:'unrelated-project-evidence.png',originalSize:payload.unrelated.size}
              });
              window.__SENTINEL_TEST__.setData(project);
              const normalized=window.__SENTINEL_TEST__.getData();
              normalized.assurance.signOff.fingerprint=window.__SENTINEL_TEST__.assuranceFingerprint(normalized);
              window.__SENTINEL_TEST__.setData(normalized);
              const selectedBytes=Uint8Array.from(atob(payload.selected.b64),c=>c.charCodeAt(0));
              const unrelatedBytes=Uint8Array.from(atob(payload.unrelated.b64),c=>c.charCodeAt(0));
              window.__SENTINEL_TEST__.setTestEvidenceBlob('report-evidence-selected',new Blob([selectedBytes],{type:'image/png'}),{filename:'selected-report-evidence.png',mimeType:'image/png',sha256:payload.selected.sha256});
              window.__SENTINEL_TEST__.setTestEvidenceBlob('report-evidence-unrelated',new Blob([unrelatedBytes],{type:'image/png'}),{filename:'unrelated-project-evidence.png',mimeType:'image/png',sha256:payload.unrelated.sha256});
              window.__SENTINEL_TEST__.setView('report');
            }""",
            evidence_payload,
        )
        page.wait_for_timeout(250)
        record("Report navigation destination exists", page.locator('[data-view="report"]').count() == 1)
        record("Report Builder workspace renders", "PROFESSIONAL REPORT BUILDER 2.0" in page.locator("#mainContent").inner_text().upper())
        record("Five report workspaces render", page.locator("[data-report-tab]").count() == 5)

        # Composition, persistence, custom sections, and appendix selection.
        page.locator('[data-report-field="handlingInstructions"]').fill(
            "Distribute only to the client sponsor and named physical-security officials."
        )
        page.locator("#addCustomReportSection").click()
        page.locator("#m_report_custom_title").fill("Management Response")
        page.locator("#m_report_custom_body").fill(
            "Management responses may be recorded here without modifying the validated finding record."
        )
        save_modal(page)
        page.wait_for_timeout(160)
        composition = page.evaluate(
            """()=>{const r=window.__SENTINEL_TEST__.activeReportRevision();return {
              handling:r.handlingInstructions,
              custom:r.customSections.map(x=>({title:x.title,body:x.body})),
              order:r.sectionOrder
            }}"""
        )
        record("Composition fields persist", composition["handling"].startswith("Distribute only"), composition)
        record("Custom report section persists", composition["custom"] == [{
            "title": "Management Response",
            "body": "Management responses may be recorded here without modifying the validated finding record.",
        }], composition)
        record("Custom section is ordered before appendices", composition["order"].index(next(x for x in composition["order"] if x.startswith("custom:"))) < composition["order"].index("appendices"), composition["order"])

        page.locator('[data-report-tab="APPENDICES"]').click()
        daily = page.locator('[data-report-appendix="dailyLogs"]')
        if not daily.is_checked():
            daily.check()
        record(
            "Appendix selection persists",
            page.evaluate("()=>window.__SENTINEL_TEST__.activeReportRevision().appendixSelections.dailyLogs") is True,
        )

        # Explicit evidence placement and selected-evidence distribution boundary.
        page.locator('[data-report-tab="EVIDENCE"]').click()
        record("Evidence selector lists project evidence", page.locator('[data-report-evidence-toggle]').count() == 2)
        page.locator('[data-report-evidence-toggle="report-evidence-selected"]').check()
        page.locator('[data-report-evidence-caption="report-evidence-selected"]').fill("Selected report photograph — authorized lobby control point.")
        page.locator('[data-report-evidence-section="report-evidence-selected"]').select_option("executiveSummary")
        page.wait_for_timeout(120)
        evidence_selection = page.evaluate(
            """()=>window.__SENTINEL_TEST__.activeReportRevision().evidenceSelection.map(x=>({evidenceId:x.evidenceId,caption:x.caption,sectionKey:x.sectionKey,include:x.include}))"""
        )
        record(
            "Only explicitly selected evidence enters the report artifact",
            len(evidence_selection) == 1 and evidence_selection[0]["evidenceId"] == "report-evidence-selected",
            evidence_selection,
        )
        record(
            "Evidence caption and section placement persist",
            evidence_selection[0]["caption"].startswith("Selected report photograph") and evidence_selection[0]["sectionKey"] == "executiveSummary",
            evidence_selection[0],
        )

        page.locator('[data-report-tab="PREVIEW"]').click()
        preview_text = page.locator("#reportPrintSurface").inner_text()
        record("Preview renders substantial content", len(preview_text) > 1200, len(preview_text))
        record("Custom section appears in preview", "Management Response" in preview_text)
        record("Selected evidence caption appears in preview", "Selected report photograph — authorized lobby control point." in preview_text)
        record("Sensitivity marking appears in preview", "CONTROLLED" in preview_text.upper())
        page.screenshot(path=str(OUT / "report_builder_composition.png"), full_page=True)

        # Governed lifecycle through the actual user interface.
        page.locator('[data-report-tab="GOVERNANCE"]').click()
        page.locator("#submitReportReview").click()
        page.locator("#m_report_reviewer").fill("Independent Reviewer")
        page.locator("#m_report_reviewer_role").fill("Security Reviewer")
        page.locator("#m_report_review_note").fill("Composition and distribution boundaries are ready for independent review.")
        save_modal(page)
        wait_status(page, "IN_REVIEW")
        review = page.evaluate("()=>window.__SENTINEL_TEST__.activeReportRevision()")
        record("Draft submits for independent review", bool(review["reviewFingerprint"]), review["review"])

        page.locator("#approveReport").click()
        page.locator("#m_report_reviewer").fill("Independent Reviewer")
        page.locator("#m_report_reviewer_role").fill("Security Reviewer")
        page.locator("#m_report_review_rationale").fill("Narrative, appendices, output controls, and evidence boundaries were reviewed.")
        page.locator("#m_report_approver").fill("Approval Authority")
        page.locator("#m_report_approver_role").fill("Director of Security")
        page.locator("#m_report_approval_rationale").fill("Approved for controlled Final Issue after independent review.")
        save_modal(page)
        wait_status(page, "APPROVED")
        approved = page.evaluate("()=>window.__SENTINEL_TEST__.activeReportRevision()")
        record("Independent review and approval persist", bool(approved["approvalFingerprint"]), approved["approval"])

        # Prove that a hashing failure cannot partially mutate an approved record.
        atomic = page.evaluate(
            """async()=>{
              const original=crypto.subtle;
              delete crypto.subtle;
              let error='';
              try{await window.__SENTINEL_TEST__.finalizeReportIssue(null,null,'Issuing Authority','Atomicity test',{issueNumber:'FAIL-001'});}catch(e){error=e.message;}
              Object.defineProperty(crypto,'subtle',{configurable:true,value:original});
              const r=window.__SENTINEL_TEST__.activeReportRevision();
              return {error,status:r.status,hash:r.issueFingerprint,issuedAt:r.issue.issuedAt};
            }"""
        )
        record("Failed issue hashing is transactionally atomic", bool(atomic["error"]) and atomic["status"] == "APPROVED" and not atomic["hash"] and not atomic["issuedAt"], atomic)

        page.locator("#finalIssueReport").click()
        page.locator("#m_report_issuer").fill("Issuing Authority")
        page.locator("#m_report_issue_number").fill("VAL-ISSUE-001")
        page.locator("#m_report_distribution").fill("Controlled distribution to the client sponsor and named security officials.")
        page.locator("#m_report_issue_note").fill("Final Issue created after independent review and output verification.")
        save_modal(page)
        wait_status(page, "FINAL_ISSUE", 15000)
        page.wait_for_function(
            "()=>/^[a-f0-9]{64}$/i.test(window.__SENTINEL_TEST__.activeReportRevision().issueFingerprint)",
            timeout=15000,
        )
        if page.locator('#modalBack.open').count():
            page.locator('#modalCancel').click()
            page.wait_for_timeout(80)
        issued = page.evaluate(
            """()=>{const r=window.__SENTINEL_TEST__.activeReportRevision();return {
              status:r.status,locked:r.locked,hash:r.issueFingerprint,
              issue:r.issue,snapshot:!!r.issuedSnapshot?.assessment,
              state:window.__SENTINEL_TEST__.reportRevisionState()
            }}"""
        )
        record("Final Issue is sealed with SHA-256", issued["status"] == "FINAL_ISSUE" and issued["locked"] and re.fullmatch(r"[a-f0-9]{64}", issued["hash"], re.I) is not None, issued)
        record("Final Issue preserves issuer metadata", issued["issue"]["issueNumber"] == "VAL-ISSUE-001" and issued["issue"]["distribution"].startswith("Controlled distribution"), issued["issue"])
        record("Final Issue contains a sealed assessment snapshot", issued["snapshot"] is True)

        page.locator('[data-report-tab="COMPOSITION"]').click()
        disabled = page.locator("[data-report-field]").count() and all(
            page.locator("[data-report-field]").nth(i).is_disabled()
            for i in range(page.locator("[data-report-field]").count())
        )
        record("Final Issue composition is read-only", disabled)
        issued_body = page.evaluate("()=>window.__SENTINEL_TEST__.reportBodyHtml()")

        # Final output formats.
        html_path = download_button(page, "#htmlReport", "Standalone HTML export")
        md_path = download_button(page, "#mdReport", "Markdown export")
        json_path = download_button(page, "#jsonReport", "Structured JSON export")
        html_text = html_path.read_text(encoding="utf-8", errors="ignore")
        md_text = md_path.read_text(encoding="utf-8", errors="ignore")
        report_json = json.loads(json_path.read_text(encoding="utf-8"))
        record("HTML export contains governed content", "Management Response" in html_text and "VAL-ISSUE-001" in html_text)
        record("HTML export embeds explicitly selected image evidence", "data:image/png;base64," in html_text and "Selected report photograph — authorized lobby control point." in html_text)
        unrelated_data_url = "data:image/png;base64," + evidence_payload["unrelated"]["b64"]
        record("HTML export embeds no unrelated evidence figure", unrelated_data_url not in html_text and "Unrelated project photograph" not in html_text, {"embeddedImages": html_text.count("data:image/png;base64,")})
        record("Markdown export contains full appendices", "Appendix — Test Log" in md_text and "Appendix — Daily Field Logs" in md_text)
        record("JSON export preserves issue fingerprint", report_json["revision"]["issueFingerprint"] == issued["hash"], report_json["revision"].get("issueFingerprint"))
        record("JSON export preserves one explicit evidence selection", len(report_json["selectedEvidence"]) == 1 and report_json["selectedEvidence"][0]["metadata"]["id"] == "report-evidence-selected", report_json["selectedEvidence"])

        # Render the actual standalone deliverable, including print-media rules.
        output_page = context.new_page()
        output_page.set_viewport_size({"width": 1280, "height": 900})
        output_page.set_content(html_text, wait_until="load")
        output_page.wait_for_timeout(120)
        record("Standalone report document title is governed", "Revision A" in output_page.title(), output_page.title())
        rendered_images = output_page.locator(".report-figure img")
        image_state = [rendered_images.nth(i).evaluate("img=>({complete:img.complete,width:img.naturalWidth,height:img.naturalHeight})") for i in range(rendered_images.count())]
        record("Standalone selected-evidence figures decode", bool(image_state) and all(x["complete"] and x["width"] > 0 for x in image_state), image_state)
        output_dims = output_page.evaluate("()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,sections:document.querySelectorAll('.report-section').length})")
        record("Standalone report avoids desktop horizontal overflow", output_dims["scroll"] <= output_dims["client"] + 4 and output_dims["sections"] >= 8, output_dims)
        output_page.emulate_media(media="print")
        print_state = output_page.evaluate("""()=>({
          header:getComputedStyle(document.querySelector('.report-running-header')).display,
          footer:getComputedStyle(document.querySelector('.report-running-footer')).display,
          pageBreaks:document.querySelectorAll('.report-page-break').length,
          coverMinHeight:getComputedStyle(document.querySelector('.report-cover')).minHeight
        })""")
        record("Print-media controls activate", print_state["header"] != "none" and print_state["footer"] != "none" and print_state["pageBreaks"] >= 1, print_state)
        output_page.screenshot(path=str(OUT / "report_output_print_media.png"), full_page=True)
        output_page.close()

        # Controlled report package with explicit acknowledgement.
        page.locator("#reportPackage").click()
        page.locator("#export_ack").check()
        with page.expect_download(timeout=15000) as package_info:
            page.locator(".secret-prompt button.primary").click()
        package_download = package_info.value
        package_path = OUT / package_download.suggested_filename
        package_download.save_as(package_path)
        RESULT["downloads"].append({"type": "Controlled report package", "file": package_path.name, "bytes": package_path.stat().st_size})
        record("Controlled report package downloads", package_path.stat().st_size > 0, package_path.name)
        with zipfile.ZipFile(package_path) as zf:
            names = set(zf.namelist())
            manifest = json.loads(zf.read("manifest.json"))
            record("Report package contains governed outputs", {"manifest.json", "report/report.html", "report/report.md", "report/report.json"}.issubset(names), sorted(names))
            record("Report package excludes complete project database", not any("project" in n.lower() and n.lower().endswith((".sentinel", ".json")) for n in names if n != "report/report.json"), sorted(names))
            record("Report package manifest identifies Final Issue", manifest["report"]["status"] == "FINAL_ISSUE" and manifest["report"]["issueFingerprint"] == issued["hash"], manifest["report"])
            evidence_files = [n for n in names if n.startswith("evidence/")]
            record("Report package contains exactly the explicitly selected evidence binary", len(evidence_files) == 1 and "EV-SEL-001".lower() in evidence_files[0].lower(), evidence_files)
            record("Report package excludes unrelated project evidence", not any("UNRELATED" in n.upper() for n in names), sorted(names))
            record("Report package manifest contains one selected evidence record", len(manifest["selectedEvidence"]) == 1 and manifest["selectedEvidence"][0]["evidenceId"] == "report-evidence-selected", manifest["selectedEvidence"])
            selected_payload = zf.read(manifest["selectedEvidence"][0]["path"])
            record("Selected evidence package binary matches the source fixture", hashlib.sha256(selected_payload).hexdigest() == evidence_payload["selected"]["sha256"] and len(selected_payload) == evidence_payload["selected"]["size"])
            for item in manifest["files"]:
                payload = zf.read(item["path"])
                record(f"Package hash verifies: {item['path']}", hashlib.sha256(payload).hexdigest() == item["sha256"])

        # The issued artifact must remain sealed when the live project changes.
        changed = page.evaluate(
            """()=>{
              const p=window.__SENTINEL_TEST__.getData();
              p.project.purpose='Live project purpose changed after issue.';
              p.project.scope+=' Additional post-issue scope note.';
              window.__SENTINEL_TEST__.setData(p);
              window.__SENTINEL_TEST__.setView('report');
              return window.__SENTINEL_TEST__.reportRevisionState();
            }"""
        )
        page.wait_for_timeout(150)
        changed_body = page.evaluate("()=>window.__SENTINEL_TEST__.reportBodyHtml()")
        record("Live project divergence is detected", changed["stale"] is True, changed)
        strip_divergence=lambda text: re.sub(r'<div class="report-divergence">[\s\S]*?</div>', '', text, count=1)
        record("Issued report rendering remains sealed after divergence", strip_divergence(changed_body) == strip_divergence(issued_body))
        record("Divergence warning appears in the interface", "LIVE PROJECT DIVERGED" in page.locator("#mainContent").inner_text().upper())

        page.locator('[data-report-tab="GOVERNANCE"]').click()
        page.locator("#newReportRevision").click()
        page.wait_for_timeout(120)
        new_revision = page.evaluate("()=>window.__SENTINEL_TEST__.activeReportRevision()")
        record("New revision opens as editable Draft", new_revision["status"] == "DRAFT" and new_revision["revision"] == "B" and bool(new_revision["sourceRevisionId"]), {k: new_revision[k] for k in ["status", "revision", "sourceRevisionId"]})
        record("New revision inherits sealed custom sections", new_revision["customSections"][0]["title"] == "Management Response", new_revision["customSections"])
        page.locator('[data-report-tab="COMPOSITION"]').click()
        record("New revision composition is editable", page.locator('[data-report-field="executiveSummary"]').is_enabled())

        # Responsive smoke check.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(180)
        dims = page.evaluate("()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})")
        record("Mobile Report Builder avoids major horizontal overflow", dims["scroll"] <= dims["client"] + 16, dims)
        page.screenshot(path=str(OUT / "report_builder_mobile.png"), full_page=True)

        record("No uncaught browser exceptions", not browser_errors, browser_errors)
        # Opaque-origin storage warnings are expected in this administratively restricted host,
        # but application/runtime errors are not.
        material_console = [x for x in console_errors if not re.search(r"indexeddb|localstorage|securityerror|storage", x, re.I)]
        record("No material console errors", not material_console, material_console)
        if console_errors:
            record("Environment storage console notes", True, console_errors, advisory=True)

        browser.close()


try:
    run()
except Exception as exc:
    RESULT["fatal"] = str(exc)
    RESULT["traceback"] = traceback.format_exc()
finally:
    RESULT["completed"] = dt.datetime.now(dt.timezone.utc).isoformat()
    required = [a for a in RESULT["assertions"] if not a.get("advisory")]
    RESULT["passed"] = bool(required) and all(a.get("passed") for a in required) and "fatal" not in RESULT
    (OUT / "report_builder_results.json").write_text(json.dumps(RESULT, indent=2), encoding="utf-8")
    passed = sum(1 for a in RESULT["assertions"] if a.get("passed"))
    total = len(RESULT["assertions"])
    lines = [f"{'PASS' if RESULT['passed'] else 'FAIL'} {passed}/{total}"]
    lines += [f"{'PASS' if a.get('passed') else 'FAIL'}{' (advisory)' if a.get('advisory') else ''} {a['name']}: {a.get('detail','')}" for a in RESULT["assertions"]]
    if "fatal" in RESULT:
        lines.append("FATAL " + RESULT["fatal"])
    (OUT / "report_builder_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.exit(0 if RESULT["passed"] else 1)
