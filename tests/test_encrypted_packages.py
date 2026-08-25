"""Authenticated encrypted-package export, decryption, and clean-profile import checks."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from common import URL, launch_browser

PASS = "Portable-package-passphrase-2026"
TMP = Path(os.environ.get("SENTINEL_TEST_TMP", "/tmp"))
PACKAGE = TMP / "protected-package.sentinel.enc"
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
        context = browser.new_context(viewport={"width": 1450, "height": 950}, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(30000)
        errors: list[str] = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")

        seed = page.evaluate("""async () => {
          const p=__SENTINEL_TEST__.blankProject();
          Object.assign(p.project,{name:'Package Secret Alpha',client:'Confidential Client Omega',site:'Restricted Facility Zeta',lead:'Package Analyst',classification:'CONTROLLED'});
          p.mode='advanced';p.settings.currentOperator='Package Analyst';
          const evidenceId=crypto.randomUUID(),evidenceBlob=new Blob(['highly-sensitive-binary-content'],{type:'image/png'}),digest=await crypto.subtle.digest('SHA-256',await evidenceBlob.arrayBuffer()),evidenceHash=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');
          p.evidence=[{id:evidenceId,code:'E-0001',filename:'secret-photo-alpha.png',type:'PHOTO',createdAt:new Date().toISOString(),importedAt:new Date().toISOString(),collector:'Package Analyst',description:'Sensitive package evidence',designation:'ORIGINAL',hash:evidenceHash,size:evidenceBlob.size,mimeType:evidenceBlob.type,blobStored:true,binaryAvailable:true,binaryLocked:true,hashVerified:true,lastVerifiedAt:new Date().toISOString(),tags:[],testIds:[],observationIds:[],findingIds:[],positiveObservationIds:[],verificationHistory:[],custody:[],metadataHistory:[],transformationHistory:[],photoLog:{caption:'Restricted entry photograph',direction:'',photographer:'Package Analyst',relatedAssetId:'',includeInReport:true,reportOrder:1}}];
          __SENTINEL_TEST__.setData(p);
          await __SENTINEL_TEST__.storeEvidenceBlob(evidenceId,evidenceBlob,evidenceHash);
          await __SENTINEL_TEST__.save();
          const evidence=__SENTINEL_TEST__.getData().evidence[0];
          const manifest=await __SENTINEL_TEST__.buildPackageManifest({custodyDestination:'Encrypted package validation'});
          const outer=await __SENTINEL_TEST__.encryptPackageManifest(manifest,'Portable-package-passphrase-2026');
          let wrong='';try{await __SENTINEL_TEST__.decryptEncryptedPackage(outer,'wrong-password');}catch(e){wrong=e.message;}
          const opened=await __SENTINEL_TEST__.decryptEncryptedPackage(outer,'Portable-package-passphrase-2026');
          return {outer:JSON.stringify(outer),wrong,openedName:opened.project.project.name,evidenceId:evidence.id,evidenceHash:evidence.hash,projectId:p.id};
        }""")
        outer = json.loads(seed["outer"])
        outer_text = seed["outer"]
        check("encrypted-package-format", outer["format"] == "SENTINEL_ENCRYPTED_PACKAGE" and outer["formatVersion"] == 1 and outer["schemaVersion"] == 14, {k: outer.get(k) for k in ["format", "formatVersion", "schemaVersion"]})
        check("encrypted-package-kdf", outer["kdf"]["name"] == "PBKDF2" and outer["kdf"]["hash"] == "SHA-256" and outer["kdf"]["iterations"] >= 250000, outer["kdf"])
        check("encrypted-package-aead", outer["encryption"]["name"] == "AES-GCM" and bool(outer["encryption"]["iv"]) and bool(outer["ciphertext"]), outer["encryption"])
        sensitive = ["Package Secret Alpha", "Confidential Client Omega", "Restricted Facility Zeta", "secret-photo-alpha.png", "highly-sensitive-binary-content"]
        check("encrypted-envelope-hides-project-metadata", not any(value in outer_text for value in sensitive), [value for value in sensitive if value in outer_text])
        check("wrong-package-passphrase-rejected", "incorrect" in seed["wrong"].lower() or "damaged" in seed["wrong"].lower(), seed["wrong"])
        check("correct-package-passphrase-restores-manifest", seed["openedName"] == "Package Secret Alpha", seed["openedName"])

        # Exercise the user-facing encrypted export, including export acknowledgement.
        page.evaluate("__SENTINEL_TEST__.setView('security')")
        page.click("#securityExportEncrypted")
        page.wait_for_selector("#export_ack")
        page.check("#export_ack")
        page.locator(".secret-prompt button.primary").click()
        page.wait_for_selector(".secret-prompt-back")
        page.fill("#sp_one", PASS)
        page.fill("#sp_two", PASS)
        with page.expect_download(timeout=60000) as download_info:
            page.locator(".secret-prompt button.primary").click()
        download_info.value.save_as(str(PACKAGE))
        downloaded = json.loads(PACKAGE.read_text(encoding="utf-8"))
        check("encrypted-package-download-created", PACKAGE.exists() and PACKAGE.stat().st_size > 500, PACKAGE.stat().st_size if PACKAGE.exists() else 0)
        check("downloaded-envelope-hides-sensitive-data", not any(value in PACKAGE.read_text(encoding="utf-8") for value in sensitive), "sensitive plaintext present")
        check("downloaded-package-authenticated", downloaded["format"] == "SENTINEL_ENCRYPTED_PACKAGE" and downloaded["encryption"]["name"] == "AES-GCM", downloaded)

        # Import the protected package into a clean browser profile.
        clean = browser.new_context(viewport={"width": 1450, "height": 950})
        imported_page = clean.new_page()
        imported_errors: list[str] = []
        imported_page.on("pageerror", lambda exc: imported_errors.append(str(exc)))
        imported_page.on("console", lambda msg: imported_errors.append(msg.text) if msg.type == "error" and "favicon" not in msg.text else None)
        imported_page.goto(URL, wait_until="domcontentloaded")
        imported_page.wait_for_function("window.__SENTINEL_TEST__ && document.querySelector('#storageLabel').textContent.includes('IndexedDB')")
        imported_page.set_input_files("#importInput", str(PACKAGE))
        submit_secret(imported_page, PASS)
        imported_page.wait_for_function("__SENTINEL_TEST__.getData().project.name==='Package Secret Alpha'", timeout=60000)
        imported_page.wait_for_function("document.querySelector('#autosaveText').textContent==='SAVED'", timeout=30000)
        imported = imported_page.evaluate("__SENTINEL_TEST__.getData()")
        check("encrypted-package-import-restores-project", imported["project"]["client"] == "Confidential Client Omega" and len(imported["evidence"]) == 1, imported["project"])
        check("imported-package-does-not-inherit-device-lock", imported["security"]["storageEncrypted"] is False and imported["security"]["screenLockEnabled"] is False, imported["security"])
        imported_blob = imported_page.evaluate("""async () => {const e=__SENTINEL_TEST__.getData().evidence[0],r=await __SENTINEL_TEST__.getEvidenceBlob(e.id);return {hash:e.hash,storedHash:r?.sha256,size:r?.blob?.size,verified:e.hashVerified,binaryAvailable:e.binaryAvailable}}""")
        check("encrypted-package-import-verifies-binary", imported_blob["hash"] == imported_blob["storedHash"] and imported_blob["size"] > 0 and imported_blob["verified"] is True and imported_blob["binaryAvailable"] is True, imported_blob)
        imported_audit = imported_page.evaluate("__SENTINEL_TEST__.auditProject(__SENTINEL_TEST__.getData())")
        check("encrypted-package-import-audit", imported_audit["ok"], imported_audit)
        check("encrypted-package-runtime-clean", not errors and not imported_errors, {"source": errors, "import": imported_errors})
        clean.close()
        context.close()
        browser.close()
    except Exception as exc:
        print("FAILED", repr(exc), flush=True)
        traceback.print_exc()
        try:
            page.screenshot(path="/tmp/sentinel_encrypted_packages_failure.png", full_page=True)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        os._exit(1)

print(f"ALL PASS {len(checks)} assertions", flush=True)
print(f"ASSERTIONS={len(checks)}", flush=True)
