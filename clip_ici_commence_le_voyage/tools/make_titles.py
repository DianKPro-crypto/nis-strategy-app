"""Titres pré-rendus en PNG (Playfair Display, ivoire + or), pour un rendu sans chargement de police dans le navigateur.
Usage : python3 -I make_titles.py <dossier public>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
pub = sys.argv[1]
F500 = os.path.join(pub, 'fonts/playfair-display-latin-500-normal.woff2')
F400I = os.path.join(pub, 'fonts/playfair-display-latin-400-italic.woff2')
IVORY, GOLD = (247, 240, 227, 255), (227, 179, 76, 255)
PAD = 60
def title(size, align, rule_w, out):
    f1 = ImageFont.truetype(F500, size); f2 = ImageFont.truetype(F400I, round(size * 1.08))
    l1, l2 = 'Ici commence', 'le voyage'
    w1 = f1.getlength(l1); w2 = f2.getlength(l2)
    W = int(max(w1, w2)) + 2 * PAD
    lh1, lh2 = size * 1.04, size * 1.08 * 1.04
    H = int(lh1 + lh2 + size * 0.32 + 2) + 2 * PAD
    txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
    def x(w): return PAD + ((W - 2 * PAD - w) / 2 if align == 'center' else (W - 2 * PAD - w))
    d.text((x(w1), PAD + lh1 / 2), l1, font=f1, fill=IVORY, anchor='lm')
    d.text((x(w2), PAD + lh1 + lh2 / 2), l2, font=f2, fill=GOLD, anchor='lm')
    ry = PAD + lh1 + lh2 + size * 0.32
    d.rectangle([x(rule_w), ry, x(rule_w) + rule_w, ry + 2], fill=(227, 179, 76, 230))
    a = txt.split()[3]
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6)))
    sh2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh2.putalpha(a.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: int(v * 0.55)))
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    base.alpha_composite(sh, (0, 2)); base.alpha_composite(sh2, (0, 1)); base.alpha_composite(txt)
    base.save(os.path.join(pub, 'titles', out)); print(out, base.size)
os.makedirs(os.path.join(pub, 'titles'), exist_ok=True)
title(112, 'center', 120, 'title_h_open.png')
title(92, 'right', 120, 'title_h_final.png')
title(118, 'center', 110, 'title_v_open.png')
title(100, 'center', 110, 'title_v_final.png')
