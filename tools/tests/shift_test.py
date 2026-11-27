from playwright.sync_api import sync_playwright
import os
SITE=os.environ.get('TEST_SITE','/tmp/site-test')
BASE='file://'+SITE+'/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files'],ignore_default_args=['--hide-scrollbars'])
    for url in ['index.html','ru/index.html','cases/sales-crm.html','ru/cases/design-system.html']:
        for vw in (1440,1024,390):
            pg=b.new_page(viewport={'width':vw,'height':800})
            pg.goto(BASE+url); pg.wait_for_timeout(300)
            sel='.header .btn' if 'cases/' in url else '.hero .btn'
            if vw<=480 and 'cases/' not in url: sel='.hero .btn'
            q='''()=>{const g=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.left*10)/10,Math.round(r.width*10)/10]};
              return {sb:window.innerWidth-document.documentElement.clientWidth,brand:g('.brand'),title:g('.hero__title')||g('.case-title'),footer:g('.footer__in'),flag:g('.flag')}}'''
            before=pg.evaluate(q)
            pg.click(sel); pg.wait_for_timeout(300)
            after=pg.evaluate(q)
            same= before['brand']==after['brand'] and before['title']==after['title'] and before['footer']==after['footer'] and before['flag']==after['flag']
            print('OK ' if same else 'SHIFT',url,vw,'scrollbar',before['sb'],'->',after['sb'],'' if same else (before,after))
            pg.close()
    b.close()
