from playwright.sync_api import sync_playwright
import os
SITE=os.environ.get('TEST_SITE','/tmp/site-test')
BASE='file://'+SITE+'/'
res=[]
def ok(name,cond,extra=''): res.append((name,bool(cond),extra)); print(('PASS' if cond else 'FAIL'),name,extra)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files'])
    for url,lang in [('index.html','en'),('cases/sales-crm.html','en'),('ru/index.html','ru'),('ru/cases/financial-dashboard.html','ru')]:
        pg=b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror',lambda e,errs=errs:errs.append(str(e)))
        pg.goto(BASE+url); pg.wait_for_timeout(300)
        ok(f'{url}: html lang={lang}', pg.evaluate('document.documentElement.lang')==lang)
        # modal via header button
        pg.click('.header .btn' if 'cases/' in url else '.hero .btn'); pg.wait_for_timeout(250)
        st=pg.evaluate('''()=>{const d=document.getElementById("contact-modal");const r=d.getBoundingClientRect();return {open:d.open,w:Math.round(r.width),cx:Math.round(r.left+r.width/2),cy:Math.round(r.top+r.height/2),vw:innerWidth,vh:innerHeight,h:Math.round(r.height),title:d.querySelector(".modal__title").textContent,cta:d.querySelector(".modal__cta").textContent,href:d.querySelector(".modal__cta").href,locked:document.body.classList.contains("is-modal")}}''')
        ok(f'{url}: modal opens 352 wide, centered', st['open'] and st['w']==352 and abs(st['cx']-720)<=1 and abs(st['cy']-450)<=1, str(st))
        ok(f'{url}: calendly link', st['href']=='https://calendly.com/lifespacezero/30min')
        if url in('index.html','ru/index.html'): pg.screenshot(path=f'/tmp/modal_{lang}_{url.split("/")[-1][:5]}.png')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        ok(f'{url}: Esc closes', not pg.evaluate('document.getElementById("contact-modal").open'))
        pg.click('.header .btn' if 'cases/' in url else '.hero .btn'); pg.wait_for_timeout(150); pg.mouse.click(20,20); pg.wait_for_timeout(100)
        ok(f'{url}: backdrop click closes', not pg.evaluate('document.getElementById("contact-modal").open'))
        pg.click('.header .btn' if 'cases/' in url else '.hero .btn'); pg.wait_for_timeout(150); pg.click('.modal__close'); pg.wait_for_timeout(100)
        ok(f'{url}: X closes + scroll unlocked', not pg.evaluate('document.getElementById("contact-modal").open') and not pg.evaluate('document.body.classList.contains("is-modal")'))
        # click inside modal does not close
        pg.click('.header .btn' if 'cases/' in url else '.hero .btn'); pg.wait_for_timeout(150); pg.click('.modal__title'); pg.wait_for_timeout(100)
        ok(f'{url}: click inside keeps open', pg.evaluate('document.getElementById("contact-modal").open')); pg.keyboard.press('Escape')
        if url.endswith('index.html') and url in('index.html','ru/index.html'):
            pg.click('.hero .btn'); pg.wait_for_timeout(150)
            ok(f'{url}: hero button opens modal', pg.evaluate('document.getElementById("contact-modal").open')); pg.keyboard.press('Escape')
        # language menu
        pg.click('.flag'); pg.wait_for_timeout(100)
        vis=pg.evaluate('!document.getElementById("langpop").hidden')
        ok(f'{url}: flag opens menu', vis)
        pg.screenshot(path=f'/tmp/langmenu_{lang}.png',clip={'x':1140,'y':0,'width':300,'height':160}) if url=='index.html' else None
        target='ru' if lang=='en' else 'en'
        pg.click(f'#langpop a[hreflang={target}]'); pg.wait_for_load_state(); pg.wait_for_timeout(300)
        ok(f'{url}: switch -> {target}', pg.evaluate('document.documentElement.lang')==target, pg.url.replace(BASE,''))
        # same page in other language
        exp=url.replace('ru/','') if lang=='ru' else ('ru/'+url)
        ok(f'{url}: lands on counterpart', pg.url.endswith(exp), exp)
        # footer link back
        pg.click(f'.lang a[hreflang={lang}]'); pg.wait_for_load_state(); pg.wait_for_timeout(200)
        ok(f'{url}: footer link back', pg.url.endswith(url) , pg.url.replace(BASE,''))
        ok(f'{url}: no js errors', not errs, str(errs))
        pg.close()
    b.close()
print('FAILED:',[r[0] for r in res if not r[1]])
