"""Assemble QA stills into one contact sheet. Usage: python3 -I scripts/contact_sheet.py <dir> <prefix> <out.jpg> [thumb_w]"""
import glob, os, sys
from PIL import Image, ImageDraw

d, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 640
files = sorted(glob.glob(os.path.join(d, f"{prefix}_*.png")), key=lambda p: (int(os.path.basename(p).split('_')[1].split('-')[0]), ['start', 'mid', 'end'].index(p.rsplit('_', 1)[1][:-4])))
ims = [Image.open(f).convert('RGB') for f in files]
w, h = ims[0].size
th = int(tw * h / w)
cols = 3
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (tw + 10) + 10, rows * (th + 34) + 10), (40, 40, 40))
dr = ImageDraw.Draw(sheet)
for i, (f, im) in enumerate(zip(files, ims)):
    x = 10 + (i % cols) * (tw + 10)
    y = 10 + (i // cols) * (th + 34)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
    dr.text((x, y + th + 6), os.path.basename(f), fill=(230, 230, 230))
sheet.save(out, quality=88)
print(out, sheet.size)
