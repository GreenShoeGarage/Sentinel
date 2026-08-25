#!/usr/bin/env python3
from pathlib import Path
import zipfile, json, re, hashlib, datetime as dt, sys
ROOT=Path(__file__).resolve().parents[2]; out=ROOT/'test-results'; files=[]
for p in out.iterdir() if out.exists() else []:
 if p.is_file() and ('report' in p.name.lower() or 'assessment' in p.name.lower()) and p.suffix.lower() in {'.zip','.report','.sentinel','.pkg'}: files.append(p)
files.sort(key=lambda p:p.stat().st_mtime,reverse=True)
A=[]
def chk(n,o,d=''): A.append({'name':n,'passed':bool(o),'detail':str(d)[:3000]})
chk('A report package download exists',bool(files),[p.name for p in files])
manifest=None; names=[]; pkg=files[0] if files else None
if pkg:
 try:
  with zipfile.ZipFile(pkg) as z:
   names=z.namelist()
   mans=[n for n in names if re.search(r'manifest.*\.json$',n,re.I)]
   chk('Report package is a valid ZIP archive',True,len(names))
   chk('Report package contains a manifest',bool(mans),names)
   if mans:
    manifest=json.loads(z.read(mans[0]).decode('utf-8'))
   chk('Report package contains standalone HTML',any(n.lower().endswith(('.html','.htm')) for n in names),names)
   chk('Report package contains Markdown or structured JSON',any(n.lower().endswith(('.md','.json')) and 'manifest' not in n.lower() for n in names),names)
   chk('Report package does not contain a SENTINEL project database',not any(re.search(r'project\.(sentinel|db|sqlite)$',n,re.I) for n in names),names)
   # The manifest should identify report/revision/issue and selected evidence.
   mtxt=json.dumps(manifest or {})
   chk('Manifest identifies the report revision or issue',bool(re.search(r'revision|issue|report',mtxt,re.I)),mtxt[:1000])
   evidence_files=[n for n in names if re.search(r'(^|/)(evidence|media|attachments?)/',n,re.I) and not n.endswith('/')]
   # Compare against any manifest evidence list/count when exposed.
   selected=[]
   if isinstance(manifest,dict):
    for key in ['evidence','selectedEvidence','includedEvidence','files']:
     v=manifest.get(key)
     if isinstance(v,list):
      cand=[x for x in v if isinstance(x,(str,dict))]
      if key!='files' or any(('evidence' in str(x).lower()) for x in cand): selected=cand; break
   chk('Package evidence is explicitly manifested',not evidence_files or bool(selected) or 'evidenceCount' in (manifest or {}),{'evidence_files':evidence_files,'manifest_keys':list((manifest or {}).keys())})
 except Exception as e:
  chk('Report package is a valid ZIP archive',False,repr(e))
passed=all(a['passed'] for a in A)
res={'suite':'Report package inspection','timestamp':dt.datetime.now(dt.timezone.utc).isoformat(),'passed':passed,'package':str(pkg) if pkg else None,'assertions':A,'entries':names,'manifest':manifest}
(out/'report_package_inspection.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
(out/'report_package_inspection.txt').write_text(('PASS' if passed else 'FAIL')+f" {sum(a['passed'] for a in A)}/{len(A)}\n"+'\n'.join(f"{'PASS' if a['passed'] else 'FAIL'} {a['name']}: {a['detail']}" for a in A)+'\n',encoding='utf-8')
sys.exit(0 if passed else 1)
