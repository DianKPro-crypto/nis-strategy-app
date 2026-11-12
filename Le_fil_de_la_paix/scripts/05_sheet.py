"""Planche de controle a partir d'un dossier d'images (frames) : python3 scripts/05_sheet.py <dossier> <sortie_prefixe> [colonnes] [largeur]"""
import sys, glob, re, cv2, numpy as np
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 7; tw = int(sys.argv[4]) if len(sys.argv) > 4 else 270
fs = sorted(glob.glob(d + '/frame-*.png') + glob.glob(d + '/f_*.jpg'))
per = cols * 2
for s in range(0, len(fs), per):
    cells = []
    for f in fs[s:s + per]:
        im = cv2.imread(f); th = int(im.shape[0] * tw / im.shape[1]); im = cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
        m = re.search(r'at-([\d.]+)s|f_([\d.]+)', f); lab = (m.group(1) or m.group(2)) + ' s'
        bar = np.full((34, tw, 3), 20, np.uint8); cv2.putText(bar, lab, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 235, 244), 1, cv2.LINE_AA)
        cells.append(np.vstack([im, bar]))
    while len(cells) % cols: cells.append(np.full_like(cells[0], 12))
    rows = [np.hstack(cells[i:i + cols]) for i in range(0, len(cells), cols)]
    cv2.imwrite(f'{out}_{s // per + 1}.jpg', np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
