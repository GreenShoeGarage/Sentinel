"""Assessment Assurance, multidimensional coverage, gap review, sign-off, and visual traceability checks."""
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


PROJECT_FACTORY = r"""() => {
  const p=__SENTINEL_TEST__.blankProject(); p.mode='advanced';
  const org=p.sites[0];
  Object.assign(p.project,{name:'Assurance Regression Project',client:'Example Client',site:'Main Campus',lead:'Alex Analyst',startDate:'2026-08-20',endDate:'2026-08-22',classification:'CONTROLLED',purpose:'Evaluate physical security controls.',scope:'Authorized assessment of the main campus.'});
  Object.assign(p.authorization,{status:'COMPLETE',reference:'AUTH-2026-001',sponsor:'Security Director',authority:'Chief Security Officer',team:'Alex Analyst',emergencyContacts:'Security Operations Center',authorizedFacilities:'Main Campus',authorizedAreas:'Buildings A and B',excludedAreas:'Data center interior',authorizedTechniques:'Observation and authorized access-control testing',prohibitedTechniques:'No destructive entry',allowedHours:'0800-1800',stopConditions:'Stop on safety concern or sponsor direction',escalation:'Contact assessment sponsor',evidenceHandling:'Store locally and preserve originals'});
  Object.assign(p.assurance,{coverageObjective:'RISK-BASED SAMPLE',samplingBasis:'Controls were selected by asset criticality, public exposure, and prior incident history.',samplingLimitations:'The sample does not represent overnight staffing or severe-weather operations.',scopeNotes:'Coverage is measured against the authorized facilities and controls.',reviewNotes:'Unresolved gaps require disposition before final issue.'});
  const site={id:'site-main',code:'SITE-01',name:'Main Campus',type:'SITE',parentId:org.id,description:''};
  const bldg={id:'bldg-a',code:'BLDG-A',name:'Building A',type:'BUILDING',parentId:site.id,description:''};
  const floor={id:'floor-1',code:'F1',name:'Floor 1',type:'FLOOR',parentId:bldg.id,description:''};
  const z1={id:'zone-lobby',code:'ZONE-LOBBY',name:'Lobby',type:'ZONE',parentId:floor.id,description:''};
  const z2={id:'zone-service',code:'ZONE-SVC',name:'Service Corridor',type:'ZONE',parentId:floor.id,description:''};
  const z3={id:'zone-office',code:'ZONE-OFFICE',name:'Administrative Office',type:'ZONE',parentId:floor.id,description:''};
  const z4={id:'zone-empty',code:'ZONE-EMPTY',name:'Unassessed Storage',type:'ZONE',parentId:floor.id,description:''};
  const asset={id:'asset-records',code:'ASSET-REC',name:'Records Cabinet',type:'ASSET',parentId:z3.id,description:''};
  p.sites=[org,site,bldg,floor,z1,z2,z3,z4,asset];
  const control=(id,code,category,type,locationId)=>({id,code,category,type,locationId,location:'',manufacturer:'',model:'',purpose:'',configuration:'',condition:'',evidenceIds:[]});
  p.controls=[
    control('c-pass','CTRL-PASS','ACCESS CONTROL','Badge Reader',z1.id),
    control('c-fail','CTRL-FAIL','PERIMETER','Exterior Door',z1.id),
    control('c-partial','CTRL-PART','SURVEILLANCE','Camera',z2.id),
    control('c-noev','CTRL-NOEV','DOORS','Electronic Lock',z2.id),
    control('c-notest','CTRL-NOTEST','VISITOR MANAGEMENT','Reception Procedure',z3.id),
    control('c-na','CTRL-NA','ADMINISTRATIVE','Key Policy',asset.id),
    control('c-noloc','CTRL-NOLOC','DETECTION','Alarm Sensor','')
  ];
  const test=(id,code,controlId,locationId,result,day='2026-08-21')=>({id,code,title:`Test ${code}`,objective:'Evaluate the linked control.',controlId,locationId,location:'',preconditions:'Authorization confirmed.',authorizationRequirement:'AUTH-2026-001',method:'Authorized observation and validation.',expected:'The control behaves as designed.',successCriteria:'Secure behavior is observed.',failureCriteria:'The expected secure behavior is not observed.',safety:'Stop on any unsafe condition.',personnel:'Alex Analyst',equipment:'Field notebook',scheduled:day?`${day}T09:00:00Z`:'',actualStart:['NOT STARTED','NOT APPLICABLE'].includes(result)?'':`${day}T09:00:00Z`,actualEnd:['NOT STARTED','NOT APPLICABLE'].includes(result)?'':`${day}T09:05:00Z`,result,closingNote:result==='NOT STARTED'?'':'Assessment result recorded.'});
  p.tests=[
    test('t-pass','T-PASS','c-pass',z1.id,'PASSED'),
    test('t-fail','T-FAIL','c-fail',z1.id,'FAILED'),
    test('t-partial','T-PART','c-partial',z2.id,'PARTIAL','2026-08-22'),
    test('t-noev','T-NOEV','c-noev',z2.id,'PASSED','2026-08-22'),
    test('t-na','T-NA','c-na',asset.id,'NOT APPLICABLE','2026-08-22'),
    test('t-unlinked','T-UNLINKED','',z1.id,'NOT STARTED','')
  ];
  const evidence=(id,code,testId,controlId,hashChar,verified=true)=>({id,code,filename:`${code}.jpg`,type:'PHOTO',designation:'ORIGINAL',createdAt:'2026-08-21T09:01:00Z',importedAt:'2026-08-21T09:02:00Z',collector:'Alex Analyst',locationId:z1.id,location:'',description:`Evidence for ${code}`,controlId,testIds:testId?[testId]:[],observationIds:[],findingIds:[],positiveObservationIds:[],hash:hashChar.repeat(64),blobStored:true,binaryAvailable:true,hashVerified:verified,lastVerifiedAt:verified?'2026-08-21T09:03:00Z':'',archived:false,tags:[],metadataHistory:[],verificationHistory:[],custody:[{id:`custody-${id}`,at:'2026-08-21T09:02:00Z',action:'COLLECTED',by:'Alex Analyst',from:'Field collection',to:'Local evidence vault',note:'Original collected.'}],transformations:[],acquisition:{acquiredAt:'2026-08-21T09:01:00Z',sourceDevice:'Test camera',sourceDescription:'Authorized field capture',originalFilename:`${code}.jpg`,originalMimeType:'image/jpeg',originalSize:1200},photoLog:{caption:'',direction:'',photographer:'Alex Analyst',relatedAssetId:'',includeInReport:false}});
  const ePass=evidence('e-pass','E-PASS','t-pass','c-pass','a',true);
  const eFail=evidence('e-fail','E-FAIL','t-fail','c-fail','b',true);
  const ePart=evidence('e-part','E-PART','t-partial','c-partial','c',true); ePart.locationId=z2.id;
  const eIntegrity=evidence('e-integrity','E-INTEGRITY','','','d',false); eIntegrity.locationId='';
  p.evidence=[ePass,eFail,ePart,eIntegrity];
  p.observations=[{id:'o-pass',code:'OBS-001',timestamp:'2026-08-21T09:02:00Z',observer:'Alex Analyst',site:'Main Campus',locationId:z1.id,location:'',category:'ACCESS CONTROL',description:'The badge reader rejected an unauthorized credential.',controlId:'c-pass',testId:'t-pass',evidenceIds:['e-pass'],significance:'Positive control behavior',followUp:false,createdAt:'2026-08-21T09:02:00Z',updatedAt:'2026-08-21T09:02:00Z'}];
  ePass.observationIds=['o-pass'];
  p.events=[{id:'event-pass',timestamp:'2026-08-21T09:01:30Z',type:'ACCESS DENIED',note:'Unauthorized credential denied.',actor:'Alex Analyst',locationId:z1.id,location:'',testId:'t-pass',findingId:'',evidenceIds:['e-pass']}];
  p.findings=[
    {id:'f-fail',code:'PHY-2026-001',title:'Exterior door control failure',status:'DRAFT',severity:'HIGH',dimensions:{accessImpact:4,exploitability:4,detection:4,response:4,exposure:4,consequence:4},confidence:'HIGH',confidenceRationale:'Observed and evidenced during an authorized test.',locationId:z1.id,location:'',domain:'PERIMETER',controlId:'c-fail',description:'The expected door control did not behave as designed.',expected:'Door remains secured.',observed:'Control failed during the test.',consequence:'Unauthorized access could occur.',preconditions:'Authorized assessment window.',reproducibility:'REPRODUCIBLE',detectionLikelihood:'LOW',recommendation:'Repair and retest the control.',compensatingControls:'Guard patrols.',owner:'Facilities',targetDate:'2026-09-30',testIds:['t-fail'],observationIds:[],evidenceIds:['e-fail'],evidenceRationale:'Direct photographic evidence is linked.'},
    {id:'f-unsupported',code:'PHY-2026-002',title:'Unsupported draft conclusion',status:'DRAFT',severity:'MEDIUM',dimensions:{accessImpact:3,exploitability:3,detection:3,response:3,exposure:3,consequence:3},confidence:'LOW',confidenceRationale:'Requires additional evidence.',locationId:z3.id,location:'',domain:'VISITOR MANAGEMENT',controlId:'c-notest',description:'Draft conclusion pending support.',expected:'Visitor procedures are consistently applied.',observed:'Not yet established.',consequence:'Unknown.',preconditions:'',reproducibility:'NOT TESTED',detectionLikelihood:'UNKNOWN',recommendation:'Complete assessment.',compensatingControls:'',owner:'',targetDate:'',testIds:[],observationIds:[],evidenceIds:[],evidenceRationale:''}
  ];
  eFail.findingIds=['f-fail'];
  p.positiveObservations=[{id:'p-pass',code:'POS-001',title:'Badge reader rejected unauthorized credential',status:'DRAFT',locationId:z1.id,location:'',controlId:'c-pass',description:'The access-control reader operated as expected.',demonstratedBehavior:'Unauthorized credential was denied.',operationalValue:'Prevented unauthorized entry.',testIds:['t-pass'],evidenceIds:['e-pass'],evidenceRationale:'Linked field evidence.'}];
  ePass.positiveObservationIds=['p-pass'];
  return p;
}"""

CLEAN_PROJECT_FACTORY = r"""() => {
  const p=__SENTINEL_TEST__.blankProject(); p.mode='advanced'; const org=p.sites[0];
  Object.assign(p.project,{name:'Clean Assurance Project',client:'Example Client',site:'Site A',lead:'Alex Analyst',startDate:'2026-08-20',endDate:'2026-08-21',classification:'CONTROLLED',purpose:'Validate a security control.',scope:'One authorized control and test.'});
  Object.assign(p.authorization,{status:'AUTHORIZED',reference:'AUTH-CLEAN',sponsor:'Security Director',authority:'Chief Security Officer',team:'Alex Analyst',emergencyContacts:'Security Operations Center',authorizedFacilities:'Site A',authorizedAreas:'Lobby',excludedAreas:'None',authorizedTechniques:'Observation',prohibitedTechniques:'No intrusive techniques',allowedHours:'0800-1800',stopConditions:'Stop on safety concern',escalation:'Contact sponsor',evidenceHandling:'Preserve originals locally'});
  Object.assign(p.assurance,{coverageObjective:'ALL IN-SCOPE CONTROLS',samplingBasis:'The sole in-scope control was selected for complete assessment.',samplingLimitations:'Results apply only to the authorized daytime operating condition.',scopeNotes:'One-control assurance scope.',reviewNotes:'All records reviewed.'});
  const site={id:'clean-site',code:'SITE-CLEAN',name:'Site A',type:'SITE',parentId:org.id,description:''};
  const bldg={id:'clean-bldg',code:'BLDG-CLEAN',name:'Building A',type:'BUILDING',parentId:site.id,description:''};
  const floor={id:'clean-floor',code:'FLOOR-CLEAN',name:'Floor 1',type:'FLOOR',parentId:bldg.id,description:''};
  const zone={id:'clean-zone',code:'ZONE-CLEAN',name:'Lobby',type:'ZONE',parentId:floor.id,description:''};
  p.sites=[org,site,bldg,floor,zone];
  p.controls=[{id:'clean-control',code:'CTRL-CLEAN',category:'ACCESS CONTROL',type:'Badge Reader',locationId:zone.id,location:'',manufacturer:'',model:'',purpose:'',configuration:'',condition:'',evidenceIds:['clean-evidence']}];
  p.tests=[{id:'clean-test',code:'T-CLEAN',title:'Credential rejection test',objective:'Verify unauthorized credentials are rejected.',controlId:'clean-control',locationId:zone.id,location:'',preconditions:'Authorization confirmed.',authorizationRequirement:'AUTH-CLEAN',method:'Present authorized test credential.',expected:'Unauthorized credential is rejected.',successCriteria:'Access remains denied.',failureCriteria:'Access is granted.',safety:'Stop on safety concern.',personnel:'Alex Analyst',equipment:'Test credential',scheduled:'2026-08-20T09:00:00Z',actualStart:'2026-08-20T09:00:00Z',actualEnd:'2026-08-20T09:05:00Z',result:'PASSED',closingNote:'Control behaved as expected.'}];
  p.evidence=[{id:'clean-evidence',code:'E-CLEAN',filename:'clean.jpg',type:'PHOTO',designation:'ORIGINAL',createdAt:'2026-08-20T09:01:00Z',importedAt:'2026-08-20T09:02:00Z',collector:'Alex Analyst',locationId:zone.id,location:'',description:'Verified evidence of credential rejection.',controlId:'clean-control',testIds:['clean-test'],observationIds:[],findingIds:[],positiveObservationIds:[],hash:'e'.repeat(64),blobStored:true,binaryAvailable:true,hashVerified:true,lastVerifiedAt:'2026-08-20T09:03:00Z',archived:false,tags:[],metadataHistory:[],verificationHistory:[],custody:[{id:'clean-custody',at:'2026-08-20T09:02:00Z',action:'COLLECTED',by:'Alex Analyst',from:'Field collection',to:'Local evidence vault',note:'Original collected.'}],transformations:[],acquisition:{acquiredAt:'2026-08-20T09:01:00Z',sourceDevice:'Test camera',sourceDescription:'Authorized field capture',originalFilename:'clean.jpg',originalMimeType:'image/jpeg',originalSize:1200},photoLog:{caption:'',direction:'',photographer:'Alex Analyst',relatedAssetId:'',includeInReport:false}}];
  return p;
}"""


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
        page.set_default_timeout(20000)
        errors: list[str] = []
        console_errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14 && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        page.evaluate(f"window.__makeAssuranceProject={PROJECT_FACTORY}; window.__makeCleanAssuranceProject={CLEAN_PROJECT_FACTORY};")

        model = page.evaluate("""() => {
          const project=window.__makeAssuranceProject();
          const audit=__SENTINEL_TEST__.setData(project);
          const dims=['CONTROL','TEST','LOCATION','SECURITY DOMAIN','CONTROL TYPE','ASSESSMENT DAY'];
          const rows=Object.fromEntries(dims.map(d=>[d,__SENTINEL_TEST__.coverageRecordsForDimension(d)]));
          const controlOutcomes=[...new Set(rows.CONTROL.map(r=>r.outcome))];
          const gaps=__SENTINEL_TEST__.assuranceGapQueue();
          const completeness=__SENTINEL_TEST__.assuranceCompleteness();
          const edges=__SENTINEL_TEST__.traceEdgeList();
          const root={type:'control',id:'c-pass',record:__SENTINEL_TEST__.getData().controls.find(c=>c.id==='c-pass')};
          const graph=__SENTINEL_TEST__.buildTraceGraph(root,{direction:'ALL',depth:4,maxNodes:100});
          const down1=__SENTINEL_TEST__.buildTraceGraph(root,{direction:'DOWNSTREAM',depth:1,maxNodes:100});
          const up2=__SENTINEL_TEST__.buildTraceGraph(root,{direction:'UPSTREAM',depth:2,maxNodes:100});
          return {audit,rows,controlOutcomes,summary:__SENTINEL_TEST__.assuranceSummary(),gaps,completeness,edges,graph,down1,up2,report:__SENTINEL_TEST__.reportReadiness()};
        }""")

        check("schema14-assurance-project-audits", model["audit"]["ok"], model["audit"])
        expected_outcomes = {"NOT TESTED", "TESTED — NO EVIDENCE", "INCONCLUSIVE", "CONTROL PASSED", "CONTROL FAILED", "NOT APPLICABLE"}
        check("six-distinct-coverage-outcomes", expected_outcomes.issubset(set(model["controlOutcomes"])), model["controlOutcomes"])
        check("control-dimension-populated", len(model["rows"]["CONTROL"]) == 7, len(model["rows"]["CONTROL"]))
        check("test-dimension-populated", len(model["rows"]["TEST"]) == 6, len(model["rows"]["TEST"]))
        check("location-dimension-includes-hierarchy", len(model["rows"]["LOCATION"]) == 9, len(model["rows"]["LOCATION"]))
        check("security-domain-dimension-populated", len(model["rows"]["SECURITY DOMAIN"]) >= 6, len(model["rows"]["SECURITY DOMAIN"]))
        check("control-type-dimension-populated", len(model["rows"]["CONTROL TYPE"]) >= 6, len(model["rows"]["CONTROL TYPE"]))
        check("assessment-day-dimension-populated", len(model["rows"]["ASSESSMENT DAY"]) >= 3, [r["label"] for r in model["rows"]["ASSESSMENT DAY"]])
        lobby = next(row for row in model["rows"]["LOCATION"] if row["id"] == "zone-lobby")
        check("location-rollup-includes-descendant-records", len(lobby["tests"]) >= 2 and len(lobby["evidence"]) >= 2, lobby)
        summary = model["summary"]
        check("planned-attempted-completed-summary", summary["plannedTests"] == 6 and summary["attemptedTests"] == 4 and summary["completedTests"] == 4, summary)
        check("evidence-coverage-summary", summary["evidencedTests"] == 3 and summary["testEvidencePct"] == 75, summary)
        gap_types = {gap["type"] for gap in model["gaps"]}
        for gap_type in ["CONTROL_NO_TEST", "CONTROL_NO_LOCATION", "TEST_NO_CONTROL", "TEST_NO_EVIDENCE", "FINDING_NO_SUPPORT", "EVIDENCE_UNRELATED", "EVIDENCE_INTEGRITY", "LOCATION_NO_ASSESSMENT"]:
            check(f"gap-detected-{gap_type.lower()}", gap_type in gap_types, gap_types)
        acceptability = page.evaluate("""() => {
          const gaps=__SENTINEL_TEST__.assuranceGapQueue();
          return {
            control:__SENTINEL_TEST__.gapCanBeAccepted(gaps.find(g=>g.type==='CONTROL_NO_TEST')),
            unsupported:__SENTINEL_TEST__.gapCanBeAccepted(gaps.find(g=>g.type==='FINDING_NO_SUPPORT')),
            integrity:__SENTINEL_TEST__.gapCanBeAccepted(gaps.find(g=>g.type==='EVIDENCE_INTEGRITY'))
          };
        }""")
        check("nonblocking-gap-can-be-accepted", acceptability["control"] is True, acceptability)
        check("unsupported-conclusion-cannot-be-accepted", acceptability["unsupported"] is False, acceptability)
        check("integrity-failure-cannot-be-accepted", acceptability["integrity"] is False, acceptability)
        completeness_states = {item["state"] for item in model["completeness"]}
        check("completeness-exposes-pass-review-block", completeness_states == {"PASS", "REVIEW", "BLOCK"}, model["completeness"])
        check("report-readiness-blocks-assurance-gaps", not model["report"]["ready"] and any("assurance" in item.lower() for item in model["report"]["blocking"]), model["report"])

        edge_pairs = {(e["fromType"], e["toType"]) for e in model["edges"]}
        for pair in [("site", "control"), ("control", "test"), ("test", "event"), ("test", "observation"), ("test", "evidence"), ("evidence", "finding"), ("evidence", "positive")]:
            check(f"trace-edge-{pair[0]}-to-{pair[1]}", pair in edge_pairs, edge_pairs)
        check("trace-graph-multihop", len(model["graph"]["nodes"]) >= 7 and len(model["graph"]["edges"]) >= 7, {"nodes": len(model["graph"]["nodes"]), "edges": len(model["graph"]["edges"])})
        check("trace-direction-and-depth-honored", len(model["down1"]["nodes"]) < len(model["graph"]["nodes"]) and all(node["level"] >= 0 for node in model["down1"]["nodes"]), model["down1"])
        check("trace-upstream-finds-location", any(node["type"] == "site" for node in model["up2"]["nodes"]), model["up2"])

        page.evaluate("__SENTINEL_TEST__.setView('coverage')")
        check("assurance-ui-tabs", page.locator(".assurance-tab").count() == 3, page.locator("#coverageView").inner_text())
        check("coverage-dimension-selector", page.locator("#cf_dimension option").count() == 6, page.locator("#cf_dimension").inner_text())
        check("coverage-ui-renders-outcome-badges", page.locator(".coverage-outcome").count() >= 7, page.locator("#coverageView").inner_text())
        page.locator('[data-assurance-panel="GAPS"]').click()
        check("relationship-gap-queue-renders", page.locator("[data-gap-review]").count() >= 6, page.locator("#assurancePanel").inner_text())
        page.locator('[data-assurance-panel="COMPLETENESS"]').click()
        check("completeness-ui-renders", page.locator(".completeness-item").count() == 11, page.locator("#assurancePanel").inner_text())
        page.locator('[data-assurance-panel="MATRIX"]').click()

        with page.expect_download() as download_info:
            page.locator("#coverageJson").click()
        check("coverage-json-export", download_info.value.suggested_filename.endswith("assessment-assurance.json"), download_info.value.suggested_filename)
        with page.expect_download() as download_info:
            page.locator("#coverageCsv").click()
        check("coverage-csv-export", download_info.value.suggested_filename.endswith("coverage-control.csv"), download_info.value.suggested_filename)

        page.evaluate("__SENTINEL_TEST__.setView('trace')")
        page.locator("#traceRoot").select_option("control|c-pass")
        page.locator("#traceDepth").select_option("4")
        page.locator("#traceDirection").select_option("ALL")
        check("visual-trace-graph-renders", page.locator("#traceGraphSvg").count() == 1 and page.locator(".trace-node").count() >= 7 and page.locator(".trace-edge").count() >= 7, page.locator("#traceView").inner_text())
        with page.expect_download() as download_info:
            page.locator("#traceJson").click()
        check("trace-json-export", download_info.value.suggested_filename.endswith(".json"), download_info.value.suggested_filename)
        with page.expect_download() as download_info:
            page.locator("#traceCsv").click()
        check("trace-csv-export", download_info.value.suggested_filename.endswith("traceability.csv"), download_info.value.suggested_filename)
        with page.expect_download() as download_info:
            page.locator("#traceSvg").click()
        check("trace-svg-export", download_info.value.suggested_filename.endswith("traceability.svg"), download_info.value.suggested_filename)

        reports = page.evaluate("""async () => ({html:await __SENTINEL_TEST__.buildStandaloneReportHtml(),md:__SENTINEL_TEST__.buildMarkdown()})""")
        check("html-report-includes-assurance", "Assessment Coverage" in reports["html"] and "Sampling basis" in reports["html"] and "Analyst sign-off" in reports["html"], reports["html"][:500])
        check("markdown-report-includes-assurance", "Assessment Coverage" in reports["md"] and "Sampling basis" in reports["md"] and "Open blocking assurance gaps" in reports["md"], reports["md"][:600])

        accepted = page.evaluate("""async () => {
          const p=__SENTINEL_TEST__.getData();
          p.assurance.gapReviews.push({id:'gap-review-accepted',key:'TEST_NO_EVIDENCE:t-noev',status:'ACCEPTED',owner:'Assessment Lead',rationale:'Direct media could not be collected in the authorized area; the contemporaneous field record is retained as an explicit sampling limitation.',createdAt:'2026-08-23T12:00:00Z',updatedAt:'2026-08-23T12:00:00Z'});
          __SENTINEL_TEST__.setData(p);
          return {disclosures:__SENTINEL_TEST__.assuranceGapDisclosures(),html:await __SENTINEL_TEST__.buildStandaloneReportHtml(),md:__SENTINEL_TEST__.buildMarkdown()};
        }""")
        limitation_text = "Direct media could not be collected in the authorized area"
        check("accepted-limitation-disclosure-model", any(item["type"] == "TEST_NO_EVIDENCE" and item["owner"] == "Assessment Lead" for item in accepted["disclosures"]["accepted"]), accepted["disclosures"])
        check("html-report-discloses-accepted-limitation", limitation_text in accepted["html"] and "Accepted assessment limitations" in accepted["html"], accepted["html"][:900])
        check("markdown-report-discloses-accepted-limitation", limitation_text in accepted["md"] and "Accepted assessment limitations" in accepted["md"], accepted["md"][:900])

        malformed_acceptance = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.getData();
          const r=p.assurance.gapReviews.find(x=>x.key==='TEST_NO_EVIDENCE:t-noev');
          r.owner='';
          __SENTINEL_TEST__.setData(p);
          return {disclosures:__SENTINEL_TEST__.assuranceGapDisclosures(),readiness:__SENTINEL_TEST__.reportReadiness(),audit:__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())};
        }""")
        check("accepted-limitation-requires-accountable-owner", not any(item["type"] == "TEST_NO_EVIDENCE" for item in malformed_acceptance["disclosures"]["accepted"]) and any("accountable owner" in item.lower() for item in malformed_acceptance["audit"]["warnings"]), malformed_acceptance)

        # Clean project: exercise actual user-interface sign-off and staleness controls.
        page.evaluate("__SENTINEL_TEST__.setData(window.__makeCleanAssuranceProject()); __SENTINEL_TEST__.setView('coverage')")
        clean = page.evaluate("({audit:__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData()),checks:__SENTINEL_TEST__.assuranceCompleteness(),gaps:__SENTINEL_TEST__.assuranceGapQueue(),state:__SENTINEL_TEST__.assuranceSignOffState()})")
        check("clean-assurance-project-audits", clean["audit"]["ok"], clean["audit"])
        check("clean-project-has-no-blocking-completeness", not any(item["state"] == "BLOCK" for item in clean["checks"]), clean["checks"])
        check("clean-project-has-no-blocking-gaps", not any(gap["severity"] == "BLOCKING" for gap in clean["gaps"]), clean["gaps"])
        check("unsigned-assurance-state", clean["state"]["state"] == "NONE", clean["state"])
        page.locator('[data-assurance-panel="COMPLETENESS"]').click()
        page.locator("#openSignoff").click()
        page.locator("#m_signer").fill("Alex Analyst")
        page.locator("#m_sign_role").fill("Assessment Lead")
        page.locator("#m_sign_note").fill("All assurance checks reviewed.")
        page.locator("#m_attest").check()
        page.locator("#modalSave").click()
        page.wait_for_function("__SENTINEL_TEST__.assuranceSignOffState().state==='CURRENT'")
        signed = page.evaluate("({state:__SENTINEL_TEST__.assuranceSignOffState(),readiness:__SENTINEL_TEST__.reportReadiness()})")
        check("ui-assurance-signoff-current", signed["state"]["state"] == "CURRENT" and signed["state"]["sign"]["signedBy"] == "Alex Analyst", signed)
        check("signed-clean-project-report-ready", signed["readiness"]["ready"], signed["readiness"])
        page.evaluate("__SENTINEL_TEST__.setView('trace')")
        check("navigation-does-not-stale-signoff", page.evaluate("__SENTINEL_TEST__.assuranceSignOffState().state") == "CURRENT")

        page.click("#advancedBtn")
        page.evaluate("__SENTINEL_TEST__.setView('baselines')")
        page.locator("#createBaseline").click()
        page.locator("#m_name").fill("Signed Assurance Baseline")
        page.locator("#m_note").fill("Preserves the current assurance state.")
        page.locator("#modalSave").click()
        baseline = page.evaluate("__SENTINEL_TEST__.getData().baselines.at(-1)")
        check("baseline-preserves-assurance-record", bool(baseline and baseline.get("snapshot", {}).get("assurance", {}).get("signOff")), baseline)
        check("baseline-preserves-daily-and-retest-collections", "dailyLogs" in baseline["snapshot"] and "questions" in baseline["snapshot"] and "retests" in baseline["snapshot"], baseline["snapshot"].keys())

        page.evaluate("""() => {const p=__SENTINEL_TEST__.getData();p.controls[0].type='Changed Badge Reader';__SENTINEL_TEST__.setData(p);}""")
        stale = page.evaluate("({state:__SENTINEL_TEST__.assuranceSignOffState(),readiness:__SENTINEL_TEST__.reportReadiness()})")
        check("material-change-stales-signoff", stale["state"]["state"] == "STALE", stale)
        check("stale-signoff-blocks-report", not stale["readiness"]["ready"] and any("stale" in item.lower() for item in stale["readiness"]["blocking"]), stale["readiness"])

        check("no-assurance-page-errors", not errors, errors)
        check("no-assurance-console-errors", not console_errors, console_errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_assurance_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
