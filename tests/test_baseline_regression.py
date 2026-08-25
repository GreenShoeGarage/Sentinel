"""Immutable baseline comparison and semantic regression-analysis acceptance checks."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

from common import URL, launch_browser

TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp/sentinel-baseline-regression"))
TMP.mkdir(parents=True, exist_ok=True)
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


SEED_AND_COMPARE = r"""
async () => {
  const api=__SENTINEL_TEST__;
  const p=api.blankProject();
  p.mode='advanced';
  p.settings.currentOperator='Alex Analyst';
  p.project.name='Baseline Regression Acceptance Project';
  p.project.client='Example Client';
  p.project.site='North Campus';
  p.project.purpose='Verify semantic baseline comparison.';
  p.project.scope='Authorized physical security assessment of the North Campus.';
  p.authorization.status='AUTHORIZED';
  p.authorization.reference='AUTH-2026-013';
  p.authorization.authority='Jordan Sponsor';
  p.authorization.authorizedFacilities='North Campus';
  p.authorization.authorizedAreas='Lobby and loading zone';
  p.authorization.authorizedTechniques='Observation and approved access-control testing';
  p.authorization.stopConditions='Stop immediately on safety concern.';
  p.authorization.safetyRestrictions='No destructive testing.';
  p.assurance.coverageObjective='Assess primary exterior and lobby controls.';
  p.assurance.samplingBasis='Risk-based sampling of representative access points.';
  const org=p.sites[0];
  const site={id:'site-1',code:'SITE-01',name:'North Campus',type:'SITE',parentId:org.id,description:''};
  const building={id:'building-1',code:'BLDG-A',name:'Building A',type:'BUILDING',parentId:site.id,description:''};
  const floor={id:'floor-1',code:'F1',name:'Floor 1',type:'FLOOR',parentId:building.id,description:''};
  const zone={id:'zone-1',code:'ZONE-LOBBY',name:'Lobby',type:'ZONE',parentId:floor.id,description:''};
  const asset={id:'asset-1',code:'ASSET-RECEPTION',name:'Reception Desk',type:'ASSET',parentId:zone.id,description:''};
  p.sites.push(site,building,floor,zone,asset);
  p.controls=[
    {id:'ctrl-main',code:'CTRL-001',type:'Badge Reader',category:'ACCESS CONTROL',locationId:zone.id,location:'Lobby',manufacturer:'Example',purpose:'Restrict lobby-to-office access',configuration:'Badge required',condition:'Serviceable',notes:'',evidenceIds:['ev-1']},
    {id:'ctrl-delete',code:'CTRL-DEL',type:'Door Contact',category:'DETECTION',locationId:zone.id,location:'Lobby',manufacturer:'',purpose:'Detect door opening',configuration:'Monitored',condition:'Serviceable',notes:'',evidenceIds:[]},
    {id:'ctrl-absent',code:'CTRL-ABS',type:'Lighting',category:'PERIMETER',locationId:site.id,location:'North Campus',manufacturer:'',purpose:'Support detection',configuration:'Dusk-to-dawn',condition:'Serviceable',notes:'',evidenceIds:[]}
  ];
  p.tests=[{id:'test-1',code:'T-001',title:'Badge-reader challenge',objective:'Verify secure access behavior',controlId:'ctrl-main',locationId:zone.id,location:'Lobby',preconditions:'Authorized assessment window',authorizationRequirement:'AUTH-2026-013',method:'Observe authorized test execution',expected:'Access denied without authorization',successCriteria:'Reader denies access',failureCriteria:'Reader grants access',safety:'Stop on safety concern',personnel:'One tester',equipment:'Authorized badge',scheduled:'2026-08-24T14:00:00.000Z',actualStart:'2026-08-24T14:00:00.000Z',actualEnd:'2026-08-24T14:05:00.000Z',result:'PASSED'}];
  p.evidence=[{id:'ev-1',code:'E-001',filename:'lobby-reader.png',type:'PHOTO',mimeType:'image/png',createdAt:'2026-08-24T14:01:00.000Z',importedAt:'2026-08-24T14:06:00.000Z',collector:'Alex Analyst',currentCustodian:'Alex Analyst',locationId:zone.id,location:'Lobby',description:'Badge reader during authorized test',hash:'a'.repeat(64),blobStored:false,binaryAvailable:false,hashVerified:null,designation:'ORIGINAL',originalEvidenceId:'',parentEvidenceId:'',archived:false,controlId:'ctrl-main',testIds:['test-1'],observationIds:[],findingIds:['finding-1'],positiveObservationIds:[],tags:['access-control'],photoLog:{includeInReport:false,caption:'',direction:'',photographer:'Alex Analyst'}}];
  p.findings=[{id:'finding-1',code:'PHY-2026-001',title:'Reader response requires review',status:'VALIDATED',severity:'LOW',confidence:'MEDIUM',confidenceRationale:'Single authorized test with direct observation.',locationId:zone.id,location:'Lobby',domain:'ACCESS CONTROL',controlId:'ctrl-main',description:'A documented assessment conclusion.',expected:'Unauthorized access should be denied.',observed:'The initial baseline recorded secure behavior.',evidenceIds:['ev-1'],evidenceRationale:'Evidence metadata and test chronology support the conclusion.',observationIds:[],testIds:['test-1'],consequence:'Potential access to office space.',preconditions:'Physical presence at the lobby.',reproducibility:'REPRODUCIBLE',detectionLikelihood:'MEDIUM',recommendation:'Continue monitoring and periodic testing.',compensatingControls:'Reception oversight',owner:'Security Manager',targetDate:'2026-10-01',remediationStatus:'NOT PLANNED',remediationPriority:'PLANNED',riskAcceptanceAuthority:'',riskAcceptanceRationale:'',dimensions:{accessImpact:2,exploitability:2,detection:2,response:2,exposure:2,consequence:2}}];
  p.map.plans=[{id:'plan-1',name:'Floor 1 Plan',locationId:floor.id,fileName:'floor1.png',mimeType:'image/png',assetHash:'b'.repeat(64),assetStored:false,hashVerified:null,markers:[{id:'marker-1',type:'BADGE READER',label:'Lobby Reader',x:40,y:45,locationId:zone.id,recordType:'CONTROL',recordId:'ctrl-main'}],zones:[],paths:[],calibration:null,coverageEnabled:true,zoom:1,panX:0,panY:0}];
  api.setData(p);
  const a=await api.createBaselineRecord('Initial Assessment','Initial authorized assessment state.','Alex Analyst');
  const working=api.getData();
  working.authorization.authorizedAreas='Lobby, loading zone, and reception desk';
  working.tests[0].result='FAILED';
  working.findings[0].severity='HIGH';
  working.findings[0].overrideRationale='Later authorized testing demonstrated greater potential consequence.';
  working.findings[0].remediationStatus='IN PROGRESS';
  working.evidence[0].archived=true;
  working.controls[0].condition='Intermittent';
  working.controls.push({id:'ctrl-added',code:'CTRL-NEW',type:'Guard Patrol',category:'PERSONNEL',locationId:site.id,location:'North Campus',manufacturer:'',purpose:'Provide visible deterrence',configuration:'Hourly patrol',condition:'Active',notes:'Added after initial baseline',evidenceIds:[]});
  const deleted=working.controls.find(x=>x.id==='ctrl-delete');
  api.setData(working);
  api.addRecordTombstone('controls',deleted,'Removed from authorized scope after facility reconfiguration.','SECURITY_CONTROLS');
  const afterDelete=api.getData();
  afterDelete.controls=afterDelete.controls.filter(x=>!['ctrl-delete','ctrl-absent'].includes(x.id));
  afterDelete.map.plans[0].markers[0].x=55;
  api.setData(afterDelete);
  const b=await api.createBaselineRecord('Follow-up Assessment','Follow-up state after changed test results and scope.','Alex Analyst');
  const from=api.baselineEndpoint(a.id),to=api.baselineEndpoint(b.id);
  const raw=api.semanticBaselineDiff(from,to);
  const comparison=api.createBaselineComparisonRecord(a.id,b.id,'Initial to Follow-up','Evaluate regression, improvement, scope movement, and record loss.');
  let diff=api.semanticBaselineDiff(from,to,comparison);
  for(const change of diff.changes){
    if(['REGRESSION','REVIEW'].includes(change.impact)){
      api.updateBaselineChangeReview(comparison,change,{classification:change.impact,status:'REVIEWED',owner:'Alex Analyst',rationale:`Reviewed ${change.categoryLabel}: ${change.autoReason}`});
    }
  }
  await api.finalizeBaselineComparison(comparison,'The follow-up state contains material regressions in test outcome and finding severity, plus reviewed scope and record changes.');
  diff=api.semanticBaselineDiff(from,to,comparison);
  const reviewState=api.baselineComparisonReviewState(comparison);
  const reviewIntegrity=await api.verifyBaselineComparisonReview(comparison);
  const staleClone=JSON.parse(JSON.stringify(comparison));
  staleClone.overallRationale+=' Altered after review.';
  const staleState=api.baselineComparisonReviewState(staleClone);
  const cleanClone=JSON.parse(JSON.stringify(a));
  const cleanIntegrity=await api.verifyBaselineIntegrity(cleanClone,'Validation');
  const tampered=JSON.parse(JSON.stringify(a));
  tampered.snapshot.project.name='Tampered baseline';
  const tamperIntegrity=await api.verifyBaselineIntegrity(tampered,'Validation');
  const exportObj=api.baselineComparisonExportObject(diff,comparison);
  return {
    audit:api.auditProject(api.getData()),
    a,b,raw,diff,comparison,reviewState,reviewIntegrity,staleState,cleanIntegrity,tamperIntegrity,
    csv:api.baselineCsv(diff),html:api.baselineComparisonHtmlDocument(diff,comparison),
    exportObj,report:await api.buildStandaloneReportHtml(),markdown:api.buildMarkdown()
  };
}
"""

with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        page.set_default_timeout(20000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14")
        result = page.evaluate(SEED_AND_COMPARE)

        check("schema14-baseline-project-audits", result["audit"]["ok"], result["audit"])
        check("immutable-baselines-created", result["a"]["snapshotHash"] and result["b"]["snapshotHash"] and result["a"]["snapshotHash"] != result["b"]["snapshotHash"], [result["a"]["snapshotHash"], result["b"]["snapshotHash"]])
        check("snapshot-hashes-are-sha256", len(result["a"]["snapshotHash"]) == 64 and len(result["b"]["snapshotHash"]) == 64)
        check("baseline-integrity-verifies", result["cleanIntegrity"]["state"] == "VERIFIED", result["cleanIntegrity"])
        check("baseline-tampering-detected", result["tamperIntegrity"]["state"] == "MISMATCH", result["tamperIntegrity"])

        changes = result["raw"]["changes"]
        finding_severity = [c for c in changes if c["category"] == "FINDINGS" and c["field"] == "severity"]
        test_result = [c for c in changes if c["category"] == "TEST_CASES" and c["field"] == "result"]
        check("finding-severity-regression-detected", len(finding_severity) == 1 and finding_severity[0]["autoImpact"] == "REGRESSION", finding_severity)
        check("test-result-regression-detected", len(test_result) == 1 and test_result[0]["autoImpact"] == "REGRESSION", test_result)
        check("remediation-progress-improvement-detected", any(c["category"] == "FINDINGS" and c["field"] == "remediationStatus" and c["autoImpact"] == "IMPROVEMENT" for c in changes), changes)
        check("authorization-change-requires-review", any(c["category"] == "AUTHORIZATION_ROE" and c["autoImpact"] == "REVIEW" for c in changes), changes)
        check("map-marker-change-detected", any(c["category"] == "MAP_MARKERS" and c["field"] == "x" for c in changes), changes)
        check("record-addition-detected", any(c["category"] == "SECURITY_CONTROLS" and c["changeType"] == "ADDED" and "CTRL-NEW" in c["entityLabel"] for c in changes), changes)
        check("deliberate-deletion-distinguished", any(c["changeType"] == "DELETED" and c.get("tombstone") and c["tombstone"]["recordCode"] == "CTRL-DEL" for c in changes), changes)
        check("unexplained-absence-distinguished", any(c["changeType"] == "ABSENT_LATER" and "CTRL-ABS" in c["entityLabel"] for c in changes), changes)
        check("coverage-deltas-calculated", "controlCoveragePct" in result["raw"]["coverageBefore"] and result["raw"]["coverageBefore"] != result["raw"]["coverageAfter"], [result["raw"]["coverageBefore"], result["raw"]["coverageAfter"]])

        check("comparison-review-finalized", result["comparison"]["status"] == "REVIEWED" and len(result["comparison"]["reviewSha256"]) == 64, result["comparison"])
        check("comparison-review-current", result["reviewState"]["state"] == "CURRENT", result["reviewState"])
        check("comparison-review-sha256-verifies", result["reviewIntegrity"]["state"] == "VERIFIED", result["reviewIntegrity"])
        check("comparison-review-change-detected", result["staleState"]["state"] == "STALE", result["staleState"])
        unresolved = [c for c in result["diff"]["changes"] if c["impact"] in ("REGRESSION", "REVIEW") and (not c.get("review") or c["review"].get("status") == "OPEN")]
        check("regressions-and-review-items-dispositioned", not unresolved, unresolved)
        check("review-summary-preserved", result["diff"]["summary"]["reviewed"] > 0 and result["diff"]["summary"]["regressions"] >= 2, result["diff"]["summary"])

        check("comparison-json-export-model", result["exportObj"]["comparison"]["code"] == result["comparison"]["code"] and len(result["exportObj"]["changes"]) == result["diff"]["summary"]["total"], result["exportObj"].keys())
        check("comparison-csv-export", "Automatic impact" in result["csv"] and "CTRL-DEL" in result["csv"] and "ABSENT_LATER" in result["csv"])
        check("comparison-html-export", "Baseline Comparison" in result["html"] or result["comparison"]["name"] in result["html"])
        check("standalone-report-includes-reviewed-comparison", "Baseline Comparison and Regression Analysis" in result["report"] and result["comparison"]["code"] in result["report"])
        check("markdown-report-includes-reviewed-comparison", "## Baseline Comparison and Regression Analysis" in result["markdown"] and result["comparison"]["code"] in result["markdown"])

        page.evaluate("__SENTINEL_TEST__.setView('baselines')")
        page.wait_for_selector("#baselineFrom")
        check("baseline-compare-workspace-renders", page.locator("#baselinesView").get_by_text("Change Register", exact=True).count() == 1)
        check("baseline-summary-cards-render", page.locator("#baselinesView .baseline-summary .card").count() >= 4, page.locator("#baselinesView .baseline-summary .card").count())
        check("baseline-filter-controls-render", all(page.locator(selector).count() == 1 for selector in ["#baselineCategory", "#baselineImpact", "#baselineChangeType", "#baselineQuery"]))
        check("baseline-change-register-renders", page.locator("#baselinesView .baseline-change").count() > 0, page.locator("#baselinesView .baseline-change").count())
        page.locator('[data-baseline-tab="REVIEWS"]').click()
        check("comparison-review-log-renders", result["comparison"]["code"] in page.locator("#baselinesView").inner_text())
        page.locator('[data-baseline-tab="SNAPSHOTS"]').click()
        check("immutable-snapshot-register-renders", page.locator('[data-baseline-id]').count() == 2, page.locator('[data-baseline-id]').count())
        page.screenshot(path=str(TMP / "sentinel_baseline_regression.png"), full_page=True)

        # Save/reload through the real-origin IndexedDB path and retain both hashes and review state.
        page.evaluate("__SENTINEL_TEST__.save()")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        persisted = page.evaluate("() => {const p=__SENTINEL_TEST__.getData(),c=p.baselineComparisons[0];return {baselines:p.baselines.map(x=>x.snapshotHash),comparisons:p.baselineComparisons.length,state:__SENTINEL_TEST__.baselineComparisonReviewState(c),audit:__SENTINEL_TEST__.auditProject(p)}}")
        check("baseline-hashes-persist-after-reload", len(persisted["baselines"]) == 2 and all(len(x) == 64 for x in persisted["baselines"]), persisted)
        check("comparison-review-persists-after-reload", persisted["comparisons"] == 1 and persisted["state"]["state"] == "CURRENT", persisted)
        check("reloaded-baseline-project-audits", persisted["audit"]["ok"], persisted["audit"])
        check("no-baseline-page-errors", not errors, errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path=str(TMP / "sentinel_baseline_failure.png"), full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
