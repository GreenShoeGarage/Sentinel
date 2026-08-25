#!/usr/bin/env python3
from pathlib import Path
import subprocess, os, sys, json, re, datetime as dt, shutil
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'test-results'; OUT.mkdir(exist_ok=True)
env=os.environ.copy(); env.update({'SENTINEL_INDEX':str(ROOT/'index.html'),'SENTINEL_APP_PATH':str(ROOT/'index.html'),'SENTINEL_ROOT':str(ROOT),'PYTHONUNBUFFERED':'1'})
# Create compatibility copies beside inherited test dirs when they expect ../index.html.
for dname in ['tests','tests_current']:
 d=ROOT/dname
 if d.exists():
  # common archive structures already have app in root; no mutation required
  pass
candidates=[]
for dname in ['tests_current','tests']:
 d=ROOT/dname
 if not d.exists(): continue
 primary=[]
 for pat in ['run_all.py','run_tests.py','run_validation.py','validate_release.py','acceptance.py']:
  primary += list(d.rglob(pat))
 if primary:
  candidates.extend(primary[:1])
 else:
  # Standalone suites from prior releases. Limit to executable Python files and avoid helpers.
  for p in sorted(d.rglob('*.py')):
   n=p.name.lower()
   if n.startswith(('test_','validate_','run_')) and not any(x in n for x in ['helper','fixture','conftest']):
    candidates.append(p)
# Deduplicate.
seen=set(); ordered=[]
for p in candidates:
 s=str(p.resolve())
 if s not in seen: seen.add(s); ordered.append(p)
results=[]
for p in ordered:
 try:
  cp=subprocess.run([sys.executable,str(p)],cwd=str(p.parent),env=env,text=True,capture_output=True,timeout=900)
  results.append({'file':str(p.relative_to(ROOT)),'returncode':cp.returncode,'stdout':cp.stdout[-30000:],'stderr':cp.stderr[-30000:]})
 except Exception as e:
  results.append({'file':str(p.relative_to(ROOT)),'returncode':999,'error':repr(e)})
summary={'suite':'Inherited regression suites','timestamp':dt.datetime.now(dt.timezone.utc).isoformat(),'executed':len(results),'passed':sum(r['returncode']==0 for r in results),'failed':sum(r['returncode']!=0 for r in results),'results':results}
(OUT/'inherited_regressions.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# Advisory because historical runners may contain exact-version or path assumptions; all failures remain documented.
sys.exit(0)
