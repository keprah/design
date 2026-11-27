from playwright.sync_api import sync_playwright
import os
SITE=os.environ.get('TEST_SITE','/tmp/site-test')
import itertools
EN=['index','cases/sales-crm','cases/financial-dashboard','cases/design-system']
PAGES=[(SITE+'/'+u+'.html','en') for u in EN]+[(SITE+'/ru/'+u+'.html','ru') for u in EN]
WIDTHS=[1920,1440,1280,1100,1024,960,900,768,600,480,390,360,320]
issues=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files'])
    for path,lang in PAGES:
        for w in WIDTHS:
            pg=b.new_page(viewport={'width':w,'height':900}); errs=[]
            pg.on('pageerror',lambda e,errs=errs:errs.append(str(e))); pg.on('console',lambda m,errs=errs: errs.append(m.text) if m.type=='error' and 'ERR_' not in m.text and '403' not in m.text else None)
            pg.goto('file://'+path); pg.wait_for_timeout(200)
            r=pg.evaluate('''()=>{const de=document.documentElement,vw=de.clientWidth,bad=[];
              document.querySelectorAll('main *, header *, footer *').forEach(e=>{ if(e.closest('.slider__track')||e.closest('.case-nav ul')||e.closest('.langpop'))return; const r=e.getBoundingClientRect(); if(r.width>0&&(r.right>vw+1||r.left<-1)) bad.push(e.tagName+'.'+(e.className.baseVal===undefined?e.className:'')+':'+Math.round(r.left)+'→'+Math.round(r.right));});
              return {over:de.scrollWidth-vw,bad:bad.slice(0,3),h1:document.querySelectorAll('h1').length}}''')
            # modal opened
            pg.click('.header .btn' if 'cases/' in path else '.hero .btn'); pg.wait_for_timeout(200)
            m=pg.evaluate('''()=>{const d=document.getElementById("contact-modal"),r=d.getBoundingClientRect();return {l:Math.round(r.left),r:Math.round(r.right),vw:innerWidth,sw:d.scrollWidth,cw:d.clientWidth,t:Math.round(r.top),b:Math.round(r.bottom),vh:innerHeight}}''')
            mod_bad = m['l']<0 or m['r']>m['vw'] or m['sw']>m['cw'] or m['t']<0 or m['b']>m['vh']
            if r['over']>0 or r['bad'] or r['h1']!=1 or errs or mod_bad: issues.append((path.split('cases-test/')[1],w,r,m if mod_bad else '',errs[:2]))
            pg.close()
    b.close()
print('pages',len(PAGES),'widths',len(WIDTHS),'issues',len(issues))
for i in issues[:20]: print(i)
