#!/usr/bin/env python3
"""Копия сайта в /tmp/site-test (или $TEST_SITE) с картинками-заглушками в assets/cases/ —
   чтобы тесты и скриншоты в песочнице (без доступа к keprah.github.io) не ждали сеть.
   python3 tools/tests/make_test_copy.py"""
import os, shutil
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DST = os.environ.get("TEST_SITE", "/tmp/site-test")
shutil.rmtree(DST, ignore_errors=True)
shutil.copytree(ROOT, DST, ignore=shutil.ignore_patterns(".git", "tools", "__pycache__"))
out = os.path.join(DST, "assets", "cases"); os.makedirs(out, exist_ok=True)
SIZES = {"crm_pc": (1500, 723), "fin_main": (1500, 877), "ds_vars": (1500, 828)}
COL = [(176, 190, 235), (176, 214, 235), (235, 230, 176)]
for i, k in enumerate("crm_pc crm_phone crm_flow crm_meet fin_main fin_sales fin_plan fin_anim fin_proto fin_wire fin_layout ds_vars".split()):
    w, h = SIZES.get(k, (1500, 800))
    im = Image.new("RGB", (w, h), COL[i % 3]); d = ImageDraw.Draw(im)
    d.line((0, 0, w, h), fill=(90, 90, 90), width=3); d.line((0, h, w, 0), fill=(90, 90, 90), width=3)
    d.text((40, 40), f"{k}  {w}x{h}", fill=(20, 20, 20))
    im.save(os.path.join(out, k + ".webp"), "WEBP", quality=60)
print("копия сайта:", DST)
