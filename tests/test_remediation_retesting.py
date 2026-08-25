"""Remediation submissions, immutable formal retests, independent review, reporting, traceability, and migration checks."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, FIXTURES, launch_browser

TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp"))
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


PROJECT_FACTORY = r"""async () => {
  const p=__SENTINEL_TEST__.blankProject();p.mode='advanced';p.settings.currentOperator='Alex Analyst';
  Object.assign(p.project,{name:'Formal Retest Regression',client:'Example Client',site:'Main Facility',lead:'Alex Analyst',startDate:'2026-08-23',endDate:'2026-08-24',classification:'CONTROLLED',purpose:'Validate remediation and formal retesting.',scope:'Authorized physical security verification.'});
  Object.assign(p.authorization,{status:'ACTIVE',reference:'AUTH-RT-001',sponsor:'Security Director',authority:'Chief Security Officer',team:'Alex Analyst, Morgan Reviewer',emergencyContacts:'Security Operations Center',authorizedFacilities:'Main Facility',authorizedAreas:'Building A',excludedAreas:'None',authorizedTechniques:'Authorized observation and verification',prohibitedTechniques:'No destructive techniques',allowedHours:'0800-1800',restrictedHours:'Outside authorized period',interactionRules:'Follow approved script',photoRestrictions:'Authorized evidence only',recordingRestrictions:'Authorized evidence only',safetyRestrictions:'Stop for unsafe conditions',stopConditions:'Stop on sponsor direction',escalation:'Contact sponsor',lawEnforcement:'Security Operations Center notified',evidenceHandling:'Preserve immutable originals'});
  Object.assign(p.assurance,{samplingBasis:'All records in this fixture are included.',samplingLimitations:'Software regression fixture only.',scopeNotes:'Formal retest workflow fixture.',reviewNotes:'Independent review is modeled.'});
  const org=p.sites[0],site={id:'site-rt',code:'SITE-RT',name:'Main Facility',type:'SITE',parentId:org.id,description:''},asset={id:'asset-rt',code:'ASSET-RT',name:'Restricted Records',type:'ASSET',parentId:site.id,description:''};p.sites=[org,site,asset];
  p.controls=[{id:'control-rt',code:'CTRL-RT',category:'ACCESS CONTROL',type:'Door Control',locationId:asset.id,location:'',manufacturer:'',model:'',purpose:'Protect restricted records.',configuration:'',condition:'REMEDIATED',evidenceIds:['evidence-rem']}];
  p.evidence=[
   {id:'evidence-rem',code:'E-REM-001',filename:'implementation-note.txt',type:'NOTE',designation:'ORIGINAL',createdAt:'2026-08-20T12:00:00Z',importedAt:'2026-08-20T12:01:00Z',collector:'Facility Owner',locationId:asset.id,location:'',description:'Implementation evidence.',controlId:'control-rt',testIds:[],observationIds:[],findingIds:[],positiveObservationIds:[],hash:'',blobStored:false,binaryAvailable:false,hashVerified:null,lastVerifiedAt:'',archived:false,tags:['remediation'],metadataHistory:[],verificationHistory:[],custody:[],transformations:[],acquisition:{acquiredAt:'2026-08-20T12:00:00Z',sourceDevice:'Client submission',sourceDescription:'Remediation documentation',originalFilename:'implementation-note.txt',originalMimeType:'text/plain',originalSize:0},photoLog:{caption:'',direction:'',photographer:'',relatedAssetId:'',includeInReport:false}},
   {id:'evidence-rt',code:'E-RT-001',filename:'retest-note.txt',type:'NOTE',designation:'ORIGINAL',createdAt:'2026-08-23T10:10:00Z',importedAt:'2026-08-23T10:11:00Z',collector:'Alex Analyst',locationId:asset.id,location:'',description:'Retest evidence.',controlId:'control-rt',testIds:[],observationIds:[],findingIds:['finding-rt'],positiveObservationIds:[],hash:'',blobStored:false,binaryAvailable:false,hashVerified:null,lastVerifiedAt:'',archived:false,tags:['retest'],metadataHistory:[],verificationHistory:[],custody:[],transformations:[],acquisition:{acquiredAt:'2026-08-23T10:10:00Z',sourceDevice:'Field notebook',sourceDescription:'Authorized formal retest record',originalFilename:'retest-note.txt',originalMimeType:'text/plain',originalSize:0},photoLog:{caption:'',direction:'',photographer:'',relatedAssetId:'',includeInReport:false}}
  ];
  const finding={id:'finding-rt',code:'PHY-2026-201',title:'Door control did not perform as expected',status:'RETEST REQUIRED',dimensions:{accessImpact:3,exploitability:2,detection:3,response:3,exposure:2,consequence:3},confidence:'HIGH',confidenceRationale:'Observed during authorized testing.',locationId:asset.id,location:'',domain:'ACCESS CONTROL',controlId:'control-rt',description:'The control did not consistently enforce the expected secure state.',expected:'The control consistently prevents unauthorized entry.',observed:'The expected secure state was not consistently observed.',consequence:'Restricted records could be exposed.',preconditions:'Authorized assessment window.',reproducibility:'REPRODUCIBLE',detectionLikelihood:'MEDIUM',recommendation:'Repair the control and verify consistent secure operation.',compensatingControls:'Guard patrols.',owner:'Facility Security',targetDate:'2026-08-22',testIds:[],observationIds:[],evidenceIds:['evidence-rt'],evidenceRationale:'Formal retest evidence is linked.',remediationStatus:'IMPLEMENTED',statusHistory:[],retestHistory:[],createdAt:'2026-08-18T10:00:00Z',updatedAt:'2026-08-23T10:15:00Z'};p.findings=[finding];
  const rem=__SENTINEL_TEST__.normalizeRemediationSubmission({id:'rem-1',code:'REM-001',findingId:finding.id,findingCodeSnapshot:finding.code,findingSnapshot:__SENTINEL_TEST__.findingSnapshotForRetest(finding),status:'ACCEPTED FOR RETEST',submittedBy:'Facility Owner',submittedAt:'2026-08-20T12:00:00Z',owner:'Facility Security',implementationDate:'2026-08-20',requestedRetestDate:'2026-08-23',recommendationSnapshot:finding.recommendation,remediationDescription:'Door control repaired and configured for consistent secure operation.',implementationEvidenceIds:['evidence-rem'],compensatingControlIds:['control-rt'],compensatingControlDescription:'Guard patrols remained active during implementation.',notes:'Implementation evidence reviewed.',acceptedBy:'Morgan Reviewer',acceptedAt:'2026-08-21T12:00:00Z',acceptanceNote:'Submission is sufficiently documented for an authorized formal retest.',statusHistory:[{id:'rh-1',from:'DRAFT',to:'SUBMITTED',at:'2026-08-20T12:00:00Z',by:'Facility Owner',note:'Submitted for review.'},{id:'rh-2',from:'SUBMITTED',to:'ACCEPTED FOR RETEST',at:'2026-08-21T12:00:00Z',by:'Morgan Reviewer',note:'Accepted for formal retest.'}]});p.remediationSubmissions=[rem];
  const rt=__SENTINEL_TEST__.normalizeRetest({id:'rt-1',code:'RT-001',findingId:finding.id,findingCodeSnapshot:finding.code,findingSnapshot:__SENTINEL_TEST__.findingSnapshotForRetest(finding),remediationSubmissionId:rem.id,remediationSnapshot:__SENTINEL_TEST__.remediationSnapshotForRetest(rem),sequence:1,status:'COMPLETED',title:'PHY-2026-201 Formal Retest',objective:'Verify the repaired door control consistently provides the expected secure state.',scope:'Authorized verification of the repaired control at the restricted records area.',plannedDate:'2026-08-23',authorizationReference:'AUTH-RT-001',authorizationAuthority:'Chief Security Officer',authorizedBy:'Alex Analyst',authorizedAt:'2026-08-23T09:30:00Z',authorizationExpires:'2026-08-23T18:00:00Z',restrictions:'No destructive testing.',safety:'Stop for unsafe conditions or sponsor direction.',locationId:asset.id,location:'Restricted Records',method:'Observe and verify the repaired control under authorized test conditions.',expectedSecureBehavior:'The control consistently prevents unauthorized entry.',successCriteria:'All authorized verification attempts observe the expected secure state.',failureCriteria:'Any authorized verification attempt fails to observe the expected secure state.',tester:'Alex Analyst',actualStart:'2026-08-23T10:00:00Z',actualEnd:'2026-08-23T10:10:00Z',completedAt:'2026-08-23T10:10:00Z',completionSha256:'c'.repeat(64),evidenceIds:['evidence-rt'],controlIds:['control-rt'],result:'REMEDIATED',evidenceRationale:'Direct retest evidence is linked.',analystNotes:'The repaired control performed consistently.',compensatingControlResult:'EFFECTIVE',compensatingControlNotes:'Guard patrols remained effective.',reviewDecision:'PENDING',reviewRequired:true,statusHistory:[{id:'rth-1',from:'IN PROGRESS',to:'COMPLETED',at:'2026-08-23T10:10:00Z',by:'Alex Analyst',note:'Execution completed; independent review required.'}],reviewHistory:[]});p.retests=[rt];
  return p;
}"""


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(15000)
        errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14")
        project = page.evaluate(PROJECT_FACTORY)
        audit = page.evaluate("p=>{__SENTINEL_TEST__.setData(p);return __SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())}", project)
        check("schema14-remediation-project-audits", audit["ok"], audit)

        model = page.evaluate("""() => {const p=__SENTINEL_TEST__.getData(),rem=p.remediationSubmissions[0],rt=p.retests[0];return {
          remErrors:__SENTINEL_TEST__.remediationSubmissionWorkflowErrors(rem,rem.status,p),
          rtErrors:__SENTINEL_TEST__.retestWorkflowErrors(rt,rt.status,p),
          remLocked:__SENTINEL_TEST__.remediationSubmissionLocked(rem),
          planLocked:__SENTINEL_TEST__.retestPlanLocked(rt),
          executionLocked:__SENTINEL_TEST__.retestExecutionLocked(rt),
          queue:__SENTINEL_TEST__.retestQueueEntries(p),
          edges:__SENTINEL_TEST__.traceEdgeList(p),
          readiness:__SENTINEL_TEST__.reportReadiness(p),
          snap:[rem.findingSnapshot.code,rt.findingSnapshot.code,rt.remediationSnapshot.code]
        }}""")
        check("accepted-remediation-workflow-complete", model["remErrors"] == [], model["remErrors"])
        check("completed-retest-workflow-complete", model["rtErrors"] == [], model["rtErrors"])
        check("submitted-and-completed-records-immutable", model["remLocked"] and model["planLocked"] and model["executionLocked"], model)
        check("immutable-source-snapshots-present", model["snap"] == ["PHY-2026-201", "PHY-2026-201", "REM-001"], model["snap"])
        check("completed-retest-enters-review-queue", len(model["queue"]) == 1 and model["queue"][0]["state"] == "REVIEW", model["queue"])
        labels = {edge["label"] for edge in model["edges"]}
        check("recommendation-to-retest-traceability", {"recommendation implemented by", "verified by", "retested by", "supports retest"}.issubset(labels), labels)
        check("unreviewed-completed-retest-blocks-report", any("awaiting independent review" in item.lower() for item in model["readiness"]["blocking"]), model["readiness"])

        page.evaluate("__SENTINEL_TEST__.setView('retest')")
        check("retest-workspace-heading", page.locator("#retestView h2").first.inner_text() == "Remediation & Formal Retesting")
        check("four-retest-workspace-tabs", page.locator(".retest-tab").all_inner_texts() == ["Retest Queue", "Remediation Submissions", "Retest Register", "Independent Review"])
        page.locator('[data-retest-tab="SUBMISSIONS"]').click()
        page.locator('tr[data-type="remediation"]').first.click()
        check("accepted-submission-opens-read-only", "IMMUTABLE REMEDIATION SUBMISSION" in page.locator("#modalBody").inner_text())
        check("accepted-submission-has-no-save", not page.locator("#modalSave").is_visible())
        check("accepted-submission-can-plan-retest", page.locator("#planRemediationRetest").count() == 1)
        page.locator("#modalCancel").click()
        page.locator('[data-retest-tab="RETESTS"]').click()
        page.locator('tr[data-type="retest"]').first.click()
        body = page.locator("#modalBody").inner_text()
        check("review-modal-preserves-completed-retest-readonly", "IMMUTABLE COMPLETED RETEST" in body and "COMPLETION FINGERPRINT" in body.upper(), body)
        check("completed-execution-fields-not-editable-in-review", page.locator("#m_rt_title").count() == 0 and page.locator("#m_review_name").count() == 1)
        check("completed-retest-awaits-independent-review", page.locator("#m_review_decision").count() == 1 and page.locator("#modalSave").is_visible())
        page.locator("#modalCancel").click()
        page.evaluate("__SENTINEL_TEST__.openRetest(__SENTINEL_TEST__.getData().retests[0])")
        check("completed-retest-detail-has-no-edit-save", not page.locator("#modalSave").is_visible())
        check("completed-retest-offers-independent-review", page.locator("#reviewRetest").count() == 1)
        check("completed-retest-offers-corrective-followup", page.locator("#followupRetest").count() == 1)
        page.locator("#modalCancel").click()

        reviewed = page.evaluate("""() => {const p=__SENTINEL_TEST__.getData(),r=p.retests[0],f=p.findings[0];r.status='REVIEWED';r.reviewDecision='APPROVED';r.reviewer='Morgan Reviewer';r.reviewerRole='Independent Assessment Reviewer';r.reviewNote='Evidence, authorization, execution, and result are supported.';r.reviewedAt='2026-08-23T11:00:00Z';r.reviewSha256='d'.repeat(64);r.reviewFingerprint=__SENTINEL_TEST__.retestFingerprint(r);r.reviewRequired=false;f.status='CLOSED';f.remediationStatus='VERIFIED';f.retestResult='REMEDIATED';f.lastRetestId=r.id;f.lastRetestedAt=r.reviewedAt;__SENTINEL_TEST__.setData(p);const q=__SENTINEL_TEST__.getData();return {audit:__SENTINEL_TEST__.auditProject(q),errors:__SENTINEL_TEST__.retestWorkflowErrors(q.retests[0],'REVIEWED',q),sign:__SENTINEL_TEST__.retestSignOffState(q.retests[0]),reviewed:__SENTINEL_TEST__.reviewedRetests(q).length,readiness:__SENTINEL_TEST__.reportReadiness(q)}}""")
        check("reviewed-retest-audits", reviewed["audit"]["ok"], reviewed["audit"])
        check("reviewed-retest-workflow-complete", reviewed["errors"] == [], reviewed["errors"])
        check("independent-review-current", reviewed["sign"]["state"] == "CURRENT" and reviewed["reviewed"] == 1, reviewed)
        check("review-removes-awaiting-review-block", not any("awaiting independent review" in item.lower() for item in reviewed["readiness"]["blocking"]), reviewed["readiness"])
        check("verified-closure-supported-by-approved-retest", not any("closed as verified without" in item.lower() for item in reviewed["readiness"]["blocking"]), reviewed["readiness"])

        reports = page.evaluate("""async () => ({html:await __SENTINEL_TEST__.buildStandaloneReportHtml(),md:__SENTINEL_TEST__.buildMarkdown(),section:__SENTINEL_TEST__.retestReportHtml(__SENTINEL_TEST__.getData(),'h2',false),sectionMd:__SENTINEL_TEST__.retestMarkdown(__SENTINEL_TEST__.getData(),false)})""")
        check("html-report-includes-remediation-submission", "Remediation Submissions" in reports["html"] and "REM-001" in reports["html"] and "Acceptance rationale" in reports["html"])
        check("html-report-includes-reviewed-retest", "Formal Retests" in reports["html"] and "RT-001" in reports["html"] and "INDEPENDENTLY REVIEWED" in reports["html"])
        check("markdown-includes-remediation-and-retest", "### Remediation Submissions" in reports["md"] and "### Formal Retests" in reports["md"] and "RT-001" in reports["md"])
        check("dedicated-retest-report-functions", "REM-001" in reports["section"] and "RT-001" in reports["sectionMd"])

        diff = page.evaluate("""() => __SENTINEL_TEST__.baselineDiff({id:'baseline-empty',snapshot:{findings:[],controls:[],tests:[],evidence:[],controlChains:[],remediationSubmissions:[],retests:[]}})""")
        check("baseline-detects-remediation-addition", diff["submissionDelta"] == 1 and diff["submissionsAdded"] == ["REM-001"], diff)
        check("baseline-detects-retest-addition", diff["retestDelta"] == 1 and diff["retestsAdded"] == ["RT-001"], diff)

        stale = page.evaluate("""() => {const p=__SENTINEL_TEST__.getData(),r=p.retests[0];r.analystNotes+=' Material change.';return __SENTINEL_TEST__.retestSignOffState(r)}""")
        check("material-change-makes-review-stale", stale["state"] == "STALE", stale)

        legacy = json.loads((FIXTURES / "schema11_from_v0.11.0.json").read_text(encoding="utf-8"))
        migrated = page.evaluate("""p => {const m=__SENTINEL_TEST__.migrateProject(p);return {schema:m.schemaVersion,app:m.appVersion,submissions:Array.isArray(m.remediationSubmissions),retests:Array.isArray(m.retests),audit:__SENTINEL_TEST__.auditProject(m)}}""", legacy)
        check("schema11-migrates-to-schema14", migrated["schema"] == 14 and migrated["app"] == "0.15.0-rc.2", migrated)
        check("schema11-adds-remediation-and-retest-collections", migrated["submissions"] and migrated["retests"], migrated)
        check("schema11-migration-audits", migrated["audit"]["ok"], migrated["audit"])

        page.evaluate("__SENTINEL_TEST__.setView('retest')")
        page.locator('[data-retest-tab="REVIEW"]').click()
        check("reviewed-record-leaves-review-queue", page.locator('tr[data-type="retest"]').count() == 0, page.locator("#retestView").inner_text())
        check("no-page-errors", not errors, errors)
        check("no-console-errors", not console_errors, console_errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_remediation_retesting_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
