"""Prepare les images du film : melange agrandissement IA (60 %) + Lanczos (40 %) pour garder un grain
photographique, rognage des bords, grain fin, fonds floutes pour les plans larges."""
import cv2, numpy as np, os
os.makedirs('assets/img', exist_ok=True)
rng = np.random.default_rng(7)
def finish(gan, base, trim):
    lz = cv2.resize(base, (gan.shape[1], gan.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    out = cv2.addWeighted(gan, 0.6, lz, 0.4, 0)[trim:-trim, trim:-trim].astype(np.float32)
    g = cv2.GaussianBlur(rng.normal(0, 3.2, out.shape[:2]).astype(np.float32), (0, 0), 0.8)
    return np.clip(out + g[..., None], 0, 255).astype(np.uint8)
def backdrop(img, name):
    h, w = img.shape[:2]; cw = int(h * 1080 / 1920)
    c = cv2.resize(img[:, (w - cw) // 2:(w + cw) // 2], (1080, 1920), interpolation=cv2.INTER_AREA)
    c = cv2.GaussianBlur(c, (0, 0), 38)
    cv2.imwrite(f'assets/img/{name}_bg.jpg', (c * 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
for n in range(1, 13):
    r = finish(cv2.imread(f'work/up/v{n:02d}.png'), cv2.imread(f'work/vig/v{n:02d}.png'), 10)
    cv2.imwrite(f'assets/img/v{n:02d}.jpg', r, [cv2.IMWRITE_JPEG_QUALITY, 93]); print(n, r.shape[1], r.shape[0])
    if n in (4, 7, 8, 11): backdrop(r, f'v{n:02d}')
r = finish(cv2.imread('work/up/hero.png'), cv2.imread('sources/a.png'), 6)
cv2.imwrite('assets/img/hero.jpg', r, [cv2.IMWRITE_JPEG_QUALITY, 93]); print('hero', r.shape[1], r.shape[0])
