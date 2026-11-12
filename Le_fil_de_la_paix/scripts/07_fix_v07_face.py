"""Corrige le visage du second homme dans la vignette 07 (arrivee) : sa tete, illisible apres agrandissement,
est remplacee par celle de la vignette 08 (meme personnage, meilleure definition), retournee et raccordee.
Usage : python3 scripts/07_fix_v07_face.py [sx] [x] [y]   -> ecrit assets/img/v07.jpg (original garde dans work/v07_orig.jpg)"""
import cv2, numpy as np, os, sys, shutil
if not os.path.exists('work/v07_orig.jpg'): shutil.copy('assets/img/v07.jpg', 'work/v07_orig.jpg')
A = cv2.imread('work/v07_orig.jpg'); B = cv2.imread('assets/img/v08.jpg')
S = float(sys.argv[1]) if len(sys.argv) > 1 else 0.42
PX = int(sys.argv[2]) if len(sys.argv) > 2 else 364      # coin haut-gauche du collage dans v07
PY = int(sys.argv[3]) if len(sys.argv) > 3 else 58
# 1) detourage de la tete dans v08
x0, y0, x1, y1 = 1380, 0, 1800, 440
roi = B[y0:y1, x0:x1].copy(); m = np.zeros(roi.shape[:2], np.uint8)
bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
cv2.grabCut(roi, m, (40, 8, 330, 430), bg, fg, 6, cv2.GC_INIT_WITH_RECT)
mask = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
shirt = ((hsv[..., 2] > 150) & (hsv[..., 1] < 95)).astype(np.uint8) * 255      # chemise ecrue : exclue
mask[shirt > 0] = 0
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
mask = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
mask[395:, :] = 0
# 2) miroir + mise a l'echelle
roi, mask = roi[:, ::-1], mask[:, ::-1]
w, h = int(roi.shape[1] * S), int(roi.shape[0] * S)
roi = cv2.resize(roi, (w, h), interpolation=cv2.INTER_AREA); mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_AREA)
# 3) effacer l'ancienne tete : report d'un pan de mur voisin
out = A.copy().astype(np.float32)
hx0, hx1, hy0, hy1 = 356, 520, 30, 212
old = np.zeros(A.shape[:2], np.float32); cv2.ellipse(old, (438, 122), (74, 98), 0, 0, 360, 1, -1)
old = cv2.GaussianBlur(old, (0, 0), 7)[..., None]
wall = np.roll(A, -175, axis=1).astype(np.float32)          # mur situe 175 px a droite
out = out * (1 - old) + wall * old
# 4) accord colorimetrique sur la peau de v07 puis collage adouci
ref = A[150:200, 400:470].reshape(-1, 3).astype(np.float32).mean(0)          # joue / machoire d'origine
src = roi[mask > 200].astype(np.float32).mean(0)
roi = np.clip(roi.astype(np.float32) * (0.55 + 0.45 * ref / src), 0, 255)
al = cv2.GaussianBlur(cv2.erode(mask, np.ones((5, 5), np.uint8)), (0, 0), 1.3).astype(np.float32)[..., None] / 255
al[int(h * 0.80):] *= np.linspace(1, 0, h - int(h * 0.80))[:, None, None]      # fondu du cou vers le col
out[PY:PY + h, PX:PX + w] = out[PY:PY + h, PX:PX + w] * (1 - al) + roi * al
cv2.imwrite('assets/img/v07.jpg', out.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
cv2.imwrite('work/v07_fix_preview.jpg', np.hstack([A[0:520, 180:720], out.astype(np.uint8)[0:520, 180:720]]))
