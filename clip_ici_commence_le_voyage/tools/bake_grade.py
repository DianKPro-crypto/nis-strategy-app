"""Intègre la légère correction (saturation ×1.04, contraste ×1.03) dans les images de public/scenes.
Usage : python3 -I bake_grade.py <dossier>   (à exécuter une seule fois sur des fichiers fraîchement extraits)"""
import sys, os
from PIL import Image, ImageEnhance
d = sys.argv[1]
for f in sorted(os.listdir(d)):
    if f.endswith('.jpg') and not f.startswith('bg_'):
        p = os.path.join(d, f); im = Image.open(p).convert('RGB')
        im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.04)).enhance(1.03)
        im.save(p, quality=94); print(f)
