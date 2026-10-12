"""Bruitages discrets du film Dian K. Pro, synthétisés (aucun échantillon externe).

Usage : python3 -I audio/sfx.py <fr|en> <h|v> <sortie.wav>

Les repères reprennent le minutage TM de render/scene.html : toute modification
de TM doit être reportée ici.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
TM = {
    'fr': dict(s2a=13.6, s2b=20.3, s3=28.6, s4=40.0, end=53.6, kw=[28.9, 31.1, 32.2, 33.6], pc=[20.6, 21.8, 24.2, 25.2, 26.0, 27.1], cta=4.9, tag=9.2),
    'en': dict(s2a=12.5, s2b=19.4, s3=25.9, s4=36.9, end=46.4, kw=[26.1, 27.6, 29.1, 30.6], pc=[19.8, 20.9, 21.9, 23.0, 24.1, 25.0], cta=3.4, tag=6.6),
}
rng = np.random.default_rng(7)


def env_ad(n, a, d):
    """Enveloppe attaque linéaire / déclin exponentiel (en secondes)."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / d))
    return e


def band(x, lo, hi):
    return sosfilt(butter(4, [lo, hi], btype='band', fs=SR, output='sos'), x)


def whoosh(dur=1.2, lo=300, hi=5000, rise=.6):
    """Souffle filtré dont la bande monte puis redescend (passage de caméra)."""
    n = int(dur * SR); noise = rng.standard_normal(n)
    out = np.zeros(n); seg = 2048
    for i in range(0, n, seg // 2):
        p = i / n; c = lo * (hi / lo) ** (np.sin(np.pi * min(1, p / rise * .5 + p * .5)))
        chunk = noise[i:i + seg]
        if len(chunk) < 64: break
        y = band(chunk, max(80, c * .6), min(SR / 2 - 100, c * 1.6)) * np.hanning(len(chunk))
        out[i:i + len(chunk)] += y
    e = np.sin(np.pi * np.clip(np.arange(n) / n, 0, 1)) ** 1.6
    return out * e / (np.abs(out).max() + 1e-9)


def metal(f0=640, dur=1.6, partials=(1, 2.76, 5.40, 8.93, 13.34), decay=.55):
    """Résonance métallique inharmonique (cloche / feuille d'or)."""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, r in enumerate(partials):
        y += np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t / (decay / (1 + k * .7))) / (1 + k)
    return y * env_ad(n, .004, dur) / (np.abs(y).max() + 1e-9)


def tick(f=2600, dur=.035):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / .006)


def blip(f1=900, f2=1500, dur=.12):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(np.linspace(f1, f2, n)) / SR
    return np.sin(ph) * env_ad(n, .005, .04) * .9 + np.sin(2 * ph) * env_ad(n, .003, .02) * .25


def impact(dur=2.6):
    """Impact du logo : coup sourd grave + anneau métallique + traîne."""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 58 * np.exp(-t * 1.2) + 34
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .55)
    thump = band(rng.standard_normal(n), 60, 400) * np.exp(-t / .07) * .8
    ring = np.zeros(n); r = metal(330, dur, decay=1.1); ring[:len(r)] = r * .5
    tail = band(rng.standard_normal(n), 2000, 9000) * np.exp(-t / .9) * .05
    y = boom * 1.0 + thump + ring + tail
    return y / (np.abs(y).max() + 1e-9)


def shimmer(dur=1.6):
    """Scintillement aigu (gravure de la devise, reflets)."""
    n = int(dur * SR); t = np.arange(n) / SR
    y = band(rng.standard_normal(n), 5000, 12000) * (.5 + .5 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / dur) ** 2
    m = metal(1850, dur, partials=(1, 1.5, 2.2, 3.1), decay=.5) * .35
    return (y / (np.abs(y).max() + 1e-9)) * .6 + m


def place(bus, sig, at, gain_db, pan=0.):
    i = int(at * SR)
    if i >= bus.shape[0] or i + len(sig) <= 0: return
    j = min(bus.shape[0], i + len(sig)); s = sig[:j - i] * 10 ** (gain_db / 20)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[i:j, 0] += s * l * 1.414; bus[i:j, 1] += s * r * 1.414


def build(lang, fmt):
    T = TM[lang]; DA = T['s2a'] - 13.56
    bus = np.zeros((int((T['end'] + .5) * SR), 2))
    place(bus, metal(880, 1.4), .12, -30, -.3)                      # éclat sur la page de garde
    place(bus, whoosh(1.5, 200, 3500), .95, -27)                     # plongée vers les circuits
    for k, at in enumerate([2.3, 2.75, 3.15]):                       # activation des circuits
        place(bus, blip(700 + k * 220, 1100 + k * 260, .09), at, -33, -.4 + k * .4)
    place(bus, whoosh(1.4, 400, 5000), 5.9, -31)   # retour cadrage portrait
    place(bus, metal(520, 1.8, decay=.7), 9.0 + DA * .5, -32, .35)  # reflet sur la carte en verre
    place(bus, whoosh(1.4, 250, 4500), T['s2a'] - 1.0, -26)          # particules → globe
    place(bus, metal(440, 2.0, decay=.9), T['s2a'] + .1, -30)
    t0 = 14.2 + DA; step = (T['s2b'] - .9 - t0) / 40
    for k in range(40):                                              # compteur des 40 pays
        place(bus, tick(2300 + (k % 5) * 180), t0 + k * step + .17, -34 + (k % 4 == 0) * 3, (k / 39) * 1.2 - .6)
    place(bus, blip(1200, 1800, .14), t0 + 40 * step + .2, -29)      # compteur à 40
    if fmt == 'h':
        place(bus, whoosh(1.2, 300, 4500), T['s2b'] - .7, -27)
        for at in T['pc'][1:]:                                       # rotations du carrousel
            place(bus, whoosh(.6, 500, 6000, .5), at - .55, -31)
            place(bus, metal(760, .7, decay=.25), at - .05, -36, .3)
    else:
        for i in (0, 2, 4):                                          # arrivée des 3 écrans empilés
            place(bus, whoosh(.85, 400, 6000, .5), T['pc'][i] - .8, -28)
            place(bus, metal(700, .8, decay=.3), T['pc'][i] - .05, -34)
    place(bus, whoosh(1.0, 300, 4000), T['s3'] - .5, -29)
    for k, at in enumerate(T['kw']):                                 # activation des données
        place(bus, blip(800 + k * 150, 1300 + k * 200, .12), at, -29, -.3 + k * .2)
        for j in range(3): place(bus, tick(3200 + j * 300, .025), at + .14 + j * .07, -38)
    place(bus, whoosh(1.1, 200, 3000), T['s4'] - .9, -25)            # convergence
    place(bus, impact(), T['s4'] - .02, -17)                         # impact du logo
    place(bus, metal(600, 1.6, decay=.6), T['s4'] + 1.0, -31, -.3)   # nom DIAN K. PRO
    place(bus, shimmer(1.7), T['s4'] + T['tag'], -27)                # gravure de la devise
    place(bus, blip(1000, 1400, .1), T['s4'] + T['cta'], -33)        # appel à l'action
    return bus


if __name__ == '__main__':
    lang, fmt, out = sys.argv[1], sys.argv[2], sys.argv[3]
    b = build(lang, fmt)
    pk = np.abs(b).max()
    if pk > .9: b *= .9 / pk
    wavfile.write(out, SR, (b * 32767).astype(np.int16))
    print(out, f'{b.shape[0] / SR:.2f} s, crête {20 * np.log10(np.abs(b).max() + 1e-9):.1f} dBFS')
