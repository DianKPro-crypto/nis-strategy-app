"""Prépare les déclinaisons numériques du logo Dian K Pro à partir de dk-logo-original.png.

Usage (une seule fois, ou après changement de logo) : python3 source/marque/preparer_logo.py
Nécessite Pillow et NumPy. Les fichiers produits sont ensuite intégrés par construire.py.

Produit :
- dk-monogramme.png   le monogramme DK seul, en masque alpha (couleur appliquée par CSS selon le thème) ;
- dk-logo-complet.png le logo complet (monogramme, nom, titre, signature), en masque alpha ;
- dk-favicon.png      le monogramme or sur fond noir, pour l'onglet du navigateur.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ICI = Path(__file__).parent
ORIGINAL = Image.open(ICI / "dk-logo-original.png").convert("RGB")
OR = (227, 179, 76)


def masque(boite, largeur=None, hauteur=None):
    """Découpe une zone et convertit l'or sur noir en masque alpha (blanc + transparence)."""
    zone = np.asarray(ORIGINAL.crop(boite)).astype(float)
    alpha = np.clip((zone[:, :, 0] - 28) / (210 - 28), 0, 1)  # le rouge porte l'essentiel de l'or
    img = Image.fromarray(np.dstack([np.full(alpha.shape, 255), (alpha * 255).round()]).astype("uint8"), "LA")
    if largeur:
        img = img.resize((largeur, round(img.height * largeur / img.width)), Image.LANCZOS)
    if hauteur:
        img = img.resize((round(img.width * hauteur / img.height), hauteur), Image.LANCZOS)
    return img


masque((387, 208, 892, 673), hauteur=240).save(ICI / "dk-monogramme.png", optimize=True)
masque((96, 208, 1162, 1035), largeur=840).save(ICI / "dk-logo-complet.png", optimize=True)

mono = masque((387, 208, 892, 673), hauteur=52)
fav = Image.new("RGB", (64, 64), (11, 11, 12))
or_plein = Image.new("RGB", mono.size, OR)
fav.paste(or_plein, ((64 - mono.width) // 2, (64 - mono.height) // 2), mono.getchannel("A"))
fav.save(ICI / "dk-favicon.png", optimize=True)
print("Déclinaisons du logo créées.")
