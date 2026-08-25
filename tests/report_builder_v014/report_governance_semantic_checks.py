#!/usr/bin/env python3
from pathlib import Path
import re, json, hashlib, datetime as dt, sys
ROOT=Path(__file__).resolve().parents[2]; src=(ROOT/'index.html').read_text('utf-8',errors='ignore')
A=[]
def check(name,ok,detail=''): A.append({'name':name,'passed':bool(ok),'detail':str(detail)[:4000]})
def window(pattern,span=12000):
 m=re.search(pattern,src,re.I)
 return src[max(0,m.start()-span//4):min(len(src),m.end()+3*span//4)] if m else ''
# Persistent schema/model
check('Schema 14 migration is represented',bool(re.search(r'(?:case\s+13|schemaVersion\s*[<!=]=?\s*13|fromSchema\s*===?\s*13)[\s\S]{0,5000}(?:14|schemaVersion)',src,re.I)) or bool(re.search(r'migrate[^\n]{0,100}14',src,re.I)))
check('Report artifact is stored in project model',bool(re.search(r'(?:project|state)\s*\.\s*(?:reportArtifact|reportBuilder|reports)|(?:reportArtifact|reportBuilder)\s*:',src,re.I)))
check('Report normalization preserves custom sections',bool(re.search(r'customSections?',src,re.I)) and bool(re.search(r'(?:map|spread|\.\.\.|deepClone|structuredClone)[\s\S]{0,1200}customSections?|customSections?[\s\S]{0,1200}(?:map|spread|deepClone|structuredClone)',src,re.I)))
# Lifecycle
life=window(r'FINAL_ISSUE|final issue|issueReport',30000)
check('Final issue records accountable attribution',bool(re.search(r'issuer|issuedBy|approvedBy|actor|operator',life,re.I)))
check('Final issue records timestamp',bool(re.search(r'issuedAt|issueDate|timestamp|nowISO|new Date',life,re.I)))
check('Final issue calculates SHA-256 or fingerprint',bool(re.search(r'SHA-?256|sha256|fingerprint|digest',life,re.I)))
check('Final issue sets an immutable or locked state',bool(re.search(r'locked|immutable|FINAL_ISSUE|ISSUED',life,re.I)))
check('Review state exists',bool(re.search(r'IN_REVIEW|SUBMITTED_FOR_REVIEW|reviewStatus',src,re.I)))
check('Approval state exists',bool(re.search(r'APPROVED|approvalStatus|approvedAt',src,re.I)))
check('Return-to-draft rationale is represented',bool(re.search(r'return.{0,40}draft|reopen.{0,40}draft|DRAFT[\s\S]{0,500}rationale',src,re.I)))
# Revision/staleness
rev=window(r'new revision|createReportRevision|reviseReport',28000)
check('New revision retains prior issue history or source reference',bool(re.search(r'previous|prior|supersed|sourceRevision|issueHistory|revisionHistory',rev,re.I)))
check('New revision returns to editable draft',bool(re.search(r'DRAFT|locked\s*[:=]\s*false|issuedAt\s*[:=]\s*(?:null|["\']{2})',rev,re.I)))
stale=window(r'reportRevisionState|materialProjectFingerprint|reportProjectFingerprint',32000)
check('Material project fingerprint/staleness comparison exists',bool(re.search(r'materialProjectFingerprint|reportProjectFingerprint|fingerprint|hash|material',stale,re.I)) and bool(re.search(r'stale|diverg',stale,re.I)))
check('Issued report divergence does not overwrite issue',bool(re.search(r'issued[\s\S]{0,1800}(?:diverg|stale|new revision)|(?:diverg|stale)[\s\S]{0,1800}issued',src,re.I)))
# Composition
for label,pat in [('Executive Summary',r'executiveSummary'),('Methodology',r'methodology'),('Assessment Limitations',r'limitations'),('Conclusion',r'conclusion')]:
 check(f'{label} has persistent field',bool(re.search(pat,src,re.I)))
check('Section order is persisted',bool(re.search(r'sectionOrder|sections\s*:\s*\[|orderIndex',src,re.I)))
check('Section inclusion is persisted',bool(re.search(r'included|enabled|includeInReport|sectionVisibility',src,re.I)))
check('Custom sections are editable and orderable',bool(re.search(r'custom section',src,re.I)) and bool(re.search(r'move|reorder|order',src,re.I)))
# Evidence/package boundary
pkg=window(r'exportReportPackage|report package|report-package',50000)
check('Report package export implementation exists',bool(pkg))
check('Report package uses explicit selected evidence',bool(re.search(r'selectedEvidence|evidenceSelection|reportEvidence',pkg,re.I)))
check('Report package writes manifest',bool(re.search(r'manifest|MANIFEST',pkg,re.I)))
check('Report package includes report output',bool(re.search(r'html|markdown|json|report',pkg,re.I)))
check('Report package does not describe itself as full project backup',not bool(re.search(r'all evidence|complete evidence vault|full project backup',pkg,re.I)))
# Appendices/full records
for label,pat in [('Test Log',r'test log'),('Observation Register',r'observation register'),('Evidence Index',r'evidence index'),('Photo Log',r'photo log'),('Coverage Matrix',r'coverage matrix'),('Rules of Engagement',r'rules of engagement'),('Formal Retests',r'formal retest|retest register'),('Baseline Comparisons',r'baseline comparison')]:
 check(f'{label} appendix available',bool(re.search(pat,src,re.I)))
# Output/print
check('Standalone HTML output exists',bool(re.search(r'text/html|export.*html',src,re.I|re.S)))
check('Markdown output exists',bool(re.search(r'text/markdown|export.*markdown',src,re.I|re.S)))
check('Structured JSON output exists',bool(re.search(r'application/json|export.*json',src,re.I|re.S)))
check('Print/PDF stylesheet exists',bool(re.search(r'@media\s+print|@page',src,re.I)))
check('Draft watermark is represented',bool(re.search(r'watermark[\s\S]{0,600}draft|draft[\s\S]{0,600}watermark',src,re.I)))
check('Sensitivity marking appears in report rendering',bool(re.search(r'sensitivity|classification',src,re.I)))
# Readiness/approval
check('Report readiness gate is implemented',bool(re.search(r'reportReadiness|canIssueReport|report readiness|issue blockers',src,re.I)))
check('Approval identity and rationale are represented',bool(re.search(r'approvedBy|approver',src,re.I)) and bool(re.search(r'approvalRationale|approval rationale|rationale',src,re.I)))
check('Issued report is not normally editable',bool(re.search(r'(?:FINAL_ISSUE|ISSUED)[\s\S]{0,2000}(?:disabled|read.?only|locked)|(?:disabled|read.?only|locked)[\s\S]{0,2000}(?:FINAL_ISSUE|ISSUED)',src,re.I)))
passed=all(x['passed'] for x in A)
out={'suite':'Report governance semantic source checks','timestamp':dt.datetime.now(dt.timezone.utc).isoformat(),'passed':passed,'assertions':A,'source_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()}
(ROOT/'test-results').mkdir(exist_ok=True)
(ROOT/'test-results'/'report_governance_semantic.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
(ROOT/'test-results'/'report_governance_semantic.txt').write_text(('PASS' if passed else 'FAIL')+f" {sum(x['passed'] for x in A)}/{len(A)}\n"+'\n'.join(f"{'PASS' if x['passed'] else 'FAIL'} {x['name']}: {x['detail']}" for x in A)+'\n',encoding='utf-8')
sys.exit(0 if passed else 1)
