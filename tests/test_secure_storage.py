"""Encrypted local storage, locking, passphrase rotation, and plaintext restoration checks."""
from __future__ import annotations

import os
import traceback
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

OLD_PASS = "Old-SENTINEL-passphrase-2026"
NEW_PASS = "New-SENTINEL-passphrase-2026"
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
        context = browser.new_context(viewport={"width": 1500, "height": 1000})
        page = context.new_page()
        page.set_default_timeout(30000)
        errors: list[str] = []
        dialogs: list[tuple[str, str]] = []

        def handle_dialog(dialog):
            dialogs.append((dialog.type, dialog.message))
            dialog.accept()

        page.on("dialog", handle_dialog)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        project_id = page.evaluate("""async () => {
          const p=__SENTINEL_TEST__.blankProject();
          Object.assign(p.project,{name:'Protected Local Project',client:'Sensitive Client',site:'Secure Site',lead:'Analyst',classification:'CONTROLLED'});
          p.mode='advanced';p.settings.currentOperator='Storage Analyst';
          const planId=crypto.randomUUID();
          p.map.plans=[{id:planId,name:'Secure Floor Plan',fileName:'plan.png',mimeType:'image/png',assetStored:true,assetHash:'',hashVerified:null,size:8,locationId:'',markers:[],zones:[],paths:[],scale:null,viewport:{zoom:1,x:0,y:0}}];
          p.map.activePlanId=planId;
          const evidenceId=crypto.randomUUID(),evidenceBlob=new Blob(['first-capture'],{type:'image/png'}),digest=await crypto.subtle.digest('SHA-256',await evidenceBlob.arrayBuffer()),evidenceHash=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
          p.evidence=[{id:evidenceId,code:'E-0001',filename:'first.png',type:'PHOTO',createdAt:new Date().toISOString(),importedAt:new Date().toISOString(),collector:'Storage Analyst',description:'Protected evidence',designation:'ORIGINAL',hash:evidenceHash,size:evidenceBlob.size,mimeType:evidenceBlob.type,blobStored:true,binaryAvailable:true,binaryLocked:true,hashVerified:true,lastVerifiedAt:new Date().toISOString(),tags:[],testIds:[],observationIds:[],findingIds:[],positiveObservationIds:[],verificationHistory:[],custody:[],metadataHistory:[],transformationHistory:[],photoLog:{caption:'',direction:'',photographer:'Storage Analyst',relatedAssetId:'',includeInReport:false,reportOrder:1}}];
          __SENTINEL_TEST__.setData(p);
          await __SENTINEL_TEST__.storeEvidenceBlob(evidenceId,evidenceBlob,evidenceHash);
          await __SENTINEL_TEST__.save();
          const evidence=__SENTINEL_TEST__.getData().evidence[0];
          const second=await __SENTINEL_TEST__.stageCapture(new Blob(['queued-capture'],{type:'audio/webm'}),{kind:'AUDIO',filename:'queued.webm',actor:'Storage Analyst'});
          await __SENTINEL_TEST__.rawIdbGet('projects',p.id);
          const db=__SENTINEL_TEST__.getDb();
          const put=(store,value)=>new Promise((resolve,reject)=>{const tx=db.transaction(store,'readwrite');tx.objectStore(store).put(value);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});
          await put('assets',{id:planId,projectId:p.id,kind:'map-plan',filename:'plan.png',mimeType:'image/png',sha256:'asset-test',storedAt:new Date().toISOString(),blob:new Blob(['map-plan'],{type:'image/png'})});
          await put('checkpoints',{id:crypto.randomUUID(),projectId:p.id,projectName:p.project.name,createdAt:new Date().toISOString(),label:'Security test checkpoint',schemaVersion:11,snapshot:__SENTINEL_TEST__.getData()});
          return {projectId:p.id,evidenceId:evidence.id,evidenceHash:evidence.hash,pendingId:second.id,planId};
        }""")
        page.wait_for_function("document.querySelector('#autosaveText').textContent==='SAVED'")

        initial = page.evaluate("""async id => ({
          projects:(await __SENTINEL_TEST__.rawIdbAll('projects')).filter(x=>x.id===id).length,
          evidence:(await __SENTINEL_TEST__.rawIdbAll('evidence')).filter(x=>x.projectId===id).length,
          assets:(await __SENTINEL_TEST__.rawIdbAll('assets')).filter(x=>x.projectId===id).length,
          checkpoints:(await __SENTINEL_TEST__.rawIdbAll('checkpoints')).filter(x=>x.projectId===id).length,
          captureQueue:(await __SENTINEL_TEST__.rawIdbAll('captureQueue')).filter(x=>x.projectId===id).length
        })""", project_id["projectId"])
        check("plaintext-stores-seeded", initial["projects"] == 1 and initial["evidence"] == 1 and initial["assets"] == 1 and initial["captureQueue"] == 1 and initial["checkpoints"] >= 1, initial)
        checkpoint_count = initial["checkpoints"]

        page.evaluate("__SENTINEL_TEST__.setView('security')")
        page.click("#enableEncryptBtn")
        submit_secret(page, OLD_PASS, OLD_PASS)
        page.wait_for_function("__SENTINEL_TEST__.projectStorageEncrypted() === true", timeout=60000)
        page.wait_for_timeout(400)

        encrypted = page.evaluate("""async id => {
          const stores=['projects','evidence','assets','checkpoints','captureQueue'];
          const out={plain:{},secure:{}};
          for(const store of stores){
            out.plain[store]=(await __SENTINEL_TEST__.rawIdbAll(store)).filter(x=>(x.projectId||x.id)===id).length;
            const secureName={projects:'secureProjects',evidence:'secureEvidence',assets:'secureAssets',checkpoints:'secureCheckpoints',captureQueue:'secureCaptureQueue'}[store];
            out.secure[store]=(await __SENTINEL_TEST__.rawIdbAll(secureName)).filter(x=>x.projectId===id).length;
          }
          out.registry=__SENTINEL_TEST__.getSecurityRecord(id);
          out.localKeys=Object.keys(localStorage).filter(k=>k.startsWith('sentinel.project.'));
          return out;
        }""", project_id["projectId"])
        check("plaintext-records-removed-after-encryption", all(v == 0 for v in encrypted["plain"].values()), encrypted)
        check("all-project-stores-encrypted", encrypted["secure"]["projects"] == 1 and encrypted["secure"]["evidence"] == 1 and encrypted["secure"]["assets"] == 1 and encrypted["secure"]["captureQueue"] == 1 and encrypted["secure"]["checkpoints"] == checkpoint_count, encrypted)
        check("security-registry-encrypted", encrypted["registry"]["storageEncrypted"] is True and encrypted["registry"]["screenLockEnabled"] is True, encrypted["registry"])
        check("plaintext-recovery-shadow-removed", encrypted["localKeys"] == [], encrypted["localKeys"])

        # Lock, reload, reject the wrong passphrase, then restore with the correct passphrase.
        page.evaluate("__SENTINEL_TEST__.lockWorkspace('Validation lock')")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        check("encrypted-workspace-remains-locked-after-reload", page.locator("#lockProjectLabel").inner_text() != "")
        page.fill("#unlockPassphrase", "wrong-passphrase")
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#unlockBtn').disabled && document.querySelector('#lockError').textContent && !document.querySelector('#lockError').textContent.startsWith('Unlocking')", timeout=60000)
        check("wrong-local-passphrase-rejected", "incorrect" in page.locator("#lockError").inner_text().lower() or "authenticated" in page.locator("#lockError").inner_text().lower(), page.locator("#lockError").inner_text())
        page.fill("#unlockPassphrase", OLD_PASS)
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#lockScreen').classList.contains('open')", timeout=60000)
        restored = page.evaluate("__SENTINEL_TEST__.getData()")
        check("encrypted-project-restored", restored["id"] == project_id["projectId"] and restored["project"]["name"] == "Protected Local Project", restored["project"])
        restored_blob = page.evaluate("""async id => {const r=await __SENTINEL_TEST__.getEvidenceBlob(id);return r?{size:r.blob.size,sha:r.sha256}:null}""", project_id["evidenceId"])
        check("encrypted-evidence-restored", bool(restored_blob) and restored_blob["sha"] == project_id["evidenceHash"], restored_blob)
        queue = page.evaluate("__SENTINEL_TEST__.getPendingCaptures()")
        check("encrypted-pending-capture-restored", len(queue) == 1 and queue[0]["id"] == project_id["pendingId"], queue)

        # Rotate the wrapping passphrase after a real reload.
        page.evaluate("__SENTINEL_TEST__.setView('security')")
        page.click("#changePassBtn")
        submit_secret(page, OLD_PASS)
        submit_secret(page, NEW_PASS, NEW_PASS)
        page.wait_for_timeout(400)
        check("passphrase-change-confirmed", any("passphrase changed" in message.lower() for _, message in dialogs), dialogs[-3:])
        page.evaluate("__SENTINEL_TEST__.lockWorkspace('Passphrase rotation test')")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.fill("#unlockPassphrase", OLD_PASS)
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#unlockBtn').disabled && document.querySelector('#lockError').textContent && !document.querySelector('#lockError').textContent.startsWith('Unlocking')", timeout=60000)
        check("old-passphrase-rejected-after-rotation", "incorrect" in page.locator("#lockError").inner_text().lower() or "authenticated" in page.locator("#lockError").inner_text().lower(), page.locator("#lockError").inner_text())
        page.fill("#unlockPassphrase", NEW_PASS)
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#lockScreen').classList.contains('open')", timeout=60000)
        check("new-passphrase-unlocks", page.evaluate("__SENTINEL_TEST__.getData().id") == project_id["projectId"])

        # Decrypt all local records while retaining the independent screen lock.
        page.evaluate("__SENTINEL_TEST__.setView('security')")
        page.click("#disableEncryptBtn")
        submit_secret(page, NEW_PASS)
        page.wait_for_function("__SENTINEL_TEST__.projectStorageEncrypted() === false", timeout=60000)
        page.wait_for_timeout(300)
        decrypted = page.evaluate("""async id => {
          const stores=['projects','evidence','assets','checkpoints','captureQueue'];
          const out={plain:{},secure:{}};
          for(const store of stores){
            out.plain[store]=(await __SENTINEL_TEST__.rawIdbAll(store)).filter(x=>(x.projectId||x.id)===id).length;
            const secureName={projects:'secureProjects',evidence:'secureEvidence',assets:'secureAssets',checkpoints:'secureCheckpoints',captureQueue:'secureCaptureQueue'}[store];
            out.secure[store]=(await __SENTINEL_TEST__.rawIdbAll(secureName)).filter(x=>x.projectId===id).length;
          }
          out.registry=__SENTINEL_TEST__.getSecurityRecord(id);
          return out;
        }""", project_id["projectId"])
        check("plaintext-stores-restored-after-decryption", decrypted["plain"]["projects"] == 1 and decrypted["plain"]["evidence"] == 1 and decrypted["plain"]["assets"] == 1 and decrypted["plain"]["captureQueue"] == 1 and decrypted["plain"]["checkpoints"] >= checkpoint_count, decrypted)
        check("secure-stores-cleared-after-decryption", all(v == 0 for v in decrypted["secure"].values()), decrypted)
        check("screen-lock-retained-after-decryption", decrypted["registry"]["storageEncrypted"] is False and decrypted["registry"]["screenLockEnabled"] is True, decrypted["registry"])
        plain_blob = page.evaluate("""async id => {const r=await __SENTINEL_TEST__.getEvidenceBlob(id);return r?{sha:r.sha256,size:r.blob.size}:null}""", project_id["evidenceId"])
        check("evidence-hash-preserved-through-encrypt-decrypt", bool(plain_blob) and plain_blob["sha"] == project_id["evidenceHash"], plain_blob)

        # Screen-lock-only mode must survive reload while leaving ordinary IndexedDB records intact.
        page.evaluate("__SENTINEL_TEST__.lockWorkspace('Screen-lock-only validation')")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("document.querySelector('#lockScreen').classList.contains('open')")
        lock_only_stores = page.evaluate("""async id => ({plain:(await __SENTINEL_TEST__.rawIdbAll('projects')).filter(x=>x.id===id).length,secure:(await __SENTINEL_TEST__.rawIdbAll('secureProjects')).filter(x=>x.projectId===id).length})""", project_id["projectId"])
        check("screen-lock-only-keeps-plaintext-indexeddb", lock_only_stores == {"plain": 1, "secure": 0}, lock_only_stores)
        page.fill("#unlockPassphrase", NEW_PASS)
        page.click("#unlockBtn")
        page.wait_for_function("!document.querySelector('#lockScreen').classList.contains('open')", timeout=60000)
        check("screen-lock-only-unlocks-after-reload", page.evaluate("__SENTINEL_TEST__.getData().id") == project_id["projectId"])
        audit = page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("secure-storage-roundtrip-audit", audit["ok"], audit)
        check("secure-storage-runtime-clean", not errors, errors)
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_secure_storage_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
