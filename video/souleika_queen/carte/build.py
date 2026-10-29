"""Carte surprise « L'Enveloppe enchantée » : assemble le site statique dans work/carte_site/ (hors Git).

La carte (carte/index.html) s'ouvre le 31 octobre à minuit, heure de Djibouti, en brisant un sceau de cire ;
la chanson démarre, la lettre se révèle au rythme du chant, puis le film « Nuit enchantée » se lance.

Usage :
  python3 carte/build.py --url https://exemple.netlify.app      assemble le site (photos, chant, film, polices)
  node carte/capture.js                                         image d'aperçu WhatsApp + contrôles visuels
  python3 carte/build.py --zip exports/enchante/carte.zip       archive à déposer sur Netlify (glisser-déposer)

Le numéro WhatsApp de Karim est lu dans carte/prive.json (hors Git).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))
from photos import load_rgb  # noqa: E402

OUT = ROOT / "work" / "carte_site"
OUVERTURE = "2026-10-31T00:00:00+03:00"      # minuit, heure de Djibouti
APERCU = "dk3110"                            # lien d'aperçu réservé à Karim : ?apercu=dk3110
EXTRAIT = (61.20, 112.0)                     # extrait du chant : juste avant « Gacaliso », jusqu'à l'interlude


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def portrait(dst):
    """Portrait en arche (3:4) centré sur le visage de P13 (voile rose, papillons)."""
    im = load_rgb(ROOT / "sources" / "photos" / "P13_voile_rose_papillons.png")
    h, w = im.shape[:2]
    cw = int(w * 0.66)
    ch = int(cw * 4 / 3)
    cx, cy = int(w * 0.37), int(h * 0.30)
    x0 = max(0, min(w - cw, cx - cw // 2))
    y0 = max(0, min(h - ch, cy - int(ch * 0.42)))
    crop = cv2.resize(im[y0:y0 + ch, x0:x0 + cw], (600, 800), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(dst), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])


def fonts(media):
    from fontTools import subset
    src = ROOT / "assets" / "fonts"
    for name, dst in [("playfair-display-latin-700-normal.woff", "playfair-700.woff"),
                      ("playfair-display-latin-500-italic.woff", "playfair-500-italic.woff"),
                      ("playfair-display-latin-400-italic.woff", "playfair-400-italic.woff")]:
        shutil.copy(src / name, media / dst)
    for name, dst in [("Inter-Medium.otf", "inter-500.woff"), ("Inter-SemiBold.otf", "inter-600.woff")]:
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "tnum"]
        f = subset.load_font(str(src / name), opts)
        s = subset.Subsetter(opts)
        s.populate(unicodes=list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + [0x2019, 0x2026, 0x00B7, 0x2014, 0x2013, 0x2728, 0x21BA])
        s.subset(f)
        subset.save_font(f, str(media / dst), opts)


def archive(dst):
    """Archive du site prêt à publier (sans la page de fabrication de l'aperçu)."""
    import zipfile
    assert (OUT / "media" / "apercu.jpg").exists(), "lancer d'abord node carte/capture.js (image d'aperçu)"
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            rel = f.relative_to(OUT)
            if f.is_file() and rel.name != "apercu.html" and rel.parts[0] != ".netlify":
                z.write(f, rel)            # fichiers à la racine : l'archive se dépose telle quelle ou décompressée
    print(f"archive : {dst} ({dst.stat().st_size / 1e6:.1f} Mo)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="adresse publique du site (aperçu WhatsApp)")
    ap.add_argument("--zip", help="seulement créer l'archive à déposer sur Netlify")
    args = ap.parse_args()
    if args.zip:
        archive(args.zip)
        return
    if not args.url:
        ap.error("--url est requis pour assembler le site")
    prive = json.loads((HERE / "prive.json").read_text(encoding="utf-8"))
    if OUT.exists():
        shutil.rmtree(OUT)
    media = OUT / "media"
    media.mkdir(parents=True)

    html = (HERE / "index.html").read_text(encoding="utf-8")
    for k, v in {"__URL__": args.url.rstrip("/"), "__TEL__": prive["telephone_whatsapp"],
                 "__APERCU__": APERCU, "__OUVERTURE__": OUVERTURE}.items():
        assert k in html, k
        html = html.replace(k, v)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    shutil.copy(HERE / "apercu.html", OUT / "apercu.html")

    # monogramme du sceau
    dk = cv2.imread(str(ROOT / "assets" / "dk_monogram.png"), cv2.IMREAD_UNCHANGED)
    cv2.imwrite(str(media / "dk.png"), cv2.resize(dk, (256, round(256 * dk.shape[0] / dk.shape[1])), interpolation=cv2.INTER_AREA))
    portrait(media / "portrait.jpg")
    fonts(media)

    # chant : extrait du master (fondu d'entrée court, fondu de sortie long)
    a, b = EXTRAIT
    run(["ffmpeg", "-v", "error", "-y", "-ss", a, "-to", b, "-i", ROOT / "work" / "audio_master.wav",
         "-af", f"afade=t=in:d=0.6,afade=t=out:st={b - a - 6:.2f}:d=6", "-c:a", "libmp3lame", "-b:a", "128k",
         "-ar", "44100", media / "musique.mp3"])
    # film : version téléphone (720 × 1280) et affiche (première image : la page d'accueil)
    film = ROOT / "exports" / "enchante" / "Souleika_Queen_Nuit_Enchantee_Telephone_720p.mp4"
    shutil.copy(film, media / "film.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", film, "-frames:v", "1", "-q:v", "3", media / "poster.jpg"])

    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (OUT / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  Referrer-Policy: no-referrer\n"
                                  "/media/*\n  Cache-Control: public, max-age=86400\n", encoding="utf-8")
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"site assemblé : {OUT} ({total / 1e6:.1f} Mo)")
    for f in sorted(media.iterdir()):
        print(f"  media/{f.name:24s} {f.stat().st_size / 1e3:8.0f} ko")


if __name__ == "__main__":
    main()
