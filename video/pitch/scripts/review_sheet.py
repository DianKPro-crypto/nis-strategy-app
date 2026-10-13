"""One contact sheet for every rendered version: a row per MP4, one frame per scene.
Usage: python3 -I scripts/review_sheet.py out out/contact_sheet.jpg"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
times = [0.0, 13.0, 20.5, 37.0, 55.0, 67.0, 75.0, 85.5]
labels = ['Cover', 'Bottleneck', 'Reveal', 'Proof', 'Offers', 'Method', 'Trust', 'CTA']
H, GAP, LBL = 300, 8, 34
files = sorted(glob.glob(os.path.join(src, 'Pitch-*.mp4')), key=lambda p: (['EN', 'FR'].index(p.split('-')[1]), ['16x9', '1x1', '9x16'].index(p.split('-')[2][:-4])))
tmp = tempfile.mkdtemp()
rows = []
for f in files:
    frames = []
    for i, t in enumerate(times):
        p = os.path.join(tmp, f'{os.path.basename(f)}_{i}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', f, '-frames:v', '1', p], check=True)
        im = Image.open(p).convert('RGB')
        frames.append(im.resize((round(im.width * H / im.height), H), Image.LANCZOS))
    rows.append((os.path.basename(f), frames))
W = max(sum(fr.width + GAP for fr in r[1]) for r in rows) + GAP
sheet = Image.new('RGB', (W, len(rows) * (H + LBL + GAP) + LBL + GAP), (28, 28, 28))
d = ImageDraw.Draw(sheet)
d.text((GAP, 10), 'Dr. Dian SIDIBE — pitch video · final renders · one frame per scene: ' + ' · '.join(labels), fill=(236, 186, 91))
y = LBL + GAP
for name, frames in rows:
    d.text((GAP, y + 8), name, fill=(230, 230, 230))
    x = GAP
    for fr in frames:
        sheet.paste(fr, (x, y + LBL - 6))
        x += fr.width + GAP
    y += H + LBL + GAP
sheet.save(out, quality=86)
print(out, sheet.size)
