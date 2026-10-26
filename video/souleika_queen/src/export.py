"""Chaîne complète : rendu parallèle sans perte -> encodages finaux -> planche, timeline CSV, contrôle qualité.

Usage :
  python3 src/export.py            tout refaire (rendu + exports + contrôles)
  python3 src/export.py --encode   ré-encoder et refaire les livrables sans re-rendre les images
"""
import argparse
import csv
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import FPS, H, ROOT, W, load_json, tc

EXP = ROOT / "exports"
WORK = ROOT / "work"
MAIN = EXP / "Souleika_Queen_Anniversaire_1080x1920.mp4"
SHARE = EXP / "Souleika_Queen_Partage.mp4"
BOARD = EXP / "Souleika_Queen_Storyboard.jpg"
CSVF = EXP / "Souleika_Queen_Timeline.csv"
STATUS = [EXP / "Souleika_Queen_Statut_WhatsApp_1-2.mp4", EXP / "Souleika_Queen_Statut_WhatsApp_2-2.mp4"]
WORKERS, CHUNKS = 4, 12


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd)[:200], flush=True)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def total_frames(tl):
    return int(round(tl["shots"][-1]["end"] * FPS))


def render_all(tl):
    n = total_frames(tl)
    (WORK / "chunks").mkdir(parents=True, exist_ok=True)
    bounds = np.linspace(0, n, CHUNKS + 1).astype(int)
    jobs = [(i, bounds[i], bounds[i + 1]) for i in range(CHUNKS)]
    t0 = time.time()

    def job(j):
        i, a, b = j
        out = WORK / "chunks" / f"c{i:02d}.mkv"
        subprocess.run([sys.executable, str(ROOT / "src" / "render.py"), "--range", str(a), str(b), "--out", str(out.relative_to(ROOT))],
                       check=True, cwd=ROOT, stderr=subprocess.DEVNULL)
        print(f"  segment {i:02d} [{a}-{b}] terminé ({time.time() - t0:.0f} s)", flush=True)
        return out

    with ThreadPoolExecutor(WORKERS) as ex:
        outs = list(ex.map(job, jobs))
    with open(WORK / "chunks" / "list.txt", "w") as f:
        for o in outs:
            f.write(f"file '{o.name}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", WORK / "chunks" / "list.txt", "-c", "copy",
         WORK / "master_lossless.mkv"])
    print(f"rendu terminé en {time.time() - t0:.0f} s, {n} images")


def audio_filter(tl):
    st, d = tl["audio_fade_out"]
    return f"volume={tl['audio_gain_db']}dB,afade=t=out:st={st}:d={d}"


COLOR = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]


def encode(tl):
    EXP.mkdir(exist_ok=True)
    src = WORK / "master_lossless.mkv"
    aud = ROOT / tl["audio"]
    common_v = ["-pix_fmt", "yuv420p", "-r", str(FPS), "-fps_mode", "cfr", *COLOR, "-movflags", "+faststart"]
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", aud, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "film", "-profile:v", "high", "-level:v", "4.2",
         "-maxrate", "40M", "-bufsize", "60M", *common_v,
         "-af", audio_filter(tl), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", MAIN])
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", aud, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-profile:v", "high", "-level:v", "4.1",
         "-maxrate", "4500k", "-bufsize", "9M", *common_v,
         "-af", audio_filter(tl), "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", SHARE])
    # Déclinaison Statut WhatsApp (préférence Dr Sidibé : 90 s maximum par élément) -> 2 parties
    cut = 89.24   # temps fort de l'interlude instrumental : chaque partie <= 90 s
    end = total_frames(tl) / FPS
    for k, (a, b) in enumerate([(0.0, cut), (cut, end)]):
        af = audio_filter(tl) + f",atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.25,afade=t=out:st={b - a - 0.3:.3f}:d=0.3"
        if k == 0:
            af = f"volume={tl['audio_gain_db']}dB,atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=out:st={b - a - 0.3:.3f}:d=0.3"
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", aud, "-map", "0:v", "-map", "1:a",
             "-vf", f"trim={a}:{b},setpts=PTS-STARTPTS" + (",fade=t=in:d=0.3" if k else f",fade=t=out:st={b - a - 0.3:.3f}:d=0.3"),
             "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-profile:v", "high", "-level:v", "4.1",
             "-maxrate", "5M", "-bufsize", "10M", *common_v, "-c:a", "aac", "-b:a", "160k", "-ar", "48000", STATUS[k]])


# ---------------------------------------------------------------------- planche de contrôle

def board_times(tl):
    out = [(0.0, "S01", "Page d'accueil (image 0)", "P00")]
    for s in tl["shots"]:
        a, b = s["start"], s["end"]
        if s.get("layout") == "bands":
            t = min(b - 0.1, max(x["t_in"] for x in s["bands"]) + 0.75)
            photos = "+".join(x["photo"] for x in s["bands"])
        else:
            t = a + (b - a) * 0.6
            photos = s["photo"]
        if s["id"] == "S01":
            continue
        out.append((t, s["id"], s["section"], photos))
    return out


def storyboard(tl):
    items = board_times(tl)
    frames = [int(round(t * FPS)) for t, *_ in items]
    tmp = WORK / "board"
    tmp.mkdir(exist_ok=True)
    for f in tmp.glob("*.png"):
        f.unlink()
    sel = "+".join(f"eq(n\\,{f})" for f in frames)
    run(["ffmpeg", "-v", "error", "-y", "-i", MAIN, "-vf", f"select='{sel}',scale=240:427", "-fps_mode", "passthrough",
         tmp / "f%03d.png"])
    files = sorted(tmp.glob("f*.png"))
    assert len(files) == len(items), (len(files), len(items))
    cols = 9
    tw, th, lab = 240, 427, 74
    gap = 14
    rows = (len(items) + cols - 1) // cols
    head = 150
    Wb = cols * tw + (cols + 1) * gap
    Hb = head + rows * (th + lab + gap) + gap
    board = Image.new("RGB", (Wb, Hb), (16, 24, 39))
    d = ImageDraw.Draw(board)
    fdir = ROOT / "assets" / "fonts"
    ft = ImageFont.truetype(str(fdir / "playfair-display-latin-700-normal.woff"), 54)
    fs = ImageFont.truetype(str(fdir / "Inter-Medium.otf"), 22)
    fl = ImageFont.truetype(str(fdir / "Inter-SemiBold.otf"), 19)
    fl2 = ImageFont.truetype(str(fdir / "Inter-Medium.otf"), 17)
    d.text((gap + 6, 30), "SOULEIKA QUEEN — L’amour en lumière", font=ft, fill=(214, 183, 119))
    d.text((gap + 8, 100), f"Planche de contrôle · images extraites du montage final ({MAIN.name}) · 1080×1920 · 30 i/s · "
           f"{len(items)} plans", font=fs, fill=(245, 239, 229))
    for k, ((t, sid, sec, ph), fpath) in enumerate(zip(items, files)):
        r, c = divmod(k, cols)
        x = gap + c * (tw + gap)
        y = head + r * (th + lab + gap)
        board.paste(Image.open(fpath).convert("RGB"), (x, y))
        d.rectangle([x - 1, y - 1, x + tw, y + th], outline=(214, 183, 119), width=1)
        d.text((x + 2, y + th + 8), f"{sid} · {tc(t)[:5]} · {ph}", font=fl, fill=(245, 239, 229))
        lab2 = sec if fl2.getlength(sec) <= tw - 4 else sec[:max(1, int(len(sec) * (tw - 16) / fl2.getlength(sec)))].rstrip(" ,") + "…"
        d.text((x + 2, y + th + 36), lab2, font=fl2, fill=(214, 183, 119))
    board.save(BOARD, quality=90)
    return items


# ---------------------------------------------------------------------- timeline CSV

def timeline_csv(tl):
    texts = load_json("config/texts.json")["blocks"]
    lyr = load_json("analysis/lyrics_aligned.json")["lines"]
    with open(CSVF, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Plan", "Section", "Début (s)", "Fin (s)", "Début (mm:ss:ii, ii = image)", "Fin (mm:ss:ii)", "Durée (s)",
                    "Photo(s)", "Cadrage zoom début→fin", "Point source début→fin", "Transition d'entrée",
                    "Texte(s) à l'écran [début–fin s]", "Paroles chantées pendant le plan (vérifiées)"])
        for s in tl["shots"]:
            a, b = s["start"], s["end"]
            if s.get("layout") == "bands":
                photos = " | ".join(x["photo"] for x in s["bands"])
                zoom = " | ".join(f"{x['z0']:.2f}→{x['z1']:.2f}" for x in s["bands"])
                pt = "bandes horizontales (entrées : " + ", ".join(f"{x['t_in']:.2f}" for x in s["bands"]) + " s)"
            else:
                photos = s["photo"]
                zoom = f"{s['z0']:.3f}→{s['z1']:.3f}"
                pt = f"({s['c0'][0]:.2f}, {s['c0'][1]:.2f})→({s['c1'][0]:.2f}, {s['c1'][1]:.2f})"
            tr = s.get("trans", {"type": "cut"})
            trs = "coupe" if tr["type"] == "cut" else f"{tr['type']} {tr['dur']:.1f} s"
            if s.get("punch"):
                trs += " + impact"
            if s.get("fade_in"):
                trs = f"ouverture depuis le noir {s['fade_in']} s"
            tx = [f"« {' '.join(l['text'].replace('|', '') for l in t['lines'])} » [{t['start']:.2f}–{t['end']:.2f}]"
                  for t in texts if t["start"] < b and t["end"] > a and t["start"] >= a - 0.5]
            ly = [l["text"] for l in lyr if a - 0.15 <= l["t"] < b - 0.15]
            w.writerow([s["id"], s["section"], f"{a:.2f}", f"{b:.2f}", tc(a), tc(b), f"{b - a:.2f}", photos, zoom, pt, trs,
                        " · ".join(tx), " / ".join(ly)])


# ---------------------------------------------------------------------- contrôle qualité

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    return i, lra, tp


def audio_presence(path, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    secs = int(np.floor(len(x) / 8000))
    rms = [20 * np.log10(np.sqrt(np.mean(x[i * 8000:(i + 1) * 8000] ** 2)) + 1e-9) for i in range(secs)]
    silent = [i for i, v in enumerate(rms) if v < -45]
    return len(x) / 8000, silent, float(np.max(np.abs(x)))


def black_segments(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "blackdetect=d=0.1:pix_th=0.06",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)


def qc(tl, items):
    lines = ["# Rapport de contrôle qualité — SOULEIKA QUEEN", ""]
    for path in [MAIN, SHARE, *STATUS]:
        p = probe(path)
        v = next(s for s in p["streams"] if s["codec_type"] == "video")
        a = next(s for s in p["streams"] if s["codec_type"] == "audio")
        size = int(p["format"]["size"]) / 1e6
        lines += [f"## {path.name}",
                  f"- Vidéo : {v['codec_name']} {v.get('profile')} niveau {v.get('level')}, {v['width']}×{v['height']}, "
                  f"{v['pix_fmt']}, {v['r_frame_rate']} (moy. {v['avg_frame_rate']}), {v.get('nb_frames')} images, "
                  f"{float(v['duration']):.3f} s, couleurs {v.get('color_space')}/{v.get('color_primaries')}/{v.get('color_transfer')}",
                  f"- Audio : {a['codec_name']} {a.get('profile')}, {a['sample_rate']} Hz, {a['channels']} canaux, "
                  f"{int(a.get('bit_rate', 0)) // 1000} kb/s, {float(a['duration']):.3f} s",
                  f"- Conteneur : {float(p['format']['duration']):.3f} s, {size:.1f} Mo, débit global {int(p['format']['bit_rate']) / 1e6:.1f} Mb/s"]
        if path in (MAIN, SHARE):
            i, lra, tp = loudness(path)
            adur, silent, peak = audio_presence(path, float(p["format"]["duration"]))
            lines.append(f"- Sonie : {i:.1f} LUFS intégrés, LRA {lra:.1f} LU, crête vraie {tp:.1f} dBTP, échantillon max {peak:.3f}")
            lines.append(f"- Son présent : {adur:.2f} s décodées ; secondes sous −45 dBFS : {silent if silent else 'aucune'}")
            lines.append(f"- Images noires détectées (fondus attendus seulement) : {black_segments(path)}")
            with open(path, "rb") as fh:
                head = fh.read(4096)
            lines.append(f"- faststart (atome moov avant mdat) : {'oui' if head.find(b'moov') != -1 and (head.find(b'mdat') == -1 or head.find(b'moov') < head.find(b'mdat')) else 'NON'}")
        lines.append("")
    # utilisation des photos
    used = {}
    for s in tl["shots"]:
        ph = [b["photo"] for b in s["bands"]] if s.get("layout") == "bands" else [s["photo"]]
        for x in ph:
            used.setdefault(x, []).append(s["id"])
    lines += ["## Photos utilisées (plans)", *[f"- {k} : {len(v)} plans ({', '.join(v)})" for k, v in sorted(used.items())], ""]
    missing = [f"P{i:02d}" for i in range(0, 13) if f"P{i:02d}" not in used]
    lines.append(f"Photos absentes : {missing if missing else 'aucune'}")
    lines.append("")
    # textes
    sys.path.insert(0, str(ROOT / "src"))
    from render import Renderer
    r = Renderer()
    lines.append("## Textes : zone de sécurité et recouvrement visages / yeux / bouches / mains / graphisme")
    for tid, txt, a, b, issues in r.qc_texts():
        lines.append(f"- {tid} [{a:.2f}–{b:.2f} s] « {txt.replace('|', '')} » : {'OK' if not issues else '; '.join(issues)}")
    lines.append("")
    lines.append(f"## Planche : {len(items)} vignettes (une par plan + image 0)")
    (ROOT / "analysis" / "qc_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--encode", action="store_true", help="ne pas re-rendre les images")
    args = ap.parse_args()
    tl = load_json("config/timeline.json")
    if not args.encode:
        render_all(tl)
    encode(tl)
    items = storyboard(tl)
    timeline_csv(tl)
    qc(tl, items)


if __name__ == "__main__":
    main()
