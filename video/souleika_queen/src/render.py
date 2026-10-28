"""Moteur de rendu image par image du clip « SOULEIKA QUEEN — L'amour en lumière ».

Usage :
  python3 src/render.py --stills 0 18.5 64.2 ...            images de contrôle (work/stills/)
  python3 src/render.py --range 0 900 --out work/c0.mkv      rendu d'un segment (images) en vidéo sans perte
  python3 src/render.py --qc                                 contrôle : textes vs visages/mains, zone de sécurité
"""
import argparse
import math
import subprocess
import sys

import cv2
import numpy as np

import fx
import livefx
from common import BAND_GAP, EASE, FPS, H, ROOT, SAFE, W, clamp, lerp, load_json, rgb, tc
from enchant import Enchant
from photos import Photo, place
from textfx import TextBlock


class Renderer:
    def __init__(self, style=None):
        self.tl = load_json("config/timeline.json")
        pcfg = load_json("config/photos.json")
        tcfg = load_json("config/texts.json")
        an = load_json("analysis/audio_analysis.json")
        self.beats = an["beats_refined"]
        self.duration = self.tl.get("duration") or 179.2
        sections = self.tl["sections"]
        shots = self.tl["shots"]
        self.style = load_json(f"config/style_{style}.json") if style else None
        if self.style:
            self._apply_style(shots, sections, tcfg)
        for i, s in enumerate(shots):
            sec = sections[s["section"]]
            s.setdefault("grade", sec["grade"])
            s["fx"] = {**{"particles": 0.4, "leaks": 0.3, "bloom": 0.22, "rays": 0.0, "ptint": "gold"}, **sec["fx"], **s.get("fx", {})}
            s.setdefault("trans", {"type": "cut", "dur": 0.0})
            if s["trans"]["type"] == "cut":
                s["trans"]["dur"] = 0.0
        for i, s in enumerate(shots):
            d_in = s["trans"]["dur"]
            d_out = shots[i + 1]["trans"]["dur"] if i + 1 < len(shots) else 0.0
            s["vs"], s["ve"] = s["start"] - d_in / 2, s["end"] + d_out / 2
        self.shots = shots
        self.starts = [s["start"] for s in shots]

        # échelle maximale par photo -> maître agrandi une seule fois
        need = {}
        for s in shots:
            for pid, cw, ch, zs in self._cams(s):
                ph = pcfg[pid]
                from PIL import Image
                w, h = Image.open(ROOT / ph["file"]).size
                cover = max(cw / w, ch / h)
                m = max(zs) * cover * (1.06 if s.get("punch") else 1.0) * (1.25 if s["trans"]["type"] == "zoom" else 1.0)
                need[pid] = max(need.get(pid, 0), m)
        self.photos = {pid: Photo(pid, pcfg[pid], m) for pid, m in sorted(need.items())}
        if self.style:                                   # version « Nuit enchantée » : personne et décor séparés
            for ph in self.photos.values():
                ph.load_layers()
        self.live = livefx.build(self.photos, pcfg, self.beats)     # effets animés des photos artistiques

        self.particles = fx.Particles()
        self.events = self.tl.get("events", [])
        for k, ev in enumerate(self.events):
            if ev["type"] == "burst":
                self.particles.add_burst(ev["t"], ev["n"], seed=100 + k)
        self.vignette = fx.make_vignette()
        self.grain = fx.make_grain()
        look = {"palette": self.style["textes"]["palette"], "halo": True} if self.style else None
        self.texts = [TextBlock(b, self.beats, look) for b in tcfg["blocks"]]
        self.enchant = Enchant(self) if self.style else None

    # ------------------------------------------------------------------ variante de style (Nuit enchantée)
    def _apply_style(self, shots, sections, tcfg):
        st = self.style
        gm = st["etalonnage"]
        for name, sec in sections.items():
            sec["grade"] = gm["sections"].get(name, gm["defaut"])
        tr = st["transitions"]
        for i, s in enumerate(shots):
            if i == 0:
                continue
            t = s.get("trans", {"type": "cut", "dur": 0.0})
            if t["type"] == "cut":
                new = tr["coupe_rythmee"] if s.get("punch") else tr["coupe"]
                s["trans"] = {"type": new["type"], "dur": new["dur"]}
            elif t["type"] in ("dissolve", "light"):
                m = tr[t["type"]]
                s["trans"] = {"type": m["type"], "dur": min(m["max"], t["dur"] * m["facteur"])}
            elif t["type"] == "zoom":
                s["trans"] = {"type": tr["zoom"]["type"], "dur": tr["zoom"]["dur"]}
            if not tr.get("garder_punch"):
                s["punch"] = False
        o = st.get("ouverture")
        for i, s in enumerate(shots):
            if o and s["id"] == o["plan"]:
                s["trans"] = dict(o["transition"])
                s.pop("fade_in", None)
                shots[i - 1].pop("fade_out", None)
        for i in range(1, len(shots)):          # une transition ne dépasse jamais 80 % du plus court des plans voisins
            lim = 0.8 * min(shots[i]["end"] - shots[i]["start"], shots[i - 1]["end"] - shots[i - 1]["start"])
            shots[i]["trans"]["dur"] = min(shots[i]["trans"]["dur"], lim)
        tx = st["textes"]
        for b in tcfg["blocks"]:
            if b["id"] in tx["baguette"]:
                b["anim"] = "wand"
            rep = tx["remplacements"].get(b["id"])
            if rep:
                b["lines"][rep["ligne"]]["text"] = rep["texte"]

    def guard_boxes(self, lays, t):
        """Zones protégées (visages, mains) des images à l'écran, en pixels du cadre."""
        boxes = []
        for s, w, role, p in lays:
            if w < 0.3:
                continue
            if s.get("layout") == "bands":
                n = len(s["bands"])
                bh = (H - BAND_GAP * (n - 1)) // n
                for i in range(n):
                    y0 = i * (bh + BAND_GAP)
                    boxes.append((W * 0.26, y0 + bh * 0.04, W * 0.74, y0 + bh * 0.96, 0.8))
                continue
            z, c, a = self.camera(s, t, role, p)
            ph = self.photos[s["photo"]]
            sc, tx, ty, _, _ = place(ph.w, ph.h, W, H, z, c, a)
            for name, (x0, y0, x1, y1) in ph.protected_boxes((sc, tx, ty)).items():
                boxes.append((x0, y0, x1, y1, 1.0 if name.startswith(("visage", "lunettes", "bouche")) else 0.6))
        return boxes

    def transforms(self, lays, t):
        out = {}
        for s, w, role, p in sorted(lays, key=lambda x: x[1]):
            if s.get("layout") == "bands" or w < 0.05:
                continue
            z, c, a = self.camera(s, t, role, p)
            ph = self.photos[s["photo"]]
            sc, tx, ty, _, _ = place(ph.w, ph.h, W, H, z, c, a)
            out[s["photo"]] = (sc, tx, ty, ph.w, ph.h)
        return out

    # ------------------------------------------------------------------ caméras
    @staticmethod
    def _cams(s):
        if s.get("layout") == "bands":
            n = len(s["bands"])
            bh = (H - BAND_GAP * (n - 1)) // n
            return [(b["photo"], W, bh, (b["z0"], b["z1"])) for b in s["bands"]]
        return [(s["photo"], W, H, (s["z0"], s["z1"]))]

    @staticmethod
    def _interp(spec, s, t):
        end = s.get("cam_end", s["ve"])            # cam_end : mouvement principal terminé avant la fin du plan
        span = max(1e-6, end - s["vs"])
        e = EASE[s.get("ease", "inOutSine")](clamp((t - s["vs"]) / span))
        z = spec["z0"] * (spec["z1"] / spec["z0"]) ** e
        c = (lerp(spec["c0"][0], spec["c1"][0], e), lerp(spec["c0"][1], spec["c1"][1], e))
        if "z2" in spec and t > end:                # puis dérive très lente jusqu'à la fin (z2, c2)
            e2 = EASE["inOutSine"](clamp((t - end) / max(1e-6, s["ve"] - end)))
            c2 = spec.get("c2", spec["c1"])
            z = spec["z1"] * (spec["z2"] / spec["z1"]) ** e2
            c = (lerp(spec["c1"][0], c2[0], e2), lerp(spec["c1"][1], c2[1], e2))
        return z, c

    def camera(self, s, t, role=None, p=0.0):
        z, c = self._interp(s, s, t)
        if s.get("punch") and t >= s["start"]:
            k = clamp((t - s["start"]) / 0.32)
            z *= 1 + 0.045 * (1 - EASE["outCubic"](k))
        if role == "zoom_out":     # plan sortant d'une transition « traversée »
            z *= 1 + 0.20 * p * p
        elif role == "zoom_in":
            z *= 1 + 0.15 * (1 - EASE["outCubic"](p))
        return z, c, tuple(s.get("a", (0.5, 0.5)))

    # ------------------------------------------------------------------ rendu d'un plan
    def render_shot(self, s, t, role=None, p=0.0):
        exposure = s.get("exposure", 0.0)
        tint = "mint" if s["grade"] == "mint" else None
        if s.get("layout") == "bands":
            img = np.empty((H, W, 3), np.float32)
            img[:] = np.float32(rgb("night")) * 0.85
            n = len(s["bands"])
            bh = (H - BAND_GAP * (n - 1)) // n
            for i, b in enumerate(s["bands"]):
                prog = clamp((t - b["t_in"]) / b.get("slide", 0.6))
                if prog <= 0:
                    continue
                z, c = self._interp(b, s, t)
                ph = self.photos[b["photo"]]
                band, _ = ph.render(W, bh, z, c, tint=tint)
                band = fx.apply_grade(band, s["grade"], exposure)
                dx = int(round((1 - EASE["outCubic"](prog)) * W * (-1 if b["from"] == "left" else 1)))
                y0 = i * (bh + BAND_GAP)
                xs0, xs1 = max(0, dx), min(W, W + dx)
                img[y0:y0 + bh, xs0:xs1] = band[:, xs0 - dx:xs1 - dx]
            gold = np.float32(rgb("gold"))
            for i in range(1, n):
                y = i * (bh + BAND_GAP) - BAND_GAP
                img[y:y + BAND_GAP] = img[y:y + BAND_GAP] * 0.25 + gold * 0.75
                img[y + 2:y + BAND_GAP - 2] = np.float32([1.0, 0.92, 0.72])
        else:
            z, c, a = self.camera(s, t, role, p)
            u8, tr = self.photos[s["photo"]].render(W, H, z, c, a, tint=tint)
            live = self.live.get(s["photo"])
            if live:
                f = u8.astype(np.float32) * (1 / 255)
                live.draw(f, t, tr)
                u8 = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
            img = fx.apply_grade(u8, s["grade"], exposure)
        if role in ("zoom_out", "zoom_in"):
            strength = p * p if role == "zoom_out" else (1 - p) ** 2
            img = fx.zoom_blur(img, strength)
        return img

    # ------------------------------------------------------------------ image complète
    def shot_index(self, t):
        i = int(np.searchsorted(self.starts, t, side="right")) - 1
        return max(0, min(i, len(self.shots) - 1))

    def layers(self, t):
        """Liste [(plan, poids, rôle, p)] visibles à t (1 ou 2 plans)."""
        i = self.shot_index(t)
        s = self.shots[i]
        if i > 0 and t < s["start"] + s["trans"]["dur"] / 2:
            return self._trans(self.shots[i - 1], s, t)
        if i + 1 < len(self.shots):
            nx = self.shots[i + 1]
            if t >= nx["start"] - nx["trans"]["dur"] / 2:
                return self._trans(s, nx, t)
        return [(s, 1.0, None, 0.0)]

    @staticmethod
    def _trans(a, b, t):
        d = b["trans"]["dur"]
        typ = b["trans"]["type"]
        p = clamp((t - (b["start"] - d / 2)) / d)
        if typ == "zoom":
            half = d / 2
            if t < b["start"]:
                pa = clamp((t - (b["start"] - half)) / half)
                w = clamp((t - (b["start"] - 0.05)) / 0.1)
                out = [(a, 1 - w, "zoom_out", pa)]
                if w > 0:
                    out.append((b, w, "zoom_in", 0.0))
                return out
            pb = clamp((t - b["start"]) / half)
            w = clamp((t - (b["start"] - 0.05)) / 0.1)
            out = [(b, w, "zoom_in", pb)]
            if w < 1:
                out.append((a, 1 - w, "zoom_out", 1.0))
            return out
        w = p * p * (3 - 2 * p)
        return [(a, 1 - w, typ + ":out", p), (b, w, typ + ":in", p)]

    def fx_params(self, lays):
        keys = ("particles", "leaks", "bloom", "rays")
        out = {k: sum(s["fx"][k] * w for s, w, _, _ in lays) for k in keys}
        out["ptint"] = max(lays, key=lambda x: x[1])[0]["fx"]["ptint"]
        return out

    def frame(self, t):
        if self.enchant:
            return self.enchant.frame(t)
        lays = self.layers(t)
        img = None
        for s, w, role, p in lays:
            if w <= 0.001:
                continue
            layer = self.render_shot(s, t, role, p)
            img = layer * w if img is None else img + layer * w
        prm = self.fx_params(lays)
        cur = self.shots[self.shot_index(t)]

        # lumière de transition (« light ») : montée chaude et douce, jamais un flash blanc
        boost = 0.0
        for s, w, role, p in lays:
            if role and role.split(":")[0] == "light":
                boost = max(boost, 0.20 * math.sin(math.pi * p))
        for ev in self.events:
            if ev["type"] == "flash" and 0 <= t - ev["t"] < 1.2:
                boost += ev["strength"] * math.exp(-(t - ev["t"]) / ev["decay"])
        leaks = prm["leaks"]
        if cur.get("reveal"):
            leaks += 0.55 * (1 - clamp((t - cur["start"]) / 5.0))
        if boost > 0:
            img = img * (1 + boost * np.float32([1.0, 0.9, 0.72]))
            leaks += boost * 0.8

        L = fx.light_leaks(t, leaks)
        if L is not None:
            img = fx.screen(img, L)
        R = fx.god_rays(t, prm["rays"])
        if R is not None:
            img = fx.screen(img, R)
        img = fx.bloom(img, prm["bloom"])
        for ev in self.events:
            if ev["type"] == "flare":
                img = fx.flare(img, t, ev)
        img *= self.vignette
        self.particles.draw(img, t, prm["particles"], prm["ptint"])
        img = np.clip(img, 0, 1)
        for tb in self.texts:
            tb.draw(img, t)

        # fondus au noir (ouverture de l'intro, fin du film)
        g = 1.0
        if cur.get("fade_in"):
            g *= EASE["inOutSine"](clamp((t - cur["start"]) / cur["fade_in"]))
        if cur.get("fade_out"):
            g *= 1 - EASE["inOutSine"](clamp((t - (cur["end"] - cur["fade_out"])) / cur["fade_out"]))
        if g < 1:
            img *= g
        img += self.grain[int(t * FPS) // 2 % len(self.grain)] * (0.35 + 0.65 * g)
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

    # ------------------------------------------------------------------ contrôle qualité des textes
    def qc_texts(self):
        report = []
        for tb in self.texts:
            x0, y0, x1, y1 = tb.bbox
            issues = []
            if x0 < SAFE[0] or x1 > SAFE[2] or y0 < SAFE[1] or y1 > SAFE[3]:
                issues.append(f"hors zone de sécurité {SAFE} : bbox {[int(v) for v in tb.bbox]}")
            for t in np.linspace(tb.start + 0.05, tb.end - 0.05, 7):
                for s, w, role, p in self.layers(t):
                    if w < 0.25 or s.get("layout") == "bands":
                        continue
                    z, c, a = self.camera(s, t, role, p)
                    ph = self.photos[s["photo"]]
                    from photos import place
                    sc, tx, ty, _, _ = place(ph.w, ph.h, W, H, z, c, a)
                    for name, (bx0, by0, bx1, by1) in ph.protected_boxes((sc, tx, ty)).items():
                        ix = min(x1, bx1) - max(x0, bx0)
                        iy = min(y1, by1) - max(y0, by0)
                        if ix > 4 and iy > 4:
                            issues.append(f"t={t:.2f} recouvre {s['photo']}:{name} ({int(ix)}x{int(iy)} px)")
            report.append((tb.id, tb.cfg["lines"][0]["text"], tb.start, tb.end, sorted(set(issues))))
        return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--range", nargs=2, type=int)
    ap.add_argument("--out")
    ap.add_argument("--qc", action="store_true")
    ap.add_argument("--dir", default="work/stills")
    ap.add_argument("--style", help="variante de style (ex. enchante : config/style_enchante.json)")
    args = ap.parse_args()
    r = Renderer(args.style)
    if args.qc:
        bad = 0
        for tid, txt, a, b, issues in r.qc_texts():
            status = "OK" if not issues else "À VÉRIFIER"
            bad += bool(issues)
            print(f"{tid} [{tc(a)}–{tc(b)}] « {txt.replace('|', '')} » : {status}")
            for i in issues:
                print("    -", i)
        print(f"{bad} bloc(s) de texte à vérifier")
        return
    if args.stills is not None:
        out = ROOT / args.dir
        out.mkdir(parents=True, exist_ok=True)
        for t in args.stills:
            f = r.frame(t)
            cv2.imwrite(str(out / f"t{t:07.2f}.jpg"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
            print("écrit", out / f"t{t:07.2f}.jpg", flush=True)
        return
    if args.range:
        cv2.setNumThreads(1)          # un cœur par segment : les segments tournent en parallèle
        a, b = args.range
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-qp", "0",
               "-preset", "ultrafast", "-pix_fmt", "yuv444p", "-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-color_range", "tv", str(ROOT / args.out)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for fi in range(a, b):
            proc.stdin.write(r.frame(fi / FPS).tobytes())
            if (fi - a) % 150 == 0:
                print(f"[{a}-{b}] image {fi}", file=sys.stderr, flush=True)
        proc.stdin.close()
        sys.exit(proc.wait())


if __name__ == "__main__":
    main()
