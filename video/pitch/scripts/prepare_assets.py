"""Prepare production assets for the pitch video.

Usage:
  python3 -I scripts/prepare_assets.py --portrait <img> --logo <img-on-black> \
      --photos <dir> --music <mp3> [--music-alt <mp3>] --out assets

- portrait  -> assets/portrait.jpg (original) + assets/portrait_cutout.png (rembg u2net_human_seg)
- logo      -> assets/logo.png (gold on transparent; alpha recovered from the black background)
               assets/logo_monogram.png (DK monogram only)
- photos    -> assets/field/<name>.jpg (auto-oriented, HEIC supported, long edge 2400 px)
- music     -> assets/music.mp3 (first 100 s, 48 kHz, 192 kbps) + assets/beats.json
"""
import argparse, json, os, subprocess
import numpy as np
from PIL import Image, ImageOps

SELECTED = ["IMG_2110", "IMG_2065", "IMG_3341", "IMG_4598", "IMG_3338", "IMG_2995", "IMG_2082"]


def unpremultiply_on_black(im: Image.Image) -> Image.Image:
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    alpha = a.max(axis=2)
    alpha = np.clip((alpha - 0.02) / 0.98, 0, 1)  # kill the near-black noise floor
    rgb = np.where(alpha[..., None] > 1e-3, a / np.maximum(alpha[..., None], 1e-3), 0)
    out = np.dstack([np.clip(rgb, 0, 1), alpha]) * 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--portrait"); p.add_argument("--logo"); p.add_argument("--photos")
    p.add_argument("--music"); p.add_argument("--music-alt"); p.add_argument("--out", default="assets")
    args = p.parse_args()
    out = args.out
    os.makedirs(os.path.join(out, "field"), exist_ok=True)

    if args.portrait:
        im = ImageOps.exif_transpose(Image.open(args.portrait)).convert("RGB")
        im.save(os.path.join(out, "portrait.jpg"), quality=95)
        from rembg import remove, new_session
        cut = remove(im, session=new_session("u2net_human_seg"), alpha_matting=True,
                     alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15,
                     alpha_matting_erode_size=8)
        cut.save(os.path.join(out, "portrait_cutout.png"))

    if args.logo:
        logo = unpremultiply_on_black(Image.open(args.logo))
        bbox = logo.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        logo.crop(bbox).save(os.path.join(out, "logo.png"))
        w, h = logo.size  # monogram sits in the upper ~55 % of the square logo
        mono = logo.crop((0, 0, w, int(h * 0.56)))
        mb = mono.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        mono.crop(mb).save(os.path.join(out, "logo_monogram.png"))

    if args.photos:
        import pillow_heif
        pillow_heif.register_heif_opener()
        for f in sorted(os.listdir(args.photos)):
            name = os.path.splitext(f)[0]
            if name not in SELECTED:
                continue
            im = ImageOps.exif_transpose(Image.open(os.path.join(args.photos, f))).convert("RGB")
            im.thumbnail((2400, 2400), Image.LANCZOS)
            im.save(os.path.join(out, "field", name + ".jpg"), quality=86, optimize=True)

    for src, dst in ((args.music, "music.mp3"), (args.music_alt, "music_alt.mp3")):
        if src:
            subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-t", "100",
                            "-ar", "48000", "-b:a", "192k", os.path.join(out, dst)], check=True)
    if args.music:
        import librosa
        y, sr = librosa.load(os.path.join(out, "music.mp3"), sr=22050, mono=True)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        bt = librosa.frames_to_time(beats, sr=sr)
        json.dump({"bpm": float(np.atleast_1d(tempo)[0]), "beats": [round(float(t), 3) for t in bt]},
                  open(os.path.join(out, "beats.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
