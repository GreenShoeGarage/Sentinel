#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import re, json, hashlib, subprocess, tempfile, os, sys, datetime as dt
ROOT=Path(__file__).resolve().parents[2]; htmlp=ROOT/'index.html'; text=htmlp.read_text('utf-8',errors='ignore')
results=[]
def chk(name,ok,detail=''):
    results.append({'name':name,'passed':bool(ok),'detail':str(detail)[:2000]})
class P(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.scripts=[]; self.in_script=False; self.attrs={}; self.buf=[]; self.remotes=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        for k in ('src','href'):
            v=d.get(k,'')
            if re.match(r'https?://',v): self.remotes.append((tag,k,v))
        if tag=='script': self.in_script=True; self.attrs=d; self.buf=[]
    def handle_data(self,data):
        if self.in_script:self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.in_script:
            if not self.attrs.get('src') and self.attrs.get('type','').lower() not in {'application/json','application/ld+json'}:
                self.scripts.append((''.join(self.buf),self.attrs))
            self.in_script=False; self.buf=[]; self.attrs={}
p=P(); p.feed(text)
dups=sorted({x for x in p.ids if p.ids.count(x)>1})
chk('Application source exists',htmlp.exists(),htmlp.stat().st_size)
chk('Application identifies Version 0.15.0-rc.1','0.15.0-rc.1' in text)
chk('Application identifies Project Schema 14',bool(re.search(r'(?:schemaVersion|SCHEMA_VERSION|PROJECT_SCHEMA|Schema)[^\n<]{0,80}\b14\b',text,re.I)))
chk('No duplicate static element identifiers',not dups,dups[:50])
chk('No remote script or stylesheet dependencies',not p.remotes,p.remotes[:30])
chk('Inline JavaScript is present',len(p.scripts)>0,len(p.scripts))
node=[]
for i,(script,attrs) in enumerate(p.scripts):
    # Module syntax is checked using .mjs; ordinary script uses .js.
    suf='.mjs' if attrs.get('type','').lower()=='module' else '.js'
    fp=ROOT/'test-results'/f'inline_{i}{suf}'; fp.parent.mkdir(exist_ok=True); fp.write_text(script,encoding='utf-8')
    cp=subprocess.run(['node','--check',str(fp)],text=True,capture_output=True)
    node.append({'script':i,'returncode':cp.returncode,'stderr':cp.stderr[-4000:]})
chk('All inline JavaScript passes node --check',all(x['returncode']==0 for x in node),node)
# Governance and output surface checks (implementation-agnostic language patterns).
patterns={
'Persistent report artifact':r'reportArtifact|reportBuilder|reportModel',
'Ordered composition':r'sectionOrder|moveSection|reorder.*section',
'Custom report sections':r'customSections?|custom section',
'Executive summary':r'executiveSummary',
'Methodology':r'methodology',
'Limitations':r'limitations',
'Conclusion':r'conclusion',
'Branding':r'clientLogo|branding|logoData',
'Selected evidence':r'selectedEvidence|evidenceSelection|reportEvidence',
'Appendix controls':r'appendix|appendices',
'Review lifecycle':r'IN_REVIEW|submit.*review|reviewedBy',
'Approval lifecycle':r'APPROVED|approvedBy|approver',
'Final issue lifecycle':r'FINAL_ISSUE|ISSUED|final issue',
'Revision history':r'revisionHistory|reportRevisions|revision history',
'Issue hash':r'issueHash|issueFingerprint|reportHash',
'Staleness detection':r'stale|material.*fingerprint',
'Final issue locking':r'finalIssue.*lock|issued.*lock|isReportLocked|immutable',
'HTML output':r'export.*html|text/html',
'Markdown output':r'export.*markdown|text/markdown',
'JSON output':r'export.*json|application/json',
'Report package':r'report package|exportReportPackage|report-package',
'Print/PDF':r'window\.print|@media print|print.*pdf',
}
for n,pat in patterns.items(): chk(n,bool(re.search(pat,text,re.I|re.S)))
passed=all(r['passed'] for r in results)
out={'suite':'Static release checks','timestamp':dt.datetime.now(dt.timezone.utc).isoformat(),'passed':passed,'assertions':results,'source_sha256':hashlib.sha256(htmlp.read_bytes()).hexdigest()}
(ROOT/'test-results'/'static_release_results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(ROOT/'test-results'/'static_release_results.txt').write_text(('PASS' if passed else 'FAIL')+f" {sum(r['passed'] for r in results)}/{len(results)}\n"+'\n'.join(f"{'PASS' if r['passed'] else 'FAIL'} {r['name']}: {r['detail']}" for r in results)+'\n',encoding='utf-8')
sys.exit(0 if passed else 1)
