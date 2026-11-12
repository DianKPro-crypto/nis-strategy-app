"""Genere le projet HyperFrames 9:16 (index.html + compositions/sNN.html), Storyboard_final.csv,
Coupes_audio.csv et le SRT, a partir de la liste de plans ci-dessous.
Calage des paroles : alignement Suno du morceau (b6c27201), au niveau du vers / segment chante.
Usage : python3 scripts/04_build.py"""
import csv, html, json, os
import cv2

W, H = 1080, 1920
DUR = 197.6            # duree du film (audio source : 197.592 s, aucune coupe)
PANEL_H = 1300         # hauteur du cadre image dans la mise en page « refrain »
IVORY, GOLD, BLACK = '#F4EBDD', '#E3B34C', '#0B0B0C'

SIZES = {}
for n in ['hero'] + [f'v{i:02d}' for i in range(1, 13)]:
    im = cv2.imread(f'assets/img/{n}.jpg'); SIZES[n] = (im.shape[1], im.shape[0])

# ---------------------------------------------------------------- paroles (segments chantes, secondes)
L = {
 'i1': [("Ya Allah…", 4.16, 5.45)],
 'i2': [("Entre mes *mains*,", 11.35, 12.80)],
 'i3': [("Un *fil* demeure…", 16.27, 17.97)],
 'i4': [("Apaise mon *cœur*.", 21.20, 22.44)],
 'a1': [("J’avais gardé chaque mot comme une *pierre*,", 28.40, 31.07)],
 'a2': [("Chaque silence avait pris ton visage.", 33.24, 35.91)],
 'a3': [("Je demandais la paix dans mes prières,", 38.11, 40.84)],
 'a4': [("Mais ma colère habitait mon *langage*.", 43.08, 46.15)],
 'a5': [("Puis j’ai revu mes propres *maladresses*,", 47.91, 50.85)],
 'a6': [("Ces mots trop lourds que je croyais légers.", 52.73, 55.37)],
 'a7': [("Sous nos armures, il reste une *tendresse*,", 57.59, 60.67)],
 'a8': [("Un peu de nous qui voudrait *réparer*.", 62.59, 65.09)],
 'c1': [("Un fil de *paix*, un fil d’*amour*,", 66.50, 68.90)],
 'c2': [("*Recoud* nos cœurs, jour après jour.", 71.27, 73.73)],
 'c3': [("Ya Allah, apprends-moi la *douceur*,", 75.03, 78.67)],
 'c4': [("Que mes deux mains suivent enfin mon *cœur*.", 79.95, 83.49)],
 'c5': [("Un fil de paix, même *fragile*,", 84.68, 87.35)],
 'c6': [("Peut rapprocher nos deux *rives*.", 89.81, 92.26)],
 'c7': [("Je fais un *pas*,", 94.59, 95.69), ("sans tout savoir,", 97.00, 98.23)],
 'c8': [("Je laisse à l’amour un peu d’*espoir*.", 99.31, 101.90)],
 'b1': [("Je ne te veux ni sans faille ni sans *ombre*,", 104.18, 107.07)],
 'b2': [("Je viens vers toi *tel que je suis* aussi.", 109.07, 111.78)],
 'b3': [("Nous avons tous nos saisons les plus sombres,", 114.05, 117.97)],
 'b4': [("Et des regrets qui nous tiennent éveillés.", 118.00, 121.47)],
 'b5': [("J’ai déposé ma *colère* sur la table,", 123.04, 125.35)],
 'b6': [("Cherché les mots qui ne blesseraient pas.", 125.46, 127.66)],
 'b7': [("Un simple pardon, une voix plus calme,", 127.99, 130.24)],
 'b8': [("Et le *courage* de rester là.", 130.26, 132.48)],
 'p1': [("Je peux nommer ce qui m’a fait souffrir,", 132.67, 135.02),
        ("sans *condamner* tout ce que tu peux être.", 135.04, 137.57)],
 'p2': [("Je tends la main,", 137.57, 138.58), ("je te laisse *choisir*.", 138.58, 139.91)],
 'p3': [("La paix demande du temps pour renaître.", 140.05, 142.30)],
 'f1': [("Un fil de *paix*, un fil d’*amour*,", 142.56, 144.91)],
 'f2': [("*Recoud* nos cœurs, jour après jour.", 147.34, 149.80)],
 'f3': [("Ya Allah, apprends-nous la *douceur*,", 151.10, 154.74)],
 'f4': [("Que nos deux mains suivent enfin nos *cœurs*.", 156.00, 159.65)],
 'f5': [("Un fil de paix, même *fragile*,", 160.81, 163.42)],
 'f6': [("Peut rapprocher nos deux *rives*.", 165.82, 169.37)],
 'f7': [("Nous faisons un *pas*,", 170.44, 171.84), ("sans tout savoir,", 173.08, 174.50)],
 'f8': [("Nous laissons à l’amour un peu d’*espoir*.", 175.38, 178.05)],
 'o1': [("Ya Allah…", 184.21, 185.92)], 'o2': [("Le fil demeure…", 186.63, 188.06)],
 'o3': [("Entre nos mains,", 188.91, 190.38)], 'o4': [("La paix prend cœur.", 191.60, 193.40)],
}

# ---------------------------------------------------------------- plans
# rect = (cx, cy, h) en fractions de l'image : centre et hauteur de la zone cadree (debut -> fin)
def S(t0, t1, mode, img, r0, r1, lyric=None, note='', img2=None, r2=None, r3=None, fade=0, desc=''):
    return dict(t0=t0, t1=t1, mode=mode, img=img, r0=r0, r1=r1, lyric=lyric, note=note,
                img2=img2, r2=r2, r3=r3, fade=fade, desc=desc)

SEQ = [
 ('s01', 'La présence', 0.0, [
   S(0.0, 6.4, 'full', 'hero', (.49, .50, 1.0), (.49, .47, .84), desc='Plan moyen, lent rapprochement ; page de garde'),
   S(6.4, 11.2, 'full', 'hero', (.485, .26, .52), (.485, .25, .47), desc='Portrait, regard hors champ'),
   S(11.2, 16.1, 'full', 'hero', (.49, .78, .44), (.49, .79, .41), 'i2', desc='Détail des mains réunies'),
   S(16.1, 21.0, 'full', 'hero', (.48, .50, .46), (.48, .57, .46), 'i3', desc='Broderies du boubou, descente lente'),
   S(21.0, 28.25, 'full', 'v02', (.43, .5, 1.0), (.43, .55, .9), 'i4', desc='Portrait rapproché'),
 ]),
 ('s02', 'Les mots restés en soi', 28.25, [
   S(28.25, 33.1, 'full', 'v02', (.44, .60, .80), (.45, .62, .76), 'a1', desc='Détail du regard'),
   S(33.1, 38.0, 'full', 'hero', (.485, .27, .40), (.485, .26, .37), desc='Trois-quarts, silence'),
   S(38.0, 42.9, 'full', 'hero', (.50, .45, .80), (.48, .43, .74), desc='Plan taille dans la cour'),
   S(42.9, 47.8, 'full', 'v02', (.42, .57, .86), (.42, .54, .92), 'a4', desc='Portrait, léger recul'),
 ]),
 ('s03', 'Le poids du silence', 47.8, [
   S(47.8, 52.6, 'full', 'v03', (.47, .60, .80), (.47, .62, .75), 'a5', desc='Mains réunies et broderies'),
   S(52.6, 57.45, 'full', 'hero', (.485, .30, .50), (.485, .28, .46), desc='Retour au visage'),
   S(57.45, 62.4, 'full', 'v03', (.50, .40, .80), (.48, .58, .80), 'a7', desc='Des broderies vers les mains'),
   S(62.4, 66.35, 'fullwide', 'v04', (.55, .66, .64), (.57, .68, .58), 'a8', desc='Raccord : l’étoffe à la couture défaite'),
 ]),
 ('s04', 'Ce qui peut être réparé', 66.35, [
   S(66.35, 71.1, 'panel', 'v04', (.47, .5, 1.0), (.47, .5, .94), 'c1', desc='Assis devant l’étoffe ; cadre élargi au refrain'),
   S(71.1, 74.9, 'panel', 'v04', (.58, .70, .58), (.60, .71, .54), 'c2', desc='Détail de la couture défaite'),
   S(74.9, 79.8, 'panel', 'v04', (.47, .34, .66), (.47, .33, .60), 'c3', desc='Portrait'),
   S(79.8, 84.55, 'panel', 'v04', (.40, .66, .66), (.62, .66, .66), 'c4', desc='Les deux mains sur l’étoffe, panoramique'),
 ]),
 ('s05', 'La place de l’autre', 84.55, [
   S(84.55, 89.65, 'panel', 'v05', (.30, .5, 1.0), (.32, .5, .95), 'c5', desc='Son regard vers la chaise'),
   S(89.65, 94.45, 'duo', 'v05', (.28, .40, .66), (.30, .40, .64), 'c6', img2='v05', r2=(.80, .62, .66), r3=(.78, .62, .64),
     desc='Diptyque vertical : lui / la chaise vide'),
 ]),
 ('s06', 'Le premier geste', 94.45, [
   S(94.45, 99.15, 'panel', 'v06', (.50, .5, 1.0), (.50, .52, .94), 'c7', desc='Il pose la bobine de fil'),
   S(99.15, 104.0, 'panel', 'v06', (.62, .70, .62), (.63, .70, .60), 'c8', desc='Bobine et couture défaite, plan presque fixe'),
 ]),
 ('s07', 'L’invitation', 104.0, [
   S(104.0, 108.9, 'full', 'v07', (.21, .5, 1.0), (.215, .48, .92), 'b1', desc='Arrivée du second homme'),
   S(108.9, 113.9, 'full', 'v07', (.76, .5, 1.0), (.74, .5, .95), 'b2', desc='La main ouverte'),
   S(113.9, 118.0, 'fullwide', 'v07', (.5, .5, 1.0), (.5, .5, .96), 'b3', desc='Les deux hommes dans la cour'),
   S(118.0, 122.9, 'full', 'v08', (.79, .5, 1.0), (.78, .48, .92), desc='Le second homme assis, regard'),
 ]),
 ('s08', 'L’écoute', 122.9, [
   S(122.9, 127.85, 'panel', 'v08', (.23, .5, 1.0), (.23, .48, .93), 'b5', desc='Champ : il parle'),
   S(127.85, 132.55, 'duo', 'v08', (.21, .36, .66), (.22, .36, .63), 'b8', img2='v08', r2=(.78, .36, .66), r3=(.77, .36, .63),
     desc='Diptyque : champ / contrechamp'),
   S(132.55, 137.45, 'wide', 'v08', (.5, .5, 1.0), (.5, .5, .96), 'p1', desc='Plan à deux, même hauteur'),
 ]),
 ('s09', 'Le choix de la paix', 137.45, [
   S(137.45, 142.45, 'panel', 'v09', (.66, .5, 1.0), (.65, .53, .93), 'p2', desc='Sa main se pose sur l’étoffe'),
   S(142.45, 147.2, 'panel', 'v08', (.22, .34, .66), (.22, .33, .61), 'f1', desc='Réaction du personnage principal ; respiration'),
 ]),
 ('s10', 'La réparation', 147.2, [
   S(147.2, 152.6, 'panel', 'v10', (.60, .68, .64), (.62, .69, .60), 'f2', fade=0.7, desc='Ellipse : la couture réparée'),
   S(152.6, 155.9, 'panel', 'v10', (.43, .36, .68), (.43, .35, .64), 'f3', desc='Son visage'),
   S(155.9, 160.7, 'panel', 'v10', (.46, .5, 1.0), (.47, .5, .94), 'f4', desc='La main posée sur l’étoffe réparée'),
 ]),
 ('s11', 'Le lien retrouvé', 160.7, [
   S(160.7, 165.7, 'wide', 'v11', (.5, .5, 1.0), (.5, .5, .96), 'f5', desc='Ils tiennent ensemble l’étoffe pliée'),
   S(165.7, 170.3, 'duo', 'v11', (.24, .34, .58), (.25, .34, .56), 'f6', img2='v11', r2=(.77, .30, .58), r3=(.76, .30, .56),
     desc='Diptyque : échange de regards'),
   S(170.3, 175.25, 'panel', 'v11', (.53, .70, .60), (.53, .71, .56), 'f7', desc='Détail de l’étoffe et des mains'),
   S(175.25, 179.6, 'panel', 'v11', (.37, .37, .72), (.37, .36, .68), 'f8', desc='Son visage, sourire discret'),
   S(179.6, 184.0, 'wide', 'v11', (.5, .5, .96), (.5, .5, .90), desc='Plan à deux, lumière chaude'),
 ]),
 ('s12', 'L’apaisement', 184.0, [
   S(184.0, DUR, 'panel', 'v12', (.43, .5, 1.0), (.43, .5, .90), desc='Portrait final, rapprochement puis immobilité', note='final'),
 ]),
]

# un point de couture par vers chante dans la mise en page « refrain »
STITCH_KEYS = ['c1','c2','c3','c4','c5','c6','c7','c7b','c8','b5','b6','b7','b8','p1','p1b','p2','p2b','p3',
               'f1','f2','f3','f4','f5','f6','f7','f7b','f8']
def stitch_times():
    out = []
    for k in STITCH_KEYS:
        segs = L[k.rstrip('b')] if k.endswith('b') and k[:-1] in L else L[k]
        out.append(segs[1][1] if k.endswith('b') and k[:-1] in L else segs[0][1])
    return out
STITCH_T = stitch_times()
NST = len(STITCH_T); SX0, SX1 = 70, 1010
SPITCH = (SX1 - SX0) / NST; SLEN = SPITCH * 0.62

# ---------------------------------------------------------------- outils
def rect_tf(img, r, bw, bh):
    iw, ih = SIZES[img]; cx, cy, hf = r
    h = min(hf * ih, ih); w = h * bw / bh
    if w > iw: w = iw; h = w * bh / bw
    cx = min(max(cx * iw, w / 2), iw - w / 2); cy = min(max(cy * ih, h / 2), ih - h / 2)
    s = bh / h
    return dict(x=round(bw / 2 - cx * s, 2), y=round(bh / 2 - cy * s, 2), scale=round(s, 5))

def words_html(pid, segs, t_off):
    """Retourne (html, tweens) : chaque mot apparait a son instant chante (interpole dans le segment)."""
    parts, tw, k = [], [], 0
    for text, a, b in segs:
        ws = text.split(' '); tot = sum(len(w.strip('*')) + 1 for w in ws); acc = 0
        gold = False
        for w in ws:
            g = gold or w.startswith('*')
            if w.startswith('*'): gold = True
            if w.rstrip(',.…').endswith('*'): gold = False
            clean = w.replace('*', '')
            t = a + (b - a) * acc / tot - 0.06
            acc += len(clean) + 1; k += 1
            wid = f'{pid}-w{k}'
            parts.append(f'<span id="{wid}" class="w{" g" if g else ""}">{html.escape(clean)}</span>')
            tw.append((wid, round(max(t - t_off, 0.02), 3)))
    return ' '.join(parts), tw

CSS = f"""
#root {{ position:absolute; inset:0; background:{BLACK}; overflow:hidden; font-family:'Playfair Display',serif; color:{IVORY}; }}
.shot {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; }}
.fx {{ position:absolute; inset:0; }}
.box {{ position:absolute; left:0; overflow:hidden; width:{W}px; background:{BLACK}; }}
.box img {{ position:absolute; left:0; top:0; max-width:none; transform-origin:0 0; will-change:transform; }}
.bg {{ position:absolute; left:0; top:0; width:{W}px; height:{H}px; }}
.grad {{ position:absolute; left:0; right:0; bottom:0; height:760px;
  background:linear-gradient(to bottom, rgba(11,11,12,0) 0%, rgba(11,11,12,.34) 38%, rgba(11,11,12,.68) 70%, rgba(11,11,12,.8) 100%); }}
.ly {{ position:absolute; left:84px; width:912px; font-style:italic; font-weight:400; letter-spacing:.005em; }}
.ly.full {{ bottom:330px; font-size:74px; line-height:1.2; text-shadow:0 2px 22px rgba(11,11,12,.9), 0 0 6px rgba(11,11,12,.55); }}
.ly.pan {{ top:{PANEL_H + 74}px; font-size:64px; line-height:1.2; }}
.ly .w {{ display:inline-block; }}
.ly .g {{ color:{GOLD}; }}
.tick {{ position:absolute; left:84px; height:4px; width:132px; background:
  repeating-linear-gradient(to right, {GOLD} 0 30px, transparent 30px 44px); transform-origin:0 50%; }}
.seam {{ position:absolute; left:0; top:{PANEL_H - 3}px; width:{W}px; height:6px; }}
.st {{ position:absolute; top:0; height:6px; border-radius:3px; background:{GOLD}; transform-origin:0 50%; }}
.ground {{ position:absolute; left:0; top:{PANEL_H}px; width:{W}px; height:{H - PANEL_H}px; background:{BLACK}; }}
"""

def build_scene(sid, title, t0, shots, t1):
    hh, js = [], []
    z = 1
    uses_panel = any(s['mode'] in ('panel', 'duo', 'wide') for s in shots)
    for i, s in enumerate(shots, 1):
        pid = f'{sid}-p{i}'; a = round(s['t0'] - t0, 3); d = round(s['t1'] - s['t0'], 3)
        ext = 0.0
        nxt = shots[i] if i < len(shots) else None
        if nxt and nxt['fade']: ext = nxt['fade']
        mode = s['mode']; inner = []
        def img_layer(iid, img, r0, r1, bw, bh, top):
            f, t = rect_tf(img, r0, bw, bh), rect_tf(img, r1, bw, bh)
            iw, ih = SIZES[img]
            inner.append(f'<div class="box" data-layout-allow-overflow style="top:{top}px;height:{bh}px"><img id="{iid}" src="assets/img/{img}.jpg" '
                         f'width="{iw}" height="{ih}" style="width:{iw}px;height:{ih}px" alt=""></div>')
            dd = d + ext
            if s['note'] == 'final':
                js.append(f'tl.fromTo("#{iid}", {json.dumps(f)}, {{...{json.dumps(t)}, duration: 8.5, ease: "sine.inOut"}}, {a});')
            else:
                js.append(f'tl.fromTo("#{iid}", {json.dumps(f)}, {{...{json.dumps(t)}, duration: {round(dd,3)}, ease: "none"}}, {a});')
        if mode == 'full':
            img_layer(f'{pid}-i', s['img'], s['r0'], s['r1'], W, H, 0)
        elif mode == 'panel':
            img_layer(f'{pid}-i', s['img'], s['r0'], s['r1'], W, PANEL_H, 0)
        elif mode == 'duo':
            ph = (PANEL_H - 20) // 2
            img_layer(f'{pid}-i', s['img'], s['r0'], s['r1'], W, ph, 0)
            img_layer(f'{pid}-j', s['img2'], s['r2'], s['r3'], W, ph, ph + 20)
        elif mode in ('wide', 'fullwide'):
            bh = PANEL_H if mode == 'wide' else H
            inner.append(f'<div class="box" style="top:0;height:{bh}px"><img class="bg" src="assets/img/{s["img"]}_bg.jpg" alt=""></div>')
            sh = 608; top = (PANEL_H - sh) // 2 if mode == 'wide' else 560
            img_layer(f'{pid}-i', s['img'], s['r0'], s['r1'], W, sh, top)
        if mode in ('full', 'fullwide') and s['lyric']:
            inner.append('<div class="grad"></div>')
        if s['fade']:
            js.append(f'tl.fromTo("#{pid}-fx", {{opacity:0}}, {{opacity:1, duration:{s["fade"]}, ease:"sine.inOut"}}, {a});')
        hold = ' data-hold="true"' if s['note'] == 'final' else ''
        hh.append(f'<div id="{pid}" class="clip shot" data-start="{a}" data-duration="{round(d + ext,3)}" data-track-index="{i % 2 + 1}" '
                  f'style="z-index:{z}"{hold}><div id="{pid}-fx" class="fx">{"".join(inner)}</div></div>')
        z += 1
    if uses_panel:
        # sol noir + couture : presents sur les plans en mise en page « refrain »
        pans = [s for s in shots if s['mode'] in ('panel', 'duo', 'wide')]
        ga = round(pans[0]['t0'] - t0, 3); gd = round(pans[-1]['t1'] - pans[0]['t0'], 3)
        st = []
        for k, tt in enumerate(STITCH_T):
            if tt >= t1: break
            x = SX0 + k * SPITCH + (SPITCH - SLEN) / 2
            st.append(f'<i id="{sid}-st{k}" class="st" style="left:{x:.1f}px;width:{SLEN:.1f}px"></i>')
            if tt >= pans[0]['t0']:
                js.append(f'tl.fromTo("#{sid}-st{k}", {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:"power2.out"}}, {round(tt - t0, 3)});')
        hh.append(f'<div id="{sid}-ground" class="clip ground" data-start="{ga}" data-duration="{gd}" data-track-index="3" style="z-index:40" data-layout-ignore></div>')
        hh.append(f'<div id="{sid}-seam" class="clip seam" data-start="{ga}" data-duration="{gd}" data-track-index="4" style="z-index:41" data-layout-ignore>{"".join(st)}</div>')
    for i, s in enumerate(shots, 1):
        if not s['lyric']: continue
        pid = f'{sid}-l{i}'; segs = L[s['lyric']]
        a = round(max(segs[0][1] - 0.25, s['t0'] + 0.05) - t0, 3); e = round(s['t1'] - t0, 3)
        w, tw = words_html(pid, segs, t0)
        cls = 'full' if s['mode'] in ('full', 'fullwide') else 'pan'
        hh.append(f'<div id="{pid}" class="clip ly {cls}" data-start="{a}" data-duration="{round(e - a,3)}" data-track-index="5" style="z-index:50"><div id="{pid}-in">{w}</div></div>')
        for wid, t in tw:
            js.append(f'tl.fromTo("#{wid}", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.42, ease:"power2.out"}}, {t});')
        js.append(f'tl.fromTo("#{pid}-in", {{opacity:1}}, {{opacity:0, duration:0.28, ease:"power1.in"}}, {round(e - 0.3,3)});')
    return hh, js

TITLE_HTML = f"""
<div id="s01-cover" class="clip" data-start="0" data-duration="6.4" data-track-index="6" style="position:absolute;inset:0;z-index:60">
 <div id="s01-cover-in" style="position:absolute;inset:0">
  <div class="grad" style="height:900px"></div>
  <div id="s01-kicker" style="position:absolute;left:84px;top:1208px;font-family:Inter,sans-serif;font-weight:700;font-size:34px;letter-spacing:.3em;color:{GOLD}">CHANT SOUFI</div>
  <div id="s01-title" style="position:absolute;left:80px;top:1262px;font-weight:700;font-size:136px;line-height:1.02;letter-spacing:-.01em;color:{IVORY};text-shadow:0 3px 26px rgba(11,11,12,.7)">Le fil<br>de la paix</div>
  <div id="s01-thread" style="position:absolute;left:84px;top:1556px;width:560px;height:5px;transform-origin:0 50%;background:repeating-linear-gradient(to right,{GOLD} 0 34px,transparent 34px 50px)"></div>
  <div id="s01-by" style="position:absolute;left:84px;top:1580px;font-style:italic;font-size:42px;color:{IVORY}">Dian K. Pro</div>
 </div>
</div>"""
TITLE_JS = [
 'tl.fromTo("#s01-thread", {scaleX:0.12}, {scaleX:1, duration:2.6, ease:"power2.inOut"}, 0.3);',
 'tl.fromTo("#s01-cover-in", {opacity:1}, {opacity:0, duration:0.5, ease:"power1.in"}, 5.85);',
]
def end_html(t0):
    a = lambda t: round(t - t0, 3)
    h = f"""
<div id="s12-end" class="clip" data-start="{a(186.3)}" data-duration="{round(DUR-186.3,3)}" data-track-index="6" style="position:absolute;inset:0;z-index:60">
  <div id="s12-line" style="position:absolute;left:84px;top:{PANEL_H+70}px;width:912px;font-style:italic;font-size:62px;line-height:1.22;color:{IVORY}">
    <span id="s12-la" style="display:inline-block">La paix se tisse,</span><br><span id="s12-lb" style="display:inline-block">un geste après l’autre.</span></div>
  <div id="s12-thr" style="position:absolute;left:84px;top:{PANEL_H+262}px;width:300px;height:5px;transform-origin:0 50%;background:repeating-linear-gradient(to right,{GOLD} 0 34px,transparent 34px 50px)"></div>
  <div id="s12-sig" style="position:absolute;left:84px;top:{PANEL_H+282}px;font-weight:700;font-size:58px;color:{GOLD}">Dian K. Pro</div>
</div>
<div id="s12-black" class="clip" data-start="{a(196.5)}" data-duration="{round(DUR-196.5,3)}" data-track-index="7" style="position:absolute;inset:0;z-index:90" data-layout-ignore><div id="s12-black-in" style="position:absolute;inset:0;background:{BLACK}"></div></div>"""
    j = [
     f'tl.fromTo("#s12-la", {{opacity:0, y:18}}, {{opacity:1, y:0, duration:0.9, ease:"power2.out"}}, {a(186.5)});',
     f'tl.fromTo("#s12-lb", {{opacity:0, y:18}}, {{opacity:1, y:0, duration:0.9, ease:"power2.out"}}, {a(188.8)});',
     f'tl.fromTo("#s12-thr", {{scaleX:0}}, {{scaleX:1, duration:1.4, ease:"power2.inOut"}}, {a(191.0)});',
     f'tl.fromTo("#s12-sig", {{opacity:0}}, {{opacity:1, duration:1.0, ease:"power1.out"}}, {a(191.5)});',
     f'tl.fromTo("#s12-black-in", {{opacity:0}}, {{opacity:1, duration:0.85, ease:"sine.inOut"}}, {a(196.55)});',
    ]
    return h, j

os.makedirs('compositions', exist_ok=True)
hosts, rows = [], []
for n, (sid, title, t0, shots) in enumerate(SEQ):
    t1 = SEQ[n + 1][2] if n + 1 < len(SEQ) else DUR
    hh, js = build_scene(sid, title, t0, shots, t1)
    if sid == 's01': hh.append(TITLE_HTML); js += TITLE_JS
    if sid == 's12':
        eh, ej = end_html(t0); hh.append(eh); js += ej
    ext = 0.0
    if n + 1 < len(SEQ) and SEQ[n + 1][3][0]['fade']:   # fondu d'ellipse : la scene precedente reste dessous
        ext = SEQ[n + 1][3][0]['fade']
        last = shots[-1]; lid = f'{sid}-p{len(shots)}'
        hh = [x.replace(f'id="{lid}" class="clip shot" data-start="{round(last["t0"]-t0,3)}" data-duration="{round(last["t1"]-last["t0"],3)}"',
                        f'id="{lid}" class="clip shot" data-start="{round(last["t0"]-t0,3)}" data-duration="{round(last["t1"]-last["t0"]+ext,3)}"') for x in hh]
        hh = [x.replace(f'id="{sid}-ground" class="clip ground" data-start="0.0" data-duration="{round(t1-t0,3)}"',
                        f'id="{sid}-ground" class="clip ground" data-start="0.0" data-duration="{round(t1-t0+ext,3)}"')
               .replace(f'id="{sid}-seam" class="clip seam" data-start="0.0" data-duration="{round(t1-t0,3)}"',
                        f'id="{sid}-seam" class="clip seam" data-start="0.0" data-duration="{round(t1-t0+ext,3)}"') for x in hh]
    dur = round(t1 - t0 + ext, 3)
    open(f'compositions/{sid}.html', 'w').write(
        f'<template>\n<style>{CSS}</style>\n<div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">\n'
        + '\n'.join(hh) + '\n</div>\n<script>\n(function(){\nconst tl = gsap.timeline({ paused: true });\n' + '\n'.join(js)
        + f'\nwindow.__timelines["{sid}"] = tl;\n}})();\n</script>\n</template>\n')
    hosts.append(f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{t0}" '
                 f'data-duration="{dur}" data-track-index="{n % 2 + 1}" data-track-kind="graphics" data-width="{W}" data-height="{H}" '
                 f'style="z-index:{n + 1}"></div>')
    for i, s in enumerate(shots, 1):
        ly = ' / '.join(t.replace('*', '') for t, _, _ in L[s['lyric']]) if s['lyric'] else ''
        rows.append([sid[1:], title, i, f'{s["t0"]:.2f}', f'{s["t1"]:.2f}', f'{s["t1"]-s["t0"]:.2f}',
                     {'full': 'plein cadre', 'panel': 'cadre + texte', 'duo': 'diptyque', 'wide': 'plan large', 'fullwide': 'plan large'}[s['mode']],
                     s['img'] + ('' if not s['img2'] else '+' + s['img2']), s['desc'], ly,
                     'fondu 0,7 s' if s['fade'] else 'coupe franche'])

open('index.html', 'w').write(f"""<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: {BLACK}; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      {chr(10).join('      ' + h for h in hosts).strip()}
      <audio id="chant" class="clip" src="assets/audio/Le_fil_de_la_paix_audio_edit.wav" data-start="0" data-duration="{DUR}" data-track-index="9" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")

with open('Storyboard_final.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['sequence', 'titre', 'plan', 'debut_s', 'fin_s', 'duree_s', 'mise_en_page_9x16', 'image_source', 'description', 'paroles_a_l_ecran', 'transition_entree'])
    w.writerows(rows)
with open('Coupes_audio.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['operation', 'source_debut_s', 'source_fin_s', 'sortie_debut_s', 'sortie_fin_s', 'commentaire'])
    w.writerow(['conserve (aucune coupe)', '0.000', '197.592', '0.000', '197.592',
                'Le chant source dure 3 min 17,6 s : dans la cible 3 min - 3 min 30, fin musicale naturelle. Aucun raccord, aucune acceleration.'])
    w.writerow(['conversion', '', '', '', '', 'MP3 48 kHz stereo -> WAV PCM 16 bits 48 kHz, niveau inchange (-14,1 LUFS mesure).'])
def ts(t): ms = int(round(t * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
with open('Le_fil_de_la_paix_paroles.srt', 'w', encoding='utf-8') as f:
    n = 0
    for k, segs in L.items():
        n += 1; a, b = segs[0][1], segs[-1][2]
        f.write(f'{n}\n{ts(a)} --> {ts(b + 0.6)}\n{" ".join(t.replace("*", "") for t, _, _ in segs)}\n\n')
print('scenes', len(SEQ), 'plans', len(rows), 'points de couture', NST)
