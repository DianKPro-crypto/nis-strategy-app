"""Fonds flous dérivés (9:16) pour les plans intégrés en bande — usage : python3 -I make_backdrops.py <dossier public/scenes>"""
import sys, os
from PIL import Image, ImageFilter, ImageEnhance
d = sys.argv[1]
W, H = 1080, 1920
for f in sorted(os.listdir(d)):
    if not f.endswith('.jpg') or f.startswith('bg_'):
        continue
    im = Image.open(os.path.join(d, f)).convert('RGB')
    s = max(W / im.width, H / im.height) * 1.08
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    l = (im.width - W) // 2; t = (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(48))
    im = ImageEnhance.Brightness(im).enhance(0.5)
    im = ImageEnhance.Color(im).enhance(0.85)
    im.save(os.path.join(d, 'bg_' + f), quality=90)
    print('bg_' + f)
