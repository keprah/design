#!/usr/bin/env python3
"""Генератор сайта (EN + RU): главная и страницы кейсов  ->  корень репозитория

   python3 tools/build.py      — собрать всё:  index.html, cases/*.html,  ru/index.html, ru/cases/*.html
   python3 build.py replica    — cases/_replica.html: шаблон Case_1440.png со своим наполнением (сверка с PNG)
   python3 build.py modal      — cases/_modal.html: модалка из Frame_1321316017.png (сверка с PNG)

Контент кейсов: cases_en.json / cases_ru.json (данные старого портфолио).
"""
import json, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)   # корень репозитория (tools/ лежит внутри него)
DATA = {
    "en": json.load(open(os.path.join(HERE, "cases_en.json"), encoding="utf-8")),
    "ru": json.load(open(os.path.join(HERE, "cases_ru.json"), encoding="utf-8")),
}
REMOTE = "https://keprah.github.io/portfolio/assets/img/"
EMAIL = "lifespacezero@gmail.com"
TELEGRAM = "https://t.me/ilya_nwy"
LINKEDIN = "https://www.linkedin.com/in/ilya-andreev-232864255"
CALENDLY = "https://calendly.com/lifespacezero/30min"

# размеры картинок на старом портфолио (ширина, высота)
DIM = {
    "crm_pc": (1500, 723), "crm_phone": (1500, 723), "crm_flow": (1500, 723), "crm_meet": (1408, 874),
    "fin_main": (1500, 877), "fin_sales": (1500, 877), "fin_plan": (1500, 877), "fin_anim": (1000, 562),
    "fin_proto": (1500, 895), "fin_wire": (1500, 382), "fin_layout": (1500, 723), "ds_vars": (1500, 828),
}

ORDER = ["crm", "dashboard", "design-system"]          # в портфолио только эти три кейса (те же, что на главной)
SLUG = {"crm": "sales-crm", "dashboard": "financial-dashboard", "design-system": "design-system"}
HOME_CARDS = ["crm", "dashboard", "design-system"]

# ---------------------------------------------------------------------------------------------
#  Тексты интерфейса
# ---------------------------------------------------------------------------------------------
T = {
    "en": dict(
        lang="en", name="Ilya Andreev", initials="IA", brand_aria="Ilya Andreev — home",
        touch="Get in touch", flag_label="Language: English",
        title_home="Ilya Andreev — Product Designer",
        desc_home="Product Designer specializing in enterprise systems (B2B/B2E): CRM, dashboards, admin panels and back-office services.",
        title_suffix="Ilya Andreev",
        status="Open to offers", hero_title="Product Designer",
        hero_sub='Enterprise systems (B2B/B2E):<br>CRM, dashboards, admin panels, and <span class="nw">back-office</span> services.',
        cases_aria="Selected cases",
        story_aria="Recommendation", story_name="Roman Runzhin", story_role="CDTO at Keep Calm",
        story_quote='You can count on Ilya. He has a deep understanding<br class="br-d"> of the tasks at hand, works independently, and<br class="br-d"> consistently delivers high-quality results.',
        work_h="Work experience",
        work_sub='<span class="hl">Over 5 years</span> I translate vague business requirements into clear UX scenarios<br class="br-d"> and functional interface solutions',
        cv="Download CV (pdf)",
        jobs=[("Product / DS Designer", "2024–2026", "Keep Calm Agency",
               "Designed marketplaces, CRMs and dashboards for real estate, restaurants and construction,<br class=\"br-d\"> and led the design system in Figma."),
              ("Product Designer", "2023–2024", "Serenity Studio",
               "Designed websites and online stores for clients:<br class=\"br-d\"> information architecture and<br class=\"br-d\"> interactive prototypes."),
              ("Product Designer", "2022–2024", "Schneider Consult",
               "Improved the UX of a retail company's<br class=\"br-d\"> e-commerce: found conversion barriers<br class=\"br-d\"> and evolved the client's design system."),
              ("UX/UI Designer", "2021–2022", "Mage Studio",
               "Designed websites and online stores<br class=\"br-d\"> for the studio's clients: from structure<br class=\"br-d\"> and prototypes to responsive layouts.")],
        remote="Remote",
        about_h="About me", loc="Tbilisi, Georgia",
        about_text='My name is Ilya. I\'m a product designer specializing in enterprise systems (B2E/B2B)<br class="br-d"> and focused on UX design for complex interfaces with large amounts of data,<br class="br-d"> filters, forms, and role-based models—interfaces that help employees<br class="br-d"> work faster and make fewer mistakes.',
        contacts="Contacts", book="Book a call", close="Close",
        more="Other cases", type="Type", website="Website", nda="Confidentiality",
        before="Before", after="After", nav_aria="Case sections", prev="Previous slide", next="Next slide", slide="Slide",
        lang_en="English", lang_ru="Русский",
    ),
    "ru": dict(
        lang="ru", name="Илья Андреев", initials="IA", brand_aria="Илья Андреев — на главную",
        touch="Связаться", flag_label="Язык: русский",
        title_home="Илья Андреев — продуктовый дизайнер",
        desc_home="Продуктовый дизайнер, специализируюсь на корпоративных системах (B2B/B2E): CRM, дашборды, админ-панели и бэк-офисные сервисы.",
        title_suffix="Илья Андреев",
        status="Открыт к предложениям", hero_title="Product Designer",
        hero_sub='Корпоративные системы (B2B/B2E):<br>CRM, дашборды, админ-панели и <span class="nw">бэк-<br class="br-m">офисные</span> сервисы.',
        cases_aria="Избранные кейсы",
        story_aria="Рекомендация", story_name="Роман Рунжин", story_role="CDTO в Keep Calm",
        story_quote='На Илью можно положиться.<br class="br-m"> Он глубоко<br class="br-t"> разбирается<br class="br-d"> в задачах,<br class="br-m"> работает<br class="br-t"> самостоятельно<br class="br-m"> и стабильно выдаёт<br class="br-d br-t"> качественный<br class="br-m"> результат.',
        work_h="Опыт работы",
        work_sub='<span class="hl">Более 5 лет</span> перевожу расплывчатые<br class="br-m"> бизнес-требования<br class="br-t"> в понятные<br class="br-d br-m"> UX-сценарии и работающие<br class="br-t br-m"> интерфейсные решения',
        cv="Скачать резюме (pdf)",
        jobs=[("Product / DS Designer", "2024–2026", "Keep Calm Agency",
               "Проектировал маркетплейсы, CRM,<br class=\"br-m\"> дашборды<br class=\"br-d br-t\"> для недвижимости,<br class=\"br-m\"> ресторанов и<br class=\"br-d br-t\"> строительства, вёл<br class=\"br-m\"> дизайн-систему на Figma."),
              ("Product Designer", "2023–2024", "Serenity Studio",
               "Проектировал веб-сайты и интернет-<br class=\"br-d br-t br-m\">магазины для заказчиков:<br class=\"br-m\"> информационная<br class=\"br-d br-t\"> архитектура,<br class=\"br-m\"> интерактивные прототипы."),
              ("Product Designer", "2022–2024", "Schneider Consult",
               "Улучшал UX e-commerce розничной<br class=\"br-m\"> компании:<br class=\"br-d br-t\"> искал барьеры конверсии<br class=\"br-m\"> и развивал дизайн-<br class=\"br-d br-t\">систему клиента."),
              ("UX/UI Designer", "2021–2022", "Mage Studio",
               "Проектировал сайты и интернет-<br class=\"br-m\">магазины<br class=\"br-d br-t\"> для клиентов студии: от<br class=\"br-m\"> структуры<br class=\"br-d br-t br-m\"> и прототипов до адаптивных макетов.")],
        remote="Удаленно",
        about_h="Обо мне", loc="Тбилиси, Грузия",
        about_text='Меня зовут Илья. Я продуктовый<br class="br-m"> дизайнер, специализируюсь<br class="br-t"> на<br class="br-m"> корпоративных<br class="br-d"> системах (B2E/B2B)<br class="br-m"> и занимаюсь UX-<br class="br-t">дизайном сложных<br class="br-m"> интерфейсов с большим объёмом<br class="br-d br-m"> данных,<br class="br-t"> фильтрами, формами<br class="br-m"> и ролевыми моделями — интерфейсов,<br class="br-t br-m"> которые помогают<br class="br-d"> сотрудникам<br class="br-m"> работать быстрее и<br class="br-t"> ошибаться реже.',
        contacts="Контакты", book="Записаться на звонок", close="Закрыть",
        more="Другие кейсы", type="Тип", website="Сайт", nda="Ограничения публикации",
        before="Было", after="Стало", nav_aria="Разделы кейса", prev="Предыдущий слайд", next="Следующий слайд", slide="Слайд",
        lang_en="English", lang_ru="Русский",
    ),
}

# короткие названия (как на карточках), текст карточки и alt обложки
CASE_TXT = {
    "en": {
        "crm": ("Sales CRM", "Internal sales tool from lead intake to offers and financial calculations.", "Sales CRM screens"),
        "dashboard": ("Financial dashboard", "Financial monitoring tool, unifying plan vs. actual data, periods and versions.", "Financial dashboard"),
        "design-system": ("Design system", "Migrated SaaS delivery storefronts to components and variables.", "Design system variables and components"),
    },
    "ru": {
        "crm": ("CRM для отдела продаж", "Внутренний сервис отдела продаж: от первого обращения до офферов и финансовых расчётов.", "Экраны CRM для отдела продаж"),
        "dashboard": ("Финансовый дашборд", "Сервис финансового мониторинга: план и факт, периоды и версии данных в одном интерфейсе.", "Финансовый дашборд"),
        "design-system": ("Дизайн-система", "Перевод клиентских витрин SaaS-платформы доставки на компоненты и переменные.", "Переменные и компоненты дизайн-системы"),
    },
}

esc = html.escape
TR = dict(zip("абвгдежзийклмнопрстуфхцчшщъыьэюя", ["a", "b", "v", "g", "d", "e", "zh", "z", "i", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]))


def slugify(s):
    s = "".join(TR.get(ch, ch) for ch in s.lower().replace("ё", "е"))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


# ---------------------------------------------------------------------------------------------
#  Пути между языками
# ---------------------------------------------------------------------------------------------
def pre(lang, kind):
    """префикс до корня сайта: кейс/главная × en/ru"""
    return "../" * ((lang == "ru") + (kind == "case"))


def page_url(lang, kind, slug=None, *, from_lang, from_kind):
    """относительный URL страницы (lang, kind, slug) из страницы (from_lang, from_kind)"""
    p = pre(from_lang, from_kind)
    path = ("ru/" if lang == "ru" else "") + ("index.html" if kind == "home" else f"cases/{slug}.html")
    return p + path


def alt_urls(lang, kind, slug):
    return (page_url("en", kind, slug, from_lang=lang, from_kind=kind),
            page_url("ru", kind, slug, from_lang=lang, from_kind=kind))


# ---------------------------------------------------------------------------------------------
#  Картинки, фигуры, слайдеры
# ---------------------------------------------------------------------------------------------
def img_tag(key, alt, p, *, eager=False):
    w, h = DIM[key]
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="{p}assets/cases/{key}.webp" data-remote="{REMOTE}{key}.webp" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" {load}>')


def ratio(keys):
    """aspect-ratio рамки: у самой «высокой» картинки группы, чтобы остальные не обрезались"""
    k = min(keys, key=lambda k: DIM[k][0] / DIM[k][1])
    return f"{DIM[k][0]}/{DIM[k][1]}"


CHEV_L = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15.5 5 8.5 12l7 7"/></svg>'
CHEV_R = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8.5 5l7 7-7 7"/></svg>'
MAIL_SVG = '<svg width="20" height="16" viewBox="0 0 20 16" aria-hidden="true"><path fill="currentColor" d="M2 0h16a2 2 0 012 2v.5l-10 6.4L0 2.5V2a2 2 0 012-2zM0 5l9.5 6a1 1 0 001 0L20 5v9a2 2 0 01-2 2H2a2 2 0 01-2-2z"/></svg>'
PIN_SVG = '<svg width="16" height="20" viewBox="0 0 16 20" aria-hidden="true"><path transform="translate(1 0) scale(.875 1)" fill="currentColor" d="M8 0C3.6 0 0 3.5 0 7.9c0 5.4 6.4 11.4 7.2 12 .5.4 1.1.4 1.6 0C9.6 19.3 16 13.3 16 7.9 16 3.5 12.4 0 8 0zm0 11a3.1 3.1 0 110-6.2A3.1 3.1 0 018 11z"/></svg>'
X_SVG = '<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M.75.75l12.5 12.5M13.25.75L.75 13.25"/></svg>'


def figure_html(fig, p):
    k, c = fig["k"], fig["c"]
    return (f'<figure class="fig" style="--ar:{ratio([k])}">'
            f'<div class="fig__frame">{img_tag(k, c, p)}</div><figcaption>{esc(c)}</figcaption></figure>')


def slider_html(figs, label, p, L):
    keys = [f["k"] for f in figs]
    slides = "".join(
        f'<figure class="slide"><div class="slide__frame">{img_tag(f["k"], f["c"], p)}</div><figcaption>{esc(f["c"])}</figcaption></figure>'
        for f in figs)
    bars = "".join(f'<button type="button" aria-label="{L["slide"]} {i + 1}" aria-current="{"true" if i == 0 else "false"}"></button>'
                   for i in range(len(figs)))
    return (f'<div class="slider" data-slider style="--ar:{ratio(keys)}" role="group" aria-roledescription="carousel" aria-label="{esc(label)}">'
            f'<div class="slider__track" tabindex="0">{slides}</div>'
            f'<div class="slider__ctrl"><div class="slider__bars">{bars}</div>'
            f'<div class="slider__arrows"><button class="arrow" type="button" data-prev aria-label="{L["prev"]}">{CHEV_L}</button>'
            f'<button class="arrow" type="button" data-next aria-label="{L["next"]}">{CHEV_R}</button></div></div></div>')


def ul_html(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def block_html(blocks, label, p, L):
    """блоки секции -> html (подряд идущие fig превращаются в слайдер)"""
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b["t"] == "fig":
            j = i
            while j < len(blocks) and blocks[j]["t"] == "fig":
                j += 1
            figs = blocks[i:j]
            out.append(figure_html(figs[0], p) if len(figs) == 1 else slider_html(figs, label, p, L))
            i = j
            continue
        if b["t"] == "p":
            out.append(f"<p>{esc(b['v'])}</p>")
        elif b["t"] == "ul":
            out.append(ul_html(b["v"]))
        elif b["t"] == "ba":
            out.append(f'<div class="ba"><div><h3>{L["before"]}</h3>' + ul_html(b["was"]) +
                       f'</div><div><h3>{L["after"]}</h3>' + ul_html(b["now"]) + "</div></div>")
        i += 1
    return "".join(out)


def sections_html(blocks, p, L):
    secs, cur = [], None
    for b in blocks:
        if b["t"] == "h":
            cur = {"h": b["v"], "blocks": []}
            secs.append(cur)
        elif cur is not None:
            cur["blocks"].append(b)
    used, out, nav = set(), [], []
    for s in secs:
        sid = base = slugify(s["h"])
        n = 2
        while sid in used:
            sid = f"{base}-{n}"; n += 1
        used.add(sid)
        nav.append((sid, s["h"]))
        out.append(f'<section class="sec" id="{sid}"><h2 class="sec__h">{esc(s["h"])}</h2>'
                   f'{block_html(s["blocks"], s["h"], p, L)}</section>')
    return "".join(out), nav


# ---------------------------------------------------------------------------------------------
#  Общие куски страницы
# ---------------------------------------------------------------------------------------------
def head_html(L, kind, title, desc, p):
    ru = L["lang"] == "ru"
    preload = "".join(f'<link rel="preload" href="{p}fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>\n'
                      for f in (["geist-cyrillic-400-normal", "geist-latin-400-normal", "geist-cyrillic-500-normal", "geist-latin-500-normal",
                                 "playfair-display-cyrillic-400-normal", "playfair-display-latin-400-normal"] if ru else
                                ["geist-latin-400-normal", "geist-latin-500-normal", "playfair-display-latin-400-normal"]))
    case_css = f'<link rel="stylesheet" href="{p}case.css">\n' if kind == "case" else ""
    case_js = f'<script src="{p}case.js"></script>\n' if kind == "case" else ""
    return f"""<!DOCTYPE html>
<html lang="{L["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{preload}<link rel="stylesheet" href="{p}styles.css">
{case_css}<script src="{p}site.js"></script>
{case_js}</head>
<body{' class="case-page"' if kind == "case" else ""}>
"""


def header_html(L, kind, slug, p):
    lang = L["lang"]
    en_url, ru_url = alt_urls(lang, kind, slug)
    home = "#top" if kind == "home" else p + ("ru/index.html" if lang == "ru" else "index.html")
    # главная в языке страницы: из case-страницы это ../index.html (в том же языковом каталоге)
    if kind == "case":
        home = "../index.html"
    cur_en = ' aria-current="true"' if lang == "en" else ""
    cur_ru = ' aria-current="true"' if lang == "ru" else ""
    flag = "gb" if lang == "en" else "ru"
    return f"""
<header class="header">
  <div class="header__in">
    <a class="brand" href="{home}" aria-label="{esc(L["brand_aria"])}">
      <span class="avatar" aria-hidden="true">{L["initials"]}<i class="avatar__dot"></i></span>
      <span class="brand__name">{esc(L["name"])}</span>
    </a>
    <div class="header__actions">
      {'' if kind == "home" else f'<a class="btn" href="#contacts" data-contact>{esc(L["touch"])}</a>'}
      <div class="langmenu">
        <button class="flag" type="button" aria-label="{esc(L["flag_label"])}" aria-haspopup="true" aria-expanded="false" aria-controls="langpop"><img src="{p}assets/flag-{flag}.png" width="20" height="20" alt=""></button>
        <div class="langpop" id="langpop" hidden>
          <a href="{en_url}" lang="en" hreflang="en"{cur_en}><img src="{p}assets/flag-gb.png" width="20" height="20" alt="">English</a>
          <a href="{ru_url}" lang="ru" hreflang="ru"{cur_ru}><img src="{p}assets/flag-ru.png" width="20" height="20" alt="">Русский</a>
        </div>
      </div>
    </div>
  </div>
</header>
"""


def chips_html(p):
    return (f'<a class="chip" href="{TELEGRAM}" target="_blank" rel="noopener"><img src="{p}assets/icon-telegram.png" width="24" height="24" alt="">Telegram</a>\n'
            f'      <a class="chip" href="{LINKEDIN}" target="_blank" rel="noopener"><img src="{p}assets/icon-linkedin.png" width="24" height="24" alt="">LinkedIn</a>')


def about_html(L, p):
    return f"""
  <!-- ============ About me ============ -->
  <section class="about" id="contacts">
    <h2 class="h2">{esc(L["about_h"])}</h2>
    <p class="about__loc">
      {PIN_SVG}
      {esc(L["loc"])}
    </p>
    <p class="about__text">{L["about_text"]}</p>

    <h3 class="about__h3">{esc(L["contacts"])}</h3>
    <a class="mail" href="mailto:{EMAIL}">
      {MAIL_SVG}
      {EMAIL}
    </a>
    <div class="links">
      {chips_html(p)}
    </div>
  </section>
"""


def modal_html(L, p):
    return f"""
<dialog class="modal" id="contact-modal" aria-labelledby="contact-title">
  <button class="modal__close" type="button" data-modal-close aria-label="{esc(L["close"])}">{X_SVG}</button>
  <h2 class="modal__title" id="contact-title">{esc(L["contacts"])}</h2>
  <a class="mail" href="mailto:{EMAIL}">{MAIL_SVG}{EMAIL}</a>
  <div class="links">
    {chips_html(p)}
  </div>
  <a class="modal__cta" href="{CALENDLY}" target="_blank" rel="noopener">{esc(L["book"])}</a>
</dialog>
"""


def footer_html(L, kind, slug):
    lang = L["lang"]
    en_url, ru_url = alt_urls(lang, kind, slug)
    cur_en = ' aria-current="true"' if lang == "en" else ""
    cur_ru = ' aria-current="true"' if lang == "ru" else ""
    return f"""
<footer class="footer">
  <div class="footer__in">
    <span>© 2026</span>
    <span class="lang"><a href="{en_url}" lang="en" hreflang="en"{cur_en}>EN</a> / <a href="{ru_url}" lang="ru" hreflang="ru"{cur_ru}>RU</a></span>
  </div>
</footer>
"""


def tail_html(L, kind, slug, p):
    return about_html(L, p) + "\n</main>\n" + footer_html(L, kind, slug) + modal_html(L, p) + "\n</body>\n</html>\n"


# ---------------------------------------------------------------------------------------------
#  Карточки кейсов (главная и «Другие кейсы»): обложка = заглавная картинка страницы кейса
# ---------------------------------------------------------------------------------------------
# ручные переносы в текстах карточек главной: ≥1232 (Home_1440) · 600–959 (Home_768) · 385–480 (Home_390)
CARD_BR = {
    "ru": {"crm": 'Внутренний сервис отдела продаж:<br class="br-w br-m"> от первого обращения<br class="br-t"> до офферов<br class="br-w br-m"> и финансовых расчётов.',
           "dashboard": 'Сервис финансового мониторинга:<br class="br-w br-m"> план и факт, периоды<br class="br-t"> и версии<br class="br-m"> данных<br class="br-w"> в одном интерфейсе.',
           "design-system": 'Перевод клиентских витрин SaaS-<br class="br-m">платформы<br class="br-w"> доставки<br class="br-t"> на компоненты<br class="br-m"> и переменные.'},
}


def card_html(cid, L, p, href, home=False):
    lang = L["lang"]
    c = next(c for c in DATA[lang] if c["id"] == cid)
    h1, text, alt = CASE_TXT[lang][cid]
    k = c["thumb"]
    w, h = DIM[k]
    text_html = (CARD_BR.get(lang, {}).get(cid) if home else None) or esc(text)
    im = (f'<img src="{p}assets/cases/{k}.webp" data-remote="{REMOTE}{k}.webp" width="{w}" height="{h}" '
          f'alt="{esc(alt)}" loading="lazy" decoding="async">')
    return (f'<li><a class="card" href="{href}"><span class="card__media">{im}</span>'
            f'<span class="card__body"><span class="card__title">{esc(h1)}</span>'
            f'<span class="card__text">{text_html}</span></span></a></li>')


def more_html(cid, L, p):
    i = ORDER.index(cid)
    others = [ORDER[(i + 1) % len(ORDER)], ORDER[(i + 2) % len(ORDER)]]
    return (f'<section class="more" aria-label="{esc(L["more"])}"><h2 class="h2">{esc(L["more"])}</h2>'
            '<ul class="more__grid">' + "".join(card_html(o, L, p, f"{SLUG[o]}.html") for o in others) + "</ul></section>")


def facts_html(c, L):
    rows = [(L["type"], " · ".join(c["kind"]))] + [(k, v) for k, v in c["meta"]]
    out = ['<dl class="facts">']
    for k, v in rows:
        out.append(f'<div class="facts__row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>')
    if c.get("link"):
        l = c["link"]
        out.append(f'<div class="facts__row"><dt>{L["website"]}</dt><dd><a href="{esc(l["href"])}" target="_blank" rel="noopener">{esc(l["label"])} ↗</a></dd></div>')
    out.append("</dl>")
    if c.get("nda"):
        out.append(f'<p class="note"><strong>{L["nda"]}</strong>{esc(c["nda"])}</p>')
    return "".join(out)


# ---------------------------------------------------------------------------------------------
#  Страница кейса
# ---------------------------------------------------------------------------------------------
def build_case(cid, lang):
    L = T[lang]
    c = next(c for c in DATA[lang] if c["id"] == cid)
    slug = SLUG[cid]
    p = pre(lang, "case")
    h1 = CASE_TXT[lang][cid][0]
    thumb = c["thumb"]
    blocks = list(c["blocks"])
    hero_cap = ""
    for i, b in enumerate(blocks):                      # обложка = thumb; её подпись остаётся под hero
        if b["t"] == "fig" and b["k"] == thumb:
            hero_cap = b["c"]
            del blocks[i]
            break
    secs, nav = sections_html(blocks, p, L)
    page = head_html(L, "case", f'{c["title"]} · {L["title_suffix"]}', c["lead"], p)
    page += header_html(L, "case", slug, p)
    page += f"""
<main id="top">

  <header class="case-head">
    <h1 class="case-title">{esc(h1)}</h1>
    <p class="case-lead">{esc(c["lead"])}</p>
  </header>

  <figure class="case-hero" style="--ar:{ratio([thumb])}">
    <div class="case-hero__frame">{img_tag(thumb, hero_cap or h1, p, eager=True)}</div>
    {f'<figcaption>{esc(hero_cap)}</figcaption>' if hero_cap else ''}
  </figure>

  <div class="case-body">
    <nav class="case-nav" aria-label="{esc(L["nav_aria"])}"><ul>{''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in nav)}</ul></nav>
    <div class="case-content">
      {facts_html(c, L)}
      {secs}
    </div>
  </div>

  {more_html(cid, L, p)}
"""
    page += tail_html(L, "case", slug, p)
    out = os.path.join(ROOT, "ru" if lang == "ru" else "", "cases")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, slug + ".html"), "w", encoding="utf-8").write(page)
    return len(nav), page.count('class="slider"')


# ---------------------------------------------------------------------------------------------
#  Главная
# ---------------------------------------------------------------------------------------------
def build_home(lang):
    L = T[lang]
    p = pre(lang, "home")
    cards = "\n".join(card_html(cid, L, p, f"cases/{SLUG[cid]}.html", home=True) for cid in HOME_CARDS)
    jobs = "".join(f"""
      <li class="job">
        <span class="job__dot" aria-hidden="true"></span>
        <div class="job__body">
          <h3 class="job__role">{esc(role)}</h3>
          <p class="job__meta"><span>{years}</span><i aria-hidden="true">•</i><span>{esc(co)}</span><i aria-hidden="true">•</i><span>{esc(L["remote"])}</span></p>
          <p class="job__text">{txt}</p>
        </div>
      </li>""" for role, years, co, txt in L["jobs"])
    page = head_html(L, "home", L["title_home"], L["desc_home"], p)
    page += header_html(L, "home", None, p)
    page += f"""
<main id="top">

  <!-- ============ Hero ============ -->
  <section class="hero">
    <p class="status"><i class="status__dot" aria-hidden="true"></i>{esc(L["status"])}</p>
    <h1 class="hero__title">{esc(L["hero_title"])}</h1>
    <p class="hero__sub">{L["hero_sub"]}</p>
    <a class="btn btn--lg" href="#contacts" data-contact>{esc(L["touch"])}</a>
  </section>

  <!-- ============ Cases ============ -->
  <section class="cases" aria-label="{esc(L["cases_aria"])}">
    <ul class="cases__grid">
{cards}
    </ul>
  </section>

  <!-- ============ Story / recommendation ============ -->
  <section class="story" aria-label="{esc(L["story_aria"])}">
    <img class="story__avatar" src="{p}assets/avatar-roman-runzhin.webp" width="120" height="120" alt="{esc(L["story_name"])}" loading="lazy">
    <p class="story__name">{esc(L["story_name"])}</p>
    <p class="story__role">{esc(L["story_role"])}</p>
    <blockquote class="story__quote">
      <p>{L["story_quote"]}</p>
    </blockquote>
    <div class="dots" aria-hidden="true"><i></i><i></i><i class="is-active"></i><i></i><i></i><i></i></div>
  </section>

  <!-- ============ Work experience ============ -->
  <section class="work" id="experience">
    <h2 class="h2">{esc(L["work_h"])}</h2>
    <p class="work__sub">{L["work_sub"]}</p>
    <a class="cv" href="#" download>
      <img src="{p}assets/icon-doc.png" width="17" height="24" alt="">
      {esc(L["cv"])}
    </a>

    <ol class="timeline">{jobs}
    </ol>
  </section>
"""
    page += tail_html(L, "home", None, p)
    out = os.path.join(ROOT, "ru" if lang == "ru" else "")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)


# ---------------------------------------------------------------------------------------------
#  Сверка с макетами
# ---------------------------------------------------------------------------------------------
PX = "data:image/gif;base64,R0lGODlhAQABAIAAAMzMzAAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=="


def build_replica():
    """Шаблон Case_1440.png с его плейсхолдерами — для калибровки отступов."""
    L = T["en"]
    p = "../"
    crm = next(c for c in DATA["en"] if c["id"] == "crm")
    p1, p2 = crm["blocks"][4]["v"], crm["blocks"][5]["v"]

    def sec(sid, ps):
        return f'<section class="sec" id="{sid}"><h2 class="sec__h">Context</h2><p>{esc(ps[0])}</p><p>{esc(ps[1])}</p></section>'

    def slide(cap):
        return (f'<figure class="slide"><div class="slide__frame"><img src="{PX}" width="1080" height="807" alt=""></div>'
                f'<figcaption>{cap}</figcaption></figure>')
    cap = "CDTO at Keep Calm"
    slider = ('<div class="slider" data-slider style="--ar:3/2"><div class="slider__track" tabindex="0">' +
              slide(cap) + slide(cap) + slide(cap) +
              '</div><div class="slider__ctrl"><div class="slider__bars"><button type="button" aria-current="true"></button><button type="button" aria-current="false"></button><button type="button" aria-current="false"></button></div>'
              f'<div class="slider__arrows"><button class="arrow" type="button" data-prev>{CHEV_L}</button><button class="arrow" type="button" data-next>{CHEV_R}</button></div></div></div>')
    nav = ["Context", "The challenge", "Approach", "The flow", "On mobile"]
    secs = (sec("a", (p1, p2)) +
            f'<section class="sec" id="b"><h2 class="sec__h">Context</h2><p>{esc(p1)}</p><p>{esc(p2)}</p>{slider}</section>' +
            sec("c", (p1, p2)))
    page = head_html(L, "case", "Replica", "", p)
    page = page.replace("</head>", "<style>.sec p+p{margin-top:0}</style></head>")
    page += header_html(L, "case", "sales-crm", p)
    page += f"""
<main id="top">
  <header class="case-head"><h1 class="case-title">Sales CRM</h1><p class="case-lead">{esc(crm["lead"])}</p></header>
  <figure class="case-hero"><div class="case-hero__frame"></div></figure>
  <div class="case-body">
    <nav class="case-nav"><ul>{''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in zip('abcde', nav))}</ul></nav>
    <div class="case-content">{secs}</div>
  </div>
  {more_html('crm', L, p)}
"""
    page += tail_html(L, "case", "sales-crm", p)
    open(os.path.join(ROOT, "cases", "_replica.html"), "w", encoding="utf-8").write(page)


def build_modal():
    """Модалка отдельно, в рамке 352×307 (без подложки) — для сверки с Frame_1321316017.png."""
    L, p = T["en"], "../"
    body = modal_html(L, p).replace('<dialog class="modal" id="contact-modal"',
                                    '<dialog class="modal" open style="position:absolute;inset:0 auto auto 0;margin:0;animation:none;box-shadow:none;height:307px;max-height:none;max-width:none"')
    page = head_html(L, "case", "Modal", "", p).replace('<body class="case-page">', '<body style="margin:0;overflow:hidden;background:#fff">') + body + "</body></html>"
    open(os.path.join(ROOT, "cases", "_modal.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    os.makedirs(os.path.join(ROOT, "cases"), exist_ok=True)
    if arg == "replica":
        build_replica(); print("replica built")
    elif arg == "modal":
        build_modal(); print("modal built")
    else:
        keep = {SLUG[c] + ".html" for c in ORDER}
        for lang in ("en", "ru"):
            build_home(lang)
            for cid in ORDER:
                print(lang, cid, build_case(cid, lang))
            # страницы кейсов, которых больше нет в ORDER, удаляем
            d = os.path.join(ROOT, "ru" if lang == "ru" else "", "cases")
            for f in os.listdir(d):
                if f.endswith(".html") and not f.startswith("_") and f not in keep:
                    os.remove(os.path.join(d, f)); print("удалён", lang, f)
