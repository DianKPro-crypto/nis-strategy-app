# Dr. Dian SIDIBE — motion-design pitch video

An 86-second, text-led pitch film built in code with [Remotion](https://www.remotion.dev) (React + TypeScript, 30 fps).
It reads fully **without sound**: a muted viewer on a phone sees who Dr. Sidibé is, his three offers, the proof numbers and how to reach him.
The music is a Suno kora track supplied by Dr. Sidibé. The voice-over is optional; the script is ready to record.

**Brand:** DIAN K. PRO *Charte chromatique V1.0*: noir `#0A0A0A`, or `#D4A44C`, champagne `#ECBA5B`, or profond `#A87C33`; Playfair Display + Inter.

## Deliverables (`out/`)

| File | Format | Use |
|---|---|---|
| `Pitch-EN-16x9.mp4` | 1920×1080 | Master: website, conferences, YouTube, email |
| `Pitch-EN-1x1.mp4` | 1080×1080 | LinkedIn feed |
| `Pitch-EN-9x16.mp4` | 1080×1920 | LinkedIn mobile, WhatsApp Status, Reels |
| `Pitch-FR-16x9.mp4` | 1920×1080 | French master (francophone ministries, AFRO/EMRO) |
| `Pitch-FR-1x1.mp4` | 1080×1080 | French LinkedIn feed |
| `Pitch-FR-9x16.mp4` | 1080×1920 | French WhatsApp Status / Stories (bonus) |
| `thumbnail_en.png`, `thumbnail_fr.png` | 1920×1080 | Custom cover (portrait + headline) |
| `captions_en.srt`, `captions_fr.srt` | SRT | Sidecar captions of the voice-over, for upload |
| `vo_script_en.txt`, `vo_script_fr.txt` | text | Voice-over scripts with timed windows |
| `QA_REPORT.md` | markdown | Durations, sizes, loudness, fact check, reading times |

All MP4s use H.264 with `yuv420p` and `+faststart`. Audio is AAC at −14 LUFS integrated, ≤ −1 dBTP. Each file is ≤ 25 MB and ≤ 90 s, so it fits a single WhatsApp Status.

## Storyboard (86 s; scene cuts snap to the music's beat grid)

| # | Scene | What the viewer reads |
|---|---|---|
| 1 | Hook / cover | *What if the money was already there… and the strategy wasn't?* (complete on frame 0, so it doubles as the poster frame) |
| 2 | Bottleneck | No endorsed strategy / No costed plan / No funding cycle, each struck through by the gold thread. *And children wait.* |
| 3 | Reveal | Dr. Dian SIDIBE, MD · National Immunisation Strategy Architect · Casablanca · AFRO & EMRO |
| 4 | Proof | 28 years · 5 countries costed with NIS.COST (lit on the map) · 23 country offices · 15+ teams trained · 3 languages |
| 5 | Three offers | 01 Unlock financing · 02 Architect the strategy · 03 Build national ownership |
| 6 | Method | Djibouti NIS 2027–2030: 26 → 110 → 348 traced network · quality score 77.8 → 89.1 / 100 · *AI-accelerated. Human-validated. Fully traceable.* |
| 7 | Trust | Institutions served, shown as text wordmarks only (no logos) |
| 8 | Call to action | Strategies ministries own. Plans donors fund. Contacts + LinkedIn QR. DK monogram signature (≥ 3 s hold) |

## Render

```bash
npm ci
# If Remotion cannot download its own Chrome, point it at an installed one:
# export REMOTION_BROWSER_EXECUTABLE=/path/to/chrome-headless-shell
npx remotion studio                                   # live preview / edit
npx remotion render Pitch-EN-16x9 out/Pitch-EN-16x9.mp4   # one version, raw
scripts/render_all.sh                                 # all six + loudness + size control
npx remotion still Thumbnail-EN out/thumbnail_en.png
node scripts/make_captions.mjs out                    # SRT + VO scripts
node --experimental-strip-types scripts/qa.mjs out    # QA_REPORT.md
node scripts/stills.mjs Pitch-EN-1x1 previews         # start/mid/end stills per scene
```

`scripts/render_all.sh` encodes at CRF 20. If a file would exceed 24 MB, it falls back to a two-pass encode at 2.1 Mb/s. It runs a two-pass `loudnorm` to −14 LUFS / −1 dBTP.

## How to change things

All replaceable material lives in **`assets/`**, Remotion's public folder.

| To change… | Do this |
|---|---|
| **Music** | Run `python3 -I scripts/prepare_assets.py --music <new.mp3> --out assets`. This rewrites `assets/music.mp3` and `assets/beats.json`, and scene cuts re-snap to the new beat grid automatically. `assets/music_alt.mp3` (*mali-kora*) is a ready alternative: rename it to `music.mp3` and re-run the script on it to refresh the beats. |
| **Voice-over** | 1) Record from `out/vo_script_<lang>.txt`, staying inside each timed window. 2) Save it as `assets/vo_en.mp3` / `assets/vo_fr.mp3`. 3) Run `python3 -I scripts/vo_segments.py assets/vo_en.mp3` to list the speech segments, then nudge the scene starts in `src/timeline.json` and the windows in `src/vo.json` if needed. 4) Render with `--props='{"voiceover":true}'`. The music then ducks by −10 dB under the voice with 200 ms ramps. 5) Re-run `make_captions.mjs`. |
| **Portrait** | Run `prepare_assets.py --portrait <photo>`. It writes `portrait.jpg` and a background-removed `portrait_cutout.png` (rembg, `u2net_human_seg`). The arch frames from the head automatically. |
| **Field photos** | Add them to `prepare_assets.py` (`SELECTED`) or drop JPGs into `assets/field/`, then change the file names in `src/scenes/S2Bottleneck.tsx` (field), `S5Offers.tsx` (`PHOTOS`, one per offer) and `S7Trust.tsx`. Keep text off faces: the scenes use split layouts. |
| **Any wording / figure** | `src/copy.ts` (EN and FR). Layouts reflow; check with `scripts/stills.mjs`. |
| **Contacts / QR** | `assets/contact.json`. The QR code encodes `linkedinUrl`. |
| **Colours / fonts** | `assets/brand.json` (palette from the charter) and `assets/fonts/` (bundled, SIL OFL). |
| **Timing** | `src/timeline.json` (nominal scene starts, total length). Keep the total ≤ 90 s for WhatsApp Status. |

## Facts used (only these) and items to validate

On-screen figures come only from the approved fact sheet. `QA_REPORT.md` prints a diff table of every figure against it.

**Please confirm before publishing:**

1. **Djibouti NIS chain.** The brief says 26 objectives → **110 interventions → 348 activities**. The CV (Oct 2026) says 26 SMART objectives, **87 priority interventions, 216 activities**, from the July 2026 workshop. The video uses the brief's 110 / 348. If the CV figures are the validated ones, change `method.chain` in `src/copy.ts` and re-render.
2. **Years of experience.** The video says 28, consistent with a career starting in November 1998. The CV profile still says "25 years", so align the CV.
3. **Phone.** The video uses **+212 77 609 3831**, from the brief. The CV lists +212 770 74 28 74.
4. **LinkedIn.** `linkedin.com/in/dian-karim-sidibe`, taken from the CV. Scan the QR to confirm. No website was supplied, so none is shown.
5. **Institutions.** Gavi is not listed as an institution served, because its programmes were supported, not contracted. "Ministries of Health across Africa and the Middle East" was replaced by the six named ministries, which are all African; Djibouti sits in WHO EMRO.
6. **Map.** Land is drawn as one dot field **without internal borders**, which keeps it neutral on disputed boundaries. Only the five NIS.COST countries and Casablanca are marked.
7. **Photo consent.** Identifiable adults appear in the field and workshop photos. Consent is assumed because Dr. Sidibé supplied the photos; please confirm. No children are shown.
8. **Music rights.** Confirm the Suno tracks were generated on a paid Suno plan, which grants commercial-use rights.

**Photos excluded on purpose:** `8F7A2BAA….png` (screen showing WHO / UNICEF / Gavi / Ministry logos), `IMG_2086` (WHO emblem on a vest), `IMG_4469` (DHIS2/HISP laptop sticker), and `IMG_4651_enhanced` / `IMG_4686_enhanced` (look AI-processed; no AI imagery may be presented as real).

## Asset readiness (at build time)

| Asset | Status |
|---|---|
| Portrait | Supplied as 1122×1402 with a studio background. That is below the ≥ 2000 px recommendation but sharp enough at 1080p. Background removed with rembg; original kept. |
| Logo | Supplied as a 1254×1254 raster on black (no SVG). Transparency recovered from the black background → `logo.png`, `logo_monogram.png`. |
| Brand | Taken from the DIAN K. PRO *Charte chromatique V1.0* PDF → `brand.json`. It replaces the brief's default navy/teal palette. |
| Field photos | 17 supplied (14 HEIC, converted); 7 kept after screening; 5 used. |
| Music | 2 Suno kora tracks. *Relax Kora Mali* is used (its soft intro sits under the hook); *mali-kora* is the alternate. |
| Voice-over | Not supplied, so this is the text-led version. Timed scripts and SRTs are exported. |
| Contacts | Email and phone from the brief; LinkedIn from the CV; no website. |

## Project layout

```
assets/        drop folder: portrait, logo, field/, music, beats.json, brand.json, contact.json, fonts/
src/
  copy.ts      all on-screen text (EN / FR)        vo.json     voice-over blocks + windows
  timeline.*   beat-snapped scene cuts             theme.ts    brand tokens, easing
  components/  Thread, Counter, MapAfricaME, Network, Gauge, Icons, QR, Photo, Grain, Appear
  scenes/      S1Hook … S8CTA                      Pitch.tsx   assembly + music / VO
  Root.tsx     compositions: Pitch-{EN,FR}-{16x9,1x1,9x16}, Thumbnail-{EN,FR}
scripts/       prepare_assets.py, render_all.sh, stills.mjs, contact_sheet.py,
               make_captions.mjs, vo_segments.py, qa.mjs
```

Remotion is free for individuals and companies of up to three people (see remotion.dev/license). Playfair Display and Inter are under the SIL Open Font License.
