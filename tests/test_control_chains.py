"""Expected-versus-observed control chains, defense layers, reports, mapping, traceability, and lifecycle checks."""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp"))
checks: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    checks.append(name)
    print("PASS", name, flush=True)


PROJECT_FACTORY = r"""() => {
  const p=__SENTINEL_TEST__.blankProject(); p.mode='advanced'; p.settings.currentOperator='Alex Analyst';
  const org=p.sites[0];
  Object.assign(p.project,{name:'Control Chain Regression Project',client:'Example Client',site:'Main Campus',lead:'Alex Analyst',startDate:'2026-08-23',endDate:'2026-08-24',classification:'CONTROLLED',purpose:'Evaluate defense-in-depth relationships.',scope:'Authorized physical security control validation.'});
  Object.assign(p.authorization,{status:'COMPLETE',reference:'AUTH-CHAIN-001',sponsor:'Security Director',authority:'Chief Security Officer',team:'Alex Analyst',emergencyContacts:'Security Operations Center',authorizedFacilities:'Main Campus',authorizedAreas:'Building A',excludedAreas:'None',authorizedTechniques:'Observation and authorized access-control validation',prohibitedTechniques:'No destructive or coercive techniques',allowedHours:'0800-1800',restrictedHours:'Outside authorized window',interactionRules:'Follow approved script',photoRestrictions:'Authorized assessment evidence only',recordingRestrictions:'Authorized assessment evidence only',safetyRestrictions:'Stop for unsafe conditions',stopConditions:'Stop on sponsor direction',escalation:'Contact sponsor',lawEnforcement:'Security Operations Center notified',evidenceHandling:'Preserve originals locally'});
  Object.assign(p.assurance,{samplingBasis:'All records in this regression fixture are included.',samplingLimitations:'Fixture validates software behavior, not live security posture.',scopeNotes:'Control-chain analysis is limited to the modeled route.',reviewNotes:'Relationship analysis does not provide bypass instructions.'});
  const site={id:'site-main',code:'SITE-01',name:'Main Campus',type:'SITE',parentId:org.id,description:''};
  const building={id:'bldg-a',code:'BLDG-A',name:'Building A',type:'BUILDING',parentId:site.id,description:''};
  const floor={id:'floor-1',code:'FLOOR-1',name:'Floor 1',type:'FLOOR',parentId:building.id,description:''};
  const publicZone={id:'zone-public',code:'ZONE-PUBLIC',name:'Public Approach',type:'ZONE',parentId:floor.id,description:''};
  const lobby={id:'zone-lobby',code:'ZONE-LOBBY',name:'Lobby',type:'ZONE',parentId:floor.id,description:''};
  const secureZone={id:'zone-secure',code:'ZONE-SECURE',name:'Restricted Records Area',type:'ZONE',parentId:floor.id,description:''};
  const asset={id:'asset-records',code:'ASSET-REC',name:'Protected Records Cabinet',type:'ASSET',parentId:secureZone.id,description:''};
  p.sites=[org,site,building,floor,publicZone,lobby,secureZone,asset];
  p.controls=[
    {id:'control-perimeter',code:'CTRL-PERIM',category:'PERIMETER',type:'Exterior Door',locationId:publicZone.id,location:'',manufacturer:'',model:'',purpose:'Control entry to the building.',configuration:'',condition:'PARTIAL',evidenceIds:['evidence-1']},
    {id:'control-reception',code:'CTRL-RECEP',category:'VISITOR MANAGEMENT',type:'Reception Procedure',locationId:lobby.id,location:'',manufacturer:'',model:'',purpose:'Screen visitors.',configuration:'',condition:'FAILED',evidenceIds:['evidence-2']},
    {id:'control-interior',code:'CTRL-INT',category:'ACCESS CONTROL',type:'Interior Badge Reader',locationId:secureZone.id,location:'',manufacturer:'',model:'',purpose:'Protect restricted records.',configuration:'',condition:'UNKNOWN',evidenceIds:[]}
  ];
  const test=(id,code,controlId,locationId,result)=>({id,code,title:`Test ${code}`,objective:'Evaluate linked control behavior.',controlId,locationId,location:'',preconditions:'Authorization confirmed.',authorizationRequirement:'AUTH-CHAIN-001',method:'Authorized observation.',expected:'Control behaves as designed.',successCriteria:'Secure behavior is observed.',failureCriteria:'Expected secure behavior is not observed.',safety:'Stop for unsafe conditions.',personnel:'Alex Analyst',equipment:'Field notebook',scheduled:'2026-08-23T09:00:00Z',actualStart:'2026-08-23T09:00:00Z',actualEnd:'2026-08-23T09:05:00Z',result,closingNote:'Result recorded.'});
  p.tests=[test('test-perimeter','T-PERIM','control-perimeter',publicZone.id,'PARTIAL'),test('test-reception','T-RECEP','control-reception',lobby.id,'FAILED'),test('test-interior','T-INT','control-interior',secureZone.id,'PARTIAL')];
  p.observations=[{id:'obs-1',code:'OBS-001',timestamp:'2026-08-23T09:02:00Z',observer:'Alex Analyst',site:'Main Campus',locationId:lobby.id,location:'',category:'VISITOR MANAGEMENT',description:'Reception response was inconsistent during the authorized test.',controlId:'control-reception',testId:'test-reception',evidenceIds:['evidence-2'],significance:'Potential control degradation',followUp:true,createdAt:'2026-08-23T09:02:00Z',updatedAt:'2026-08-23T09:02:00Z'}];
  const ev=(id,code,testId,locationId)=>({id,code,filename:`${code}.txt`,type:'NOTE',designation:'ORIGINAL',createdAt:'2026-08-23T09:03:00Z',importedAt:'2026-08-23T09:03:30Z',collector:'Alex Analyst',locationId,location:'',description:`Assessment evidence ${code}`,controlId:'',testIds:[testId],observationIds:[],findingIds:[],positiveObservationIds:[],hash:'',blobStored:false,binaryAvailable:false,hashVerified:null,lastVerifiedAt:'',archived:false,tags:['control-chain'],metadataHistory:[],verificationHistory:[],custody:[],transformations:[],acquisition:{acquiredAt:'2026-08-23T09:03:00Z',sourceDevice:'Field notebook',sourceDescription:'Authorized assessment note',originalFilename:`${code}.txt`,originalMimeType:'text/plain',originalSize:0},photoLog:{caption:'',direction:'',photographer:'Alex Analyst',relatedAssetId:'',includeInReport:false}});
  p.evidence=[ev('evidence-1','E-CHAIN-1','test-perimeter',publicZone.id),ev('evidence-2','E-CHAIN-2','test-reception',lobby.id)];
  p.findings=[{id:'finding-1',code:'PHY-2026-101',title:'Reception control inconsistency',status:'DRAFT',dimensions:{accessImpact:3,exploitability:3,detection:3,response:3,exposure:3,consequence:3},confidence:'MEDIUM',confidenceRationale:'Observed during authorized testing.',locationId:lobby.id,location:'',domain:'VISITOR MANAGEMENT',controlId:'control-reception',description:'Reception response was inconsistent.',expected:'Visitor procedures are consistently applied.',observed:'Procedures were inconsistently applied.',consequence:'Layered protection may be reduced.',preconditions:'Authorized assessment window.',reproducibility:'REPRODUCIBLE',detectionLikelihood:'MEDIUM',recommendation:'Standardize and retest procedures.',compensatingControls:'Guard supervision.',owner:'Security Operations',targetDate:'2026-10-01',testIds:['test-reception'],observationIds:['obs-1'],evidenceIds:['evidence-2'],evidenceRationale:'Linked assessment note.'}];
  p.positiveObservations=[{id:'positive-1',code:'POS-101',title:'Exterior challenge was initiated',status:'DRAFT',locationId:publicZone.id,location:'',controlId:'control-perimeter',description:'Personnel initiated a challenge.',demonstratedBehavior:'Challenge occurred.',operationalValue:'Added a compensating layer.',testIds:['test-perimeter'],evidenceIds:['evidence-1'],evidenceRationale:'Linked assessment note.'}];
  p.controlChains=[{
    id:'chain-1',code:'CHAIN-001',title:'Public approach to protected records',status:'DRAFT',description:'Defense-in-depth relationship model for the authorized assessment.',objective:'Compare the intended route of protection with observed control performance.',locationId:publicZone.id,protectedAssetId:asset.id,mapPlanId:'plan-1',confidence:'HIGH',includeInReport:true,
    expectedPath:[
      {id:'exp-1',recordType:'site',recordId:publicZone.id,layer:'PROPERTY_BOUNDARY',state:'NOT TESTED',note:'Authorized entry point.',evidenceIds:[],findingIds:[]},
      {id:'exp-2',recordType:'control',recordId:'control-perimeter',layer:'EXTERIOR_PERIMETER',state:'NOT TESTED',note:'Exterior control.',evidenceIds:[],findingIds:[]},
      {id:'exp-3',recordType:'control',recordId:'control-reception',layer:'RECEPTION_VISITOR',state:'NOT TESTED',note:'Visitor screening.',evidenceIds:[],findingIds:[]},
      {id:'exp-4',recordType:'control',recordId:'control-interior',layer:'INTERIOR_ACCESS',state:'NOT TESTED',note:'Interior access control.',evidenceIds:[],findingIds:[]},
      {id:'exp-5',recordType:'site',recordId:asset.id,layer:'PROTECTED_ASSETS',state:'NOT TESTED',note:'Protected target.',evidenceIds:[],findingIds:[]}
    ],
    observedPath:[
      {id:'obs-path-1',recordType:'site',recordId:publicZone.id,layer:'PROPERTY_BOUNDARY',state:'WORKED',note:'Authorized approach observed.',evidenceIds:[],findingIds:[]},
      {id:'obs-path-2',recordType:'control',recordId:'control-perimeter',layer:'EXTERIOR_PERIMETER',state:'PARTIALLY WORKED',note:'Control response was inconsistent.',evidenceIds:['evidence-1'],findingIds:[]},
      {id:'obs-path-3',recordType:'test',recordId:'test-reception',layer:'RECEPTION_VISITOR',state:'FAILED',note:'Authorized test did not observe the expected response.',evidenceIds:['evidence-2'],findingIds:['finding-1']},
      {id:'obs-path-4',recordType:'control',recordId:'control-interior',layer:'INTERIOR_ACCESS',state:'INSUFFICIENT EVIDENCE',note:'Assessment window did not establish consistent interior behavior.',evidenceIds:[],findingIds:[]}
    ],
    layers:[
      {id:'layer-1',layer:'PROPERTY_BOUNDARY',state:'WORKED',rationale:'Authorized approach conditions were understood.',controlIds:[],testIds:[],evidenceIds:[],findingIds:[],positiveObservationIds:[]},
      {id:'layer-2',layer:'EXTERIOR_PERIMETER',state:'PARTIALLY WORKED',rationale:'Exterior response was inconsistent.',controlIds:['control-perimeter'],testIds:['test-perimeter'],evidenceIds:['evidence-1'],findingIds:[],positiveObservationIds:['positive-1']},
      {id:'layer-3',layer:'RECEPTION_VISITOR',state:'FAILED',rationale:'Expected visitor screening was not observed.',controlIds:['control-reception'],testIds:['test-reception'],evidenceIds:['evidence-2'],findingIds:['finding-1'],positiveObservationIds:[]},
      {id:'layer-4',layer:'INTERIOR_ACCESS',state:'INSUFFICIENT EVIDENCE',rationale:'Additional testing is required.',controlIds:['control-interior'],testIds:['test-interior'],evidenceIds:[],findingIds:[],positiveObservationIds:[]},
      {id:'layer-5',layer:'SENSITIVE_ROOMS',state:'INSUFFICIENT EVIDENCE',rationale:'Sensitive-room behavior was outside the completed sample.',controlIds:[],testIds:[],evidenceIds:[],findingIds:[],positiveObservationIds:[]}
    ],
    combinedNarrative:'The adjacent perimeter and reception degradation could reduce the independence expected from layered controls; this is an analytical relationship, not an assertion of bypass.',consequenceNarrative:'A failure across independent layers could increase exposure of restricted records if other controls do not compensate.',analystConclusion:'The observed path diverged from the intended sequence and warrants remediation and focused retesting.',statusHistory:[],createdAt:'2026-08-23T10:00:00Z',updatedAt:'2026-08-23T10:00:00Z'
  }];
  p.map={activePlanId:'plan-1',plans:[{id:'plan-1',name:'Building A Relationship Plan',locationId:floor.id,fileName:'',mimeType:'image/png',dataUrl:'',assetStored:false,assetMissing:false,assetHash:'',size:0,markers:[
    {id:'marker-chain',label:'Control Chain',type:'CONTROL CHAIN',locationId:publicZone.id,recordType:'CHAIN',recordId:'chain-1',x:20,y:30},
    {id:'marker-control',label:'Exterior Door',type:'DOOR',locationId:publicZone.id,recordType:'CONTROL',recordId:'control-perimeter',x:35,y:40},
    {id:'marker-asset',label:'Protected Records',type:'SENSITIVE ROOM',locationId:asset.id,recordType:'',recordId:'',x:75,y:55}
  ],zones:[],paths:[],calibration:null,viewport:{zoom:1,panX:0,panY:0},coverageEnabled:true,markerFilter:'ALL'}],markers:[],imageData:null,imageName:''};
  return p;
}"""


with sync_playwright() as p:
    browser = launch_browser(p)
    try:
        page = browser.new_page(viewport={"width": 1600, "height": 1050}, accept_downloads=True)
        page.set_default_timeout(25000)
        errors: list[str] = []
        console_errors: list[str] = []
        dialogs: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14")
        page.evaluate(f"window.__makeControlChainProject={PROJECT_FACTORY}")
        audit = page.evaluate("__SENTINEL_TEST__.setData(window.__makeControlChainProject())")
        check("control-chain-project-audits", audit["ok"], audit)
        page.evaluate("__SENTINEL_TEST__.setView('chains')")
        page.wait_for_selector("#chainsView.active")

        check("release-version-and-schema", page.evaluate("[__SENTINEL_TEST__.appVersion,__SENTINEL_TEST__.schemaVersion]") == ["0.15.0-rc.2", 14])
        check("advanced-control-chain-navigation", page.locator('[data-view="chains"]').count() == 1 and page.locator('[data-view="chains"]').is_visible())
        check("control-chain-workspace-rendered", "Control Chains & Defense in Depth" in page.locator("#chainsView").inner_text())
        check("control-chain-safety-language", "not attack instructions" in page.locator("#chainsView").inner_text().lower())
        check("six-analysis-tabs-rendered", page.locator("[data-chain-tab]").count() == 6)
        check("expected-and-observed-svg-rendered", page.locator("#chainsView svg.chain-path-svg").count() >= 1 and "EXPECTED PATH" in page.locator("#chainsView").inner_text())

        pure = page.evaluate("""() => {
          const p=__SENTINEL_TEST__.getData(),c=p.controlChains[0],reviewed={...c,reviewedBy:'Morgan Reviewer'};
          return {
            layers:c.layers.length,
            comparison:__SENTINEL_TEST__.controlChainComparison(c,p),
            candidates:__SENTINEL_TEST__.combinedWeaknessAnalysis(c,p),
            perimeterSuggestion:__SENTINEL_TEST__.suggestedDefenseLayerState(c,'EXTERIOR_PERIMETER'),
            visitorSuggestion:__SENTINEL_TEST__.suggestedDefenseLayerState(c,'RECEPTION_VISITOR'),
            workflow:__SENTINEL_TEST__.controlChainWorkflowErrors(reviewed,p,'VALIDATED'),
            draftReports:__SENTINEL_TEST__.reportableControlChains(p,false).length,
            previewReports:__SENTINEL_TEST__.reportableControlChains(p,true).length,
            portfolio:__SENTINEL_TEST__.defensePortfolioSummary(p),
            pathSvg:__SENTINEL_TEST__.controlChainPathSvg(c,{standalone:true}),
            layerSvg:__SENTINEL_TEST__.defenseLayerSvg(c,{standalone:true}),
            edges:__SENTINEL_TEST__.traceEdgeList(p),
            graph:__SENTINEL_TEST__.buildTraceGraph({type:'chain',id:c.id},{direction:'ALL',depth:3,maxNodes:120},p)
          };
        }""")
        cmp = pure["comparison"]
        check("sequence-aware-path-comparison", cmp["matchedCount"] == 3 and cmp["divergenceCount"] == 3, cmp)
        check("degraded-and-evidence-limited-nodes-separated", cmp["weakCount"] == 2 and cmp["insufficientCount"] == 1, cmp)
        check("all-eight-defense-layers-normalized", pure["layers"] == 8, pure["layers"])
        check("path-derived-layer-suggestions", pure["perimeterSuggestion"] == "PARTIALLY WORKED" and pure["visitorSuggestion"] == "FAILED", pure)
        check("valid-chain-clears-workflow-gates", pure["workflow"] == [], pure["workflow"])
        check("draft-chain-excluded-from-final-report", pure["draftReports"] == 0 and pure["previewReports"] == 1, pure)
        classifications = [item["classification"] for item in pure["candidates"]]
        check("combined-control-and-evidence-candidates-distinguished", classifications.count("CONTROL INTERACTION") >= 2 and "EVIDENCE LIMITATION" in classifications, pure["candidates"])
        check("portfolio-covers-eight-layers", len(pure["portfolio"]) == 8 and any(item["state"] == "FAILED" for item in pure["portfolio"]), pure["portfolio"])
        check("standalone-path-svg-is-light-readable", 'fill="#ffffff"' in pure["pathSvg"] and "EXPECTED PATH" in pure["pathSvg"] and "OBSERVED PATH" in pure["pathSvg"])
        check("standalone-layer-svg-is-light-readable", 'fill="#ffffff"' in pure["layerSvg"] and "Defense in Depth" in pure["layerSvg"])
        check("traceability-includes-control-chain-edges", any(e["fromType"] == "chain" or e["toType"] == "chain" for e in pure["edges"]), pure["edges"])
        check("traceability-graph-can-root-on-chain", pure["graph"]["root"]["type"] == "chain" and len(pure["graph"]["nodes"]) >= 5, pure["graph"])

        # Layer editor and suggestion workflow.
        page.click('[data-chain-tab="LAYERS"]')
        page.click('[data-edit-chain-layer="INTERIOR_ACCESS"]')
        page.fill("#m_layer_rationale", "Additional authorized testing is required before concluding control effectiveness.")
        page.fill("#m_layer_reviewer", "Alex Analyst")
        page.click("#modalSave")
        page.wait_for_function("!document.querySelector('#modalBack').classList.contains('open')")
        layer = page.evaluate("__SENTINEL_TEST__.getData().controlChains[0].layers.find(x=>x.layer==='INTERIOR_ACCESS')")
        check("defense-layer-review-persists", layer["state"] == "INSUFFICIENT EVIDENCE" and layer["reviewedBy"] == "Alex Analyst" and bool(layer["reviewedAt"]), layer)

        # Lifecycle gate and report integration.
        page.click('[data-chain-status="VALIDATED"]')
        page.fill("#m_chain_reviewer", "Morgan Reviewer")
        page.fill("#m_chain_transition_note", "Expected and observed relationships, evidence limitations, and analyst conclusions reviewed.")
        page.click("#modalSave")
        page.wait_for_function("__SENTINEL_TEST__.getData().controlChains[0].status==='VALIDATED'")
        validated = page.evaluate("__SENTINEL_TEST__.getData().controlChains[0]")
        check("control-chain-lifecycle-validation", validated["status"] == "VALIDATED" and validated["reviewedBy"] == "Morgan Reviewer", validated)
        check("control-chain-lifecycle-history", validated["statusHistory"][-1]["from"] == "DRAFT" and validated["statusHistory"][-1]["to"] == "VALIDATED" and bool(validated["statusHistory"][-1]["rationale"]), validated["statusHistory"])
        check("validated-chain-selected-for-report", page.evaluate("__SENTINEL_TEST__.reportableControlChains(__SENTINEL_TEST__.getData(),false).length") == 1)

        report = page.evaluate("""async () => ({html:await __SENTINEL_TEST__.buildStandaloneReportHtml(),md:__SENTINEL_TEST__.buildMarkdown()})""")
        check("standalone-report-includes-control-chain", "Control Chains & Defense in Depth" in report["html"] and "CHAIN-001" in report["html"] and "Supporting evidence" in report["html"], report["html"][:1000])
        check("standalone-report-embeds-light-diagrams", 'fill="#ffffff"' in report["html"] and "Expected and observed physical security control paths" in report["html"])
        check("standalone-report-preserves-safety-framing", "do not provide bypass instructions" in report["html"])
        check("markdown-report-includes-chain-analysis", "## Control Chains & Defense in Depth" in report["md"] and "E-CHAIN-1" in report["md"] and "Evidence-limited" not in report["md"])
        check("markdown-reports-evidence-limited-count", "evidence-limited observed node(s)" in report["md"])

        # SVG and portfolio exports use the current selected record.
        with page.expect_download(timeout=20000) as info:
            page.click("#exportChainSvg")
        path_export = TMP / info.value.suggested_filename
        info.value.save_as(str(path_export))
        path_text = path_export.read_text(encoding="utf-8")
        check("path-svg-export", path_text.startswith("<svg") and 'fill="#ffffff"' in path_text and "CHAIN-001" in path_text, path_text[:300])
        with page.expect_download(timeout=20000) as info:
            page.click("#exportLayerSvg")
        layer_export = TMP / info.value.suggested_filename
        info.value.save_as(str(layer_export))
        layer_text = layer_export.read_text(encoding="utf-8")
        check("defense-layer-svg-export", layer_text.startswith("<svg") and 'fill="#ffffff"' in layer_text and "Defense in Depth" in layer_text, layer_text[:300])
        with page.expect_download(timeout=20000) as info:
            page.click("#exportPortfolioChains")
        portfolio_export = TMP / info.value.suggested_filename
        info.value.save_as(str(portfolio_export))
        portfolio_text = portfolio_export.read_text(encoding="utf-8")
        check("portfolio-json-export", '"controlChains"' in portfolio_text and '"defensePortfolio"' in portfolio_text and "CHAIN-001" in portfolio_text)

        # Map-linked navigation highlights direct and related records.
        page.click("#showChainMap")
        page.wait_for_selector("#mapView.active")
        check("chain-map-navigation", "Highlighting CHAIN-001" in page.locator("#mapView").inner_text())
        check("chain-map-related-marker-highlights", page.locator("#mapView .marker.chain-highlight").count() >= 3, page.locator("#mapView .marker.chain-highlight").count())

        # Baseline snapshots and semantic path analysis are preserved.
        page.evaluate("__SENTINEL_TEST__.setView('baselines')")
        page.click("#createBaseline")
        page.fill("#m_name", "Validated Control Chain Baseline")
        page.fill("#m_note", "Preserves the reviewed expected and observed paths.")
        page.click("#modalSave")
        baseline = page.evaluate("__SENTINEL_TEST__.getData().baselines.at(-1)")
        check("baseline-preserves-control-chains", len(baseline["snapshot"]["controlChains"]) == 1 and baseline["snapshot"]["controlChains"][0]["status"] == "VALIDATED", baseline)
        diff = page.evaluate("""() => {const p=__SENTINEL_TEST__.getData(),b=p.baselines.at(-1);p.controlChains[0].observedPath[1].state='FAILED';__SENTINEL_TEST__.setData(p);return __SENTINEL_TEST__.baselineDiff(b);}""")
        check("baseline-detects-control-chain-material-change", diff["chainsChanged"] == ["CHAIN-001"], diff)

        # Restore the fixture, sign its assurance state, and prove material chain edits stale sign-off and reopen lifecycle.
        page.evaluate("__SENTINEL_TEST__.setData(window.__makeControlChainProject())")
        page.evaluate("""() => {const p=__SENTINEL_TEST__.getData();p.controlChains[0].status='VALIDATED';p.controlChains[0].reviewedBy='Morgan Reviewer';p.controlChains[0].reviewedAt='2026-08-23T12:00:00Z';p.assurance.signOff={id:'sign-chain',signedBy:'Morgan Reviewer',role:'Assessment Reviewer',signedAt:'2026-08-23T12:05:00Z',statement:'Assessment assurance reviewed.',note:'Control-chain analysis included.',fingerprint:__SENTINEL_TEST__.assuranceFingerprint(p),sha256:'a'.repeat(64),status:'SIGNED'};__SENTINEL_TEST__.setData(p);}""")
        check("chain-inclusive-assurance-signoff-current", page.evaluate("__SENTINEL_TEST__.assuranceSignOffState().state") == "CURRENT")
        page.evaluate("__SENTINEL_TEST__.setView('chains')")
        page.click("#editControlChain")
        page.fill("#m_chain_conclusion", "Materially revised analyst conclusion after additional relationship review.")
        page.click("#modalSave")
        page.wait_for_function("__SENTINEL_TEST__.getData().controlChains[0].status==='DRAFT'")
        changed = page.evaluate("({chain:__SENTINEL_TEST__.getData().controlChains[0],sign:__SENTINEL_TEST__.assuranceSignOffState()})")
        check("material-chain-edit-requires-revalidation", changed["chain"]["status"] == "DRAFT" and changed["chain"]["reviewedBy"] == "" and changed["chain"]["statusHistory"][-1]["to"] == "DRAFT", changed)
        check("material-chain-edit-stales-assurance-signoff", changed["sign"]["state"] == "STALE", changed["sign"])

        # Validation rejects a path that does not reach the protected asset.
        invalid = page.evaluate("""() => {const p=__SENTINEL_TEST__.getData(),c=structuredClone(p.controlChains[0]);c.expectedPath=c.expectedPath.filter(n=>n.recordId!==c.protectedAssetId);c.reviewedBy='Morgan Reviewer';return __SENTINEL_TEST__.controlChainWorkflowErrors(c,p,'VALIDATED');}""")
        check("workflow-requires-protected-asset-in-expected-path", any("protected asset" in item.lower() for item in invalid), invalid)

        # Mobile smoke: workspace remains usable and tabs are horizontally accessible rather than clipping content.
        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.goto(URL, wait_until="domcontentloaded")
        mobile.wait_for_function("window.__SENTINEL_TEST__ && window.__SENTINEL_TEST__.schemaVersion===14")
        mobile.evaluate(f"window.__makeControlChainProject={PROJECT_FACTORY}")
        mobile.evaluate("__SENTINEL_TEST__.setData(window.__makeControlChainProject());__SENTINEL_TEST__.setView('chains')")
        mobile.wait_for_selector("#chainsView.active")
        mobile_metrics = mobile.evaluate("""() => ({body:document.body.scrollWidth,viewport:innerWidth,tabs:document.querySelector('.chain-tabs')?.scrollWidth||0,tabClient:document.querySelector('.chain-tabs')?.clientWidth||0,newVisible:!!document.querySelector('#newControlChain')?.offsetParent})""")
        check("mobile-control-chain-workspace-visible", mobile_metrics["newVisible"], mobile_metrics)
        check("mobile-control-chain-tabs-remain-accessible", mobile_metrics["tabs"] >= mobile_metrics["tabClient"] > 0, mobile_metrics)
        mobile.close()

        check("no-control-chain-page-errors", not errors, errors)
        check("no-control-chain-console-errors", not console_errors, console_errors)
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_control_chains_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
