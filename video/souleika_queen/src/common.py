"""Constantes, chargement de la configuration et petites fonctions partagées."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
FPS = 30
BAND_GAP = 6          # filet doré entre les bandes des plans « bands »

# Zone de sécurité (8 % côtés, 12 % haut, 18 % bas)
SAFE = (int(W * 0.08), int(H * 0.12), int(W * 0.92), int(H * 0.82))

PALETTE = {
    "night": "#101827",   # bleu nuit
    "gold": "#D6B777",    # or champagne
    "ivory": "#F5EFE5",   # ivoire
    "mint": "#BFE3D0",    # vert menthe discret
    "black": "#0B0B0C",
}


def rgb(name_or_hex):
    h = PALETTE.get(name_or_hex, name_or_hex)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))


def load_json(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smoothstep(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return a + (b - a) * t


EASE = {
    "linear": lambda x: x,
    "inOutSine": lambda x: 0.5 - 0.5 * math.cos(math.pi * x),
    "outCubic": lambda x: 1 - (1 - x) ** 3,
    "inCubic": lambda x: x ** 3,
    "inOutCubic": lambda x: 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2,
    "outQuart": lambda x: 1 - (1 - x) ** 4,
    "outBack": lambda x: 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2,
}


def tc(t):
    """Secondes -> code temporel mm:ss:ii (ii = numéro d'image, 30 par seconde)."""
    f = int(round(t * FPS))
    s, ff = divmod(f, FPS)
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}:{ff:02d}"
