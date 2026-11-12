"""Agrandissement x4 local (Real-ESRGAN x4plus, CPU) des vignettes et de la photo originale.
Restauration de definition uniquement : aucun contenu nouveau, aucun service payant.
Usage : python3 scripts/02_upscale.py <poids RealESRGAN_x4plus.pth>"""
import sys, glob, os, cv2, numpy as np, torch
from spandrel import ModelLoader
torch.set_num_threads(4)
model = ModelLoader().load_from_file(sys.argv[1]).eval()
def up(img, tile=256, pad=16):
    h, w = img.shape[:2]; out = np.zeros((h * 4, w * 4, 3), np.float32)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            y0, x0 = max(y - pad, 0), max(x - pad, 0); y1, x1 = min(y + tile + pad, h), min(x + tile + pad, w)
            t = torch.from_numpy(img[y0:y1, x0:x1, ::-1].astype(np.float32) / 255).permute(2, 0, 1)[None]
            with torch.no_grad(): r = model(t)[0].clamp(0, 1).permute(1, 2, 0).numpy()[:, :, ::-1]
            ys, xs = (y - y0) * 4, (x - x0) * 4; hh, ww = (min(y + tile, h) - y) * 4, (min(x + tile, w) - x) * 4
            out[y * 4:y * 4 + hh, x * 4:x * 4 + ww] = r[ys:ys + hh, xs:xs + ww]
    return (out * 255).round().astype(np.uint8)
os.makedirs('work/up', exist_ok=True)
jobs = sorted(glob.glob('work/vig/v*.png')) + ['sources/a.png']
for f in jobs:
    o = 'work/up/' + ('hero.png' if f.endswith('a.png') else os.path.basename(f))
    if os.path.exists(o): continue
    r = up(cv2.imread(f))
    if 'hero' in o: r = cv2.resize(r, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)  # x2 final
    cv2.imwrite(o, r); print(o, r.shape, flush=True)
