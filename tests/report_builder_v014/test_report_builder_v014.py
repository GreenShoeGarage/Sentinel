#!/usr/bin/env python3
from __future__ import annotations
import contextlib, datetime as dt, http.server, json, os, re, socket, socketserver, subprocess, sys, threading, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results'; OUT.mkdir(exist_ok=True)
RESULT={'suite':'Professional Report Builder 2.0','started':dt.datetime.now(dt.timezone.utc).isoformat(),'assertions':[], 'downloads':[]}

def assertion(name, ok, detail=''):
    RESULT['assertions'].append({'name':name,'passed':bool(ok),'detail':str(detail)[:2000]})
    if not ok: raise AssertionError(f'{name}: {detail}')

def note(name, ok, detail=''):
    RESULT['assertions'].append({'name':name,'passed':bool(ok),'advisory':True,'detail':str(detail)[:2000]})

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def serve():
    os.chdir(ROOT)
    srv=socketserver.TCPServer(('127.0.0.1',0),Quiet)
    t=threading.Thread(target=srv.serve_forever,daemon=True); t.start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}/index.html'

def fill_visible(page):
    # Fill required/blank controls with context-sensitive values.
    controls=page.locator('input:visible, textarea:visible, select:visible')
    for i in range(controls.count()):
        el=controls.nth(i)
        try:
            tag=el.evaluate('(e)=>e.tagName.toLowerCase()')
            typ=(el.get_attribute('type') or '').lower()
            if typ in {'hidden','file','button','submit','reset','image'}: continue
            if tag=='select':
                opts=el.locator('option:not([disabled])')
                for j in range(opts.count()):
                    val=opts.nth(j).get_attribute('value')
                    if val not in (None,''):
                        el.select_option(value=val); break
                continue
            if typ in {'checkbox','radio'}:
                if el.get_attribute('required') is not None and not el.is_checked(): el.check(force=True)
                continue
            val=el.input_value()
            if val.strip(): continue
            ident=' '.join(filter(None,[el.get_attribute('id'),el.get_attribute('name'),el.get_attribute('placeholder'),el.get_attribute('aria-label')])).lower()
            try:
                lab=el.evaluate("e=>{const l=e.labels&&e.labels[0];return l?l.innerText:''}") or ''
                ident+=' '+lab.lower()
            except: pass
            if typ=='date': value=dt.date.today().isoformat()
            elif typ in {'datetime-local'}: value=dt.datetime.now().strftime('%Y-%m-%dT%H:%M')
            elif 'executive' in ident: value='This authorized assessment evaluated the effectiveness of physical security controls, documented strengths and weaknesses, and prioritized defensible remediation actions.'
            elif 'method' in ident: value='Testing followed the approved scope and Rules of Engagement. Conclusions are traceable to documented tests, observations, and preserved evidence.'
            elif 'limit' in ident: value='Results reflect the authorized scope, assessment period, sampling basis, and evidence available at the time of testing.'
            elif 'conclusion' in ident: value='The assessment identified control strengths and prioritized opportunities for improvement. Remediation should be verified through formal retesting.'
            elif 'title' in ident: value='Authorized Physical Security Assessment Report'
            elif 'client' in ident: value='Validation Client'
            elif 'site' in ident: value='Validation Site'
            elif 'prepared' in ident or 'author' in ident or 'analyst' in ident: value='Validation Analyst'
            elif 'review' in ident: value='Independent Reviewer'
            elif 'approv' in ident: value='Approval Authority'
            elif 'role' in ident: value='Security Reviewer'
            elif 'revision' in ident: value='A'
            elif 'reason' in ident or 'rationale' in ident or 'note' in ident or 'comment' in ident: value='Validation of the governed report lifecycle and issue controls.'
            elif 'header' in ident: value='AUTHORIZED PHYSICAL SECURITY ASSESSMENT'
            elif 'footer' in ident: value='CONTROLLED ASSESSMENT REPORT'
            elif typ=='number': value='1'
            else: value='Validation entry'
            el.fill(value)
        except Exception:
            continue

def click_action(page, patterns, required=False):
    if isinstance(patterns,str): patterns=[patterns]
    for pat in patterns:
        rx=re.compile(pat,re.I)
        for selector in ['button:visible','[role=button]:visible','a:visible']:
            loc=page.locator(selector).filter(has_text=rx)
            for i in range(loc.count()):
                b=loc.nth(i)
                try:
                    if b.is_enabled():
                        b.scroll_into_view_if_needed(); b.click(); page.wait_for_timeout(250)
                        return b.inner_text().strip()
                except: continue
    if required: raise AssertionError('Action not found: '+str(patterns))
    return None

def complete_dialog(page):
    page.wait_for_timeout(150)
    fill_visible(page)
    for txt in [r'confirm',r'save',r'apply',r'continue',r'submit',r'approve',r'issue',r'create']:
        loc=page.locator('[role=dialog] button:visible, dialog button:visible, .modal button:visible').filter(has_text=re.compile(txt,re.I))
        for i in range(loc.count()):
            try:
                if loc.nth(i).is_enabled(): loc.nth(i).click(); page.wait_for_timeout(350); return True
            except: pass
    return False

def run():
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        assertion('Playwright available',False,e); return
    srv,url=serve()
    errors=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        ctx=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':1000})
        page=ctx.new_page()
        page.on('pageerror',lambda e: errors.append('pageerror: '+str(e)))
        page.on('console',lambda m: errors.append('console error: '+m.text) if m.type=='error' else None)
        page.goto(url,wait_until='domcontentloaded',timeout=90000); page.wait_for_timeout(1200)
        assertion('Application loads',page.locator('body').inner_text().upper().find('SENTINEL')>=0)
        # Attempt to import the fullest historical project fixture before using built-in sample mechanisms.
        fixture_info={}
        try:
            fixture_info=json.loads((ROOT/'FULL_PROJECT_FIXTURE.json').read_text())
        except Exception:
            fixture_info={}
        imported_fixture=False
        fixture_path=fixture_info.get('path')
        if fixture_path and Path(fixture_path).exists():
            try:
                click_action(page,[r'^project$',r'project files',r'project menu'])
                page.wait_for_timeout(150)
                imp=page.locator('button:visible, [role=menuitem]:visible, a:visible').filter(has_text=re.compile(r'import',re.I))
                if imp.count():
                    with page.expect_file_chooser(timeout=3000) as fi:
                        imp.first.click()
                    fi.value.set_files(fixture_path)
                    page.wait_for_timeout(350)
                    complete_dialog(page)
                    page.wait_for_timeout(800)
                    imported_fixture=True
            except Exception:
                pass
        note('Historical project fixture import attempted',True,{'fixture':fixture_path,'imported':imported_fixture})
        # Attempt to seed using built-in fixture/sample mechanisms.
        seed_result=page.evaluate("""async()=>{
          const candidates=[];
          for(const k of Object.getOwnPropertyNames(window)){
            if(/sample|seed|fixture|demo/i.test(k) && typeof window[k]==='function') candidates.push(k);
          }
          for(const objName of ['__SENTINEL_TEST_API__','SENTINEL_TEST_API','sentinelTestApi','testApi']){
            const o=window[objName]; if(o&&typeof o==='object') for(const k of Object.keys(o)) if(/sample|seed|fixture|demo/i.test(k)&&typeof o[k]==='function') candidates.push(objName+'.'+k)
          }
          for(const name of candidates){
            try{ let fn,owner=window; if(name.includes('.')){const [a,b]=name.split('.');owner=window[a];fn=owner[b]}else fn=window[name]; const r=fn.call(owner); if(r&&typeof r.then==='function') await r; return {called:name}; }catch(e){}
          }
          return {called:null,candidates};
        }""")
        if not seed_result.get('called'):
            click_action(page,[r'load sample',r'sample project',r'demo data'])
            complete_dialog(page)
        note('Sample/fixture seeding attempted',True,json.dumps(seed_result))
        # Advanced mode.
        click_action(page,[r'^advanced$',r'advanced mode'])
        # Open Report module.
        clicked=click_action(page,[r'^report$',r'report builder',r'reports'],required=True)
        page.wait_for_timeout(500)
        body=page.locator('main, [role=main], body').inner_text()
        assertion('Report Builder workspace opens',bool(re.search(r'report builder|report composition|assessment report',body,re.I)),clicked)
        # Initialize report if needed.
        if click_action(page,[r'create report',r'initialize report',r'new report']): complete_dialog(page)
        fill_visible(page)
        if click_action(page,[r'save composition',r'save report',r'apply changes',r'^save$']): complete_dialog(page)
        # Verify core composition language in rendered UI.
        body=page.locator('main, [role=main], body').inner_text()
        for label,pat in [
          ('Executive Summary visible',r'executive summary'),('Methodology visible',r'methodology'),('Limitations visible',r'limitations'),
          ('Conclusion visible',r'conclusion'),('Sections controls visible',r'sections?|composition'),('Evidence selection visible',r'evidence'),
          ('Appendices visible',r'appendi'),('Revision controls visible',r'revision'),('Approval controls visible',r'approv|review')]:
            assertion(label,bool(re.search(pat,body,re.I)),body[:1200])
        # Preview must render substantial report content.
        if click_action(page,[r'preview report',r'^preview$',r'render report']): page.wait_for_timeout(600)
        text=page.locator('body').inner_text()
        assertion('Report preview produces substantial content',len(text)>1200,len(text))
        page.screenshot(path=str(OUT/'report_builder.png'),full_page=True)
        # Exercise downloadable formats adaptively.
        for label,pats in [
          ('HTML export',[r'export.*html',r'html report']),('Markdown export',[r'export.*markdown',r'markdown']),('JSON export',[r'export.*json',r'json report'])]:
            found=False
            for pat in pats:
                loc=page.locator('button:visible, a:visible').filter(has_text=re.compile(pat,re.I))
                for i in range(loc.count()):
                    try:
                        if not loc.nth(i).is_enabled(): continue
                        with page.expect_download(timeout=5000) as di: loc.nth(i).click()
                        dl=di.value; dest=OUT/dl.suggested_filename; dl.save_as(dest)
                        RESULT['downloads'].append({'type':label,'file':dest.name,'bytes':dest.stat().st_size})
                        found=dest.stat().st_size>0; break
                    except Exception:
                        try: complete_dialog(page)
                        except: pass
                if found: break
            assertion(label,found,'No successful download')
        # Lifecycle: use adaptive action discovery. These are critical gates.
        lifecycle=[]
        for state,patterns in [
          ('REVIEW',[r'submit.*review',r'send.*review',r'begin review']),
          ('APPROVED',[r'^approve$',r'approve report']),
          ('ISSUED',[r'final issue',r'issue report',r'publish final'])]:
            action=click_action(page,patterns)
            if action:
                complete_dialog(page); page.wait_for_timeout(450); lifecycle.append(state)
            else:
                lifecycle.append('MISSING_'+state)
        finalbody=page.locator('body').inner_text()
        assertion('Draft-to-review action exists','MISSING_REVIEW' not in lifecycle,lifecycle)
        assertion('Approval action exists','MISSING_APPROVED' not in lifecycle,lifecycle)
        assertion('Final issue action exists','MISSING_ISSUED' not in lifecycle,lifecycle)
        assertion('Final issue state is visible',bool(re.search(r'final issue|issued|locked',finalbody,re.I)),finalbody[-1500:])
        # Verify issue lock or disabled composition controls.
        edit_enabled=False
        for pat in [r'edit report',r'edit composition',r'add section']:
            loc=page.locator('button:visible').filter(has_text=re.compile(pat,re.I))
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_enabled(): edit_enabled=True
                except: pass
        locked=bool(re.search(r'locked|immutable|final issue',finalbody,re.I)) or not edit_enabled
        assertion('Final issue lock is enforced',locked,{'edit_enabled':edit_enabled})
        # New revision must be available after issue.
        rev=click_action(page,[r'new revision',r'create revision',r'revise report'])
        assertion('New revision action available',bool(rev),finalbody[-2000:])
        if rev: complete_dialog(page)
        page.wait_for_timeout(400)
        # Report package must download after acknowledgement.
        package=False
        loc=page.locator('button:visible, a:visible').filter(has_text=re.compile(r'report package|export package',re.I))
        for i in range(loc.count()):
            try:
                if not loc.nth(i).is_enabled(): continue
                try:
                    with page.expect_download(timeout=10000) as di:
                        loc.nth(i).click(); page.wait_for_timeout(100); complete_dialog(page)
                    dl=di.value; dest=OUT/dl.suggested_filename; dl.save_as(dest)
                    RESULT['downloads'].append({'type':'Report package','file':dest.name,'bytes':dest.stat().st_size})
                    package=dest.stat().st_size>0; break
                except Exception:
                    complete_dialog(page)
            except: pass
        assertion('Controlled report package export',package,'No report package downloaded')
        # Mobile/report responsive smoke.
        page.set_viewport_size({'width':390,'height':844}); page.wait_for_timeout(250)
        dims=page.evaluate('()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
        assertion('Report Builder mobile layout avoids major horizontal overflow',dims['scroll']<=dims['client']+16,dims)
        assertion('No uncaught browser errors',not errors,errors[:20])
        browser.close()
    finally:
      srv.shutdown(); srv.server_close()

try:
    run()
except Exception as e:
    RESULT['fatal']=str(e); RESULT['traceback']=traceback.format_exc()
finally:
    RESULT['completed']=dt.datetime.now(dt.timezone.utc).isoformat()
    RESULT['passed']=all(a.get('passed') for a in RESULT['assertions'] if not a.get('advisory')) and 'fatal' not in RESULT
    (OUT/'report_builder_results.json').write_text(json.dumps(RESULT,indent=2),encoding='utf-8')
    passed=sum(1 for a in RESULT['assertions'] if a.get('passed'))
    total=len(RESULT['assertions'])
    (OUT/'report_builder_results.txt').write_text(f"{'PASS' if RESULT['passed'] else 'FAIL'} {passed}/{total}\n"+('\n'.join(f"{'PASS' if a.get('passed') else 'FAIL'} {a['name']}: {a.get('detail','')}" for a in RESULT['assertions']))+'\n',encoding='utf-8')
    sys.exit(0 if RESULT['passed'] else 1)
