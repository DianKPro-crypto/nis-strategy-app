"""Extrait les 12 vignettes de la planche (sans bordures), efface les numeros par retouche locale."""
import cv2, numpy as np, sys, os
src = cv2.imread('sources/b.png'); H, W = src.shape[:2]
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
cream = ((hsv[..., 2] > 225) & (hsv[..., 1] < 40)).astype(np.float32)
def bands(profile, thr=0.9):
    on = profile < thr; out = []; s = None
    for i, v in enumerate(on):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s > 60: out.append((s, i))
            s = None
    if s is not None and len(on) - s > 60: out.append((s, len(on)))
    return out
cols = bands(cream.mean(0)); rows = bands(cream.mean(1))
print('cols', cols, 'rows', rows)
assert len(cols) == 3 and len(rows) == 4
n = 0
for (y0, y1) in rows:
    for (x0, x1) in cols:
        n += 1; m = 3
        v = src[y0 + m:y1 - m, x0 + m:x1 - m].copy()
        # numero : texte clair en haut a gauche -> masque puis inpainting
        roi = v[0:40, 0:52]; g = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = np.zeros(v.shape[:2], np.uint8)
        mk = ((g[..., 2] > 200) & (g[..., 1] < 70)).astype(np.uint8) * 255
        mk = cv2.dilate(mk, np.ones((5, 5), np.uint8))
        mask[0:40, 0:52] = mk
        v = cv2.inpaint(v, mask, 4, cv2.INPAINT_TELEA)
        cv2.imwrite(f'work/vig/v{n:02d}.png', v); print(n, v.shape)
