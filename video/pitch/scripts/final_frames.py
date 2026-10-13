"""Sample frames from a rendered MP4 (one per scene, fully composed) into a sheet.
Usage: python3 -I scripts/final_frames.py out/Pitch-EN-16x9.mp4 previews/final_EN_16x9.jpg"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
times = [0.0, 13.0, 20.5, 37.0, 55.0, 67.0, 75.0, 85.5]  # cover, then the end state of each scene
tmp = tempfile.mkdtemp()
ims = []
for i, t in enumerate(times):
    p = os.path.join(tmp, f'{i}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', src, '-frames:v', '1', p], check=True)
    ims.append((t, Image.open(p).convert('RGB')))
w, h = ims[0][1].size
tw = 640 if w >= h else 300
th = int(tw * h / w)
cols = 4
sheet = Image.new('RGB', (cols * (tw + 8), 2 * (th + 26)), (40, 40, 40))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(ims):
    x, y = (i % cols) * (tw + 8), (i // cols) * (th + 26)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    d.text((x + 4, y + th + 6), f'{os.path.basename(src)} @ {t:.1f}s', fill=(230, 230, 230))
sheet.save(out, quality=88)
print(out)
