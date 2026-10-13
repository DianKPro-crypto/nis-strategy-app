"""List speech segments in a recorded voice-over (ffmpeg silencedetect) next to the
planned VO windows, so scene starts in src/timeline.json can be re-timed.
Usage: python3 -I scripts/vo_segments.py assets/vo_en.mp3 [noise_dB=-35] [min_silence_s=0.45]"""
import re, subprocess, sys

path = sys.argv[1]
noise = sys.argv[2] if len(sys.argv) > 2 else '-35'
dur = sys.argv[3] if len(sys.argv) > 3 else '0.45'
log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', f'silencedetect=n={noise}dB:d={dur}', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
total = float(re.search(r'Duration: (\d+):(\d+):([\d.]+)', log).groups()[2]) + 60 * float(re.search(r'Duration: (\d+):(\d+):', log).groups()[1])
speech, t = [], 0.0
for s, e in zip(starts, ends + [total]):
    if s - t > 0.2:
        speech.append((t, s))
    t = e
if total - t > 0.2:
    speech.append((t, total))
print(f'{len(speech)} speech segments in {path} ({total:.1f} s):')
for i, (a, b) in enumerate(speech, 1):
    print(f'  {i:2d}. {a:6.2f} s → {b:6.2f} s  ({b - a:4.1f} s)')
print('\nSet each scene "start" in src/timeline.json ~0.3 s before the first segment of its VO block (see out/vo_script_*.txt),')
print('update the matching startOffset/endOffset in src/vo.json, then re-render with --props=\'{"voiceover":true}\'.')
