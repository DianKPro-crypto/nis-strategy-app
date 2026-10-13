// Build captions_<lang>.srt and vo_script_<lang>.txt from src/vo.json + the
// beat-snapped timeline. Usage: node scripts/make_captions.mjs [outDir]
import fs from 'node:fs';
import path from 'node:path';
import {SCENES, FPS} from './timeline.mjs';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.resolve(root, process.argv[2] ?? 'out');
const vo = JSON.parse(fs.readFileSync(path.join(root, 'src/vo.json'), 'utf8'));
const scene = (id) => SCENES.find((s) => s.id === id);
const sec = (f) => f / FPS;
const MAX_LINE = 42;

const ts = (t) => {
  const ms = Math.round(t * 1000);
  const h = String(Math.floor(ms / 3600000)).padStart(2, '0');
  const m = String(Math.floor((ms % 3600000) / 60000)).padStart(2, '0');
  const s = String(Math.floor((ms % 60000) / 1000)).padStart(2, '0');
  return `${h}:${m}:${s},${String(ms % 1000).padStart(3, '0')}`;
};

const mmss = (t) => `${String(Math.floor(t / 60)).padStart(2, '0')}:${(t % 60).toFixed(1).padStart(4, '0')}`;

// Split a block into caption chunks of ≤ 2 lines × 42 characters, at sentence
// then clause boundaries.
const chunk = (text) => {
  const pieces = text.split(/(?<=[.?!…;:])\s+|(?<=,)\s+/);
  const out = [];
  let cur = '';
  for (const p of pieces) {
    const next = cur ? `${cur} ${p}` : p;
    if (next.length <= MAX_LINE * 2 - 4) cur = next;
    else {
      if (cur) out.push(cur);
      cur = p;
    }
  }
  if (cur) out.push(cur);
  return out;
};

const wrap = (t) => {
  if (t.length <= MAX_LINE) return t;
  const words = t.split(' ');
  let best = t;
  let bestScore = Infinity;
  for (let i = 1; i < words.length; i++) {
    const a = words.slice(0, i).join(' ');
    const b = words.slice(i).join(' ');
    if (a.length > MAX_LINE || b.length > MAX_LINE) continue;
    const score = Math.abs(a.length - b.length);
    if (score < bestScore) {
      bestScore = score;
      best = `${a}\n${b}`;
    }
  }
  return best;
};

fs.mkdirSync(outDir, {recursive: true});
for (const lang of ['en', 'fr']) {
  const cues = [];
  const script = [];
  for (const b of vo[lang]) {
    const s = scene(b.scene);
    const start = sec(s.from) + b.startOffset;
    let end;
    if (b.endScene) end = sec(scene(b.endScene).from) + b.endAt;
    else if (b.endAt !== undefined) end = sec(s.from) + b.endAt;
    else end = sec(s.from + s.duration) + b.endOffset;
    const words = b.text.split(/\s+/).length;
    script.push({start, end, words, text: b.text});
    const parts = chunk(b.text);
    const total = parts.reduce((n, p) => n + p.length, 0);
    let t = start;
    for (const p of parts) {
      const d = ((end - start) * p.length) / total;
      cues.push({start: t, end: t + d - 0.08, text: wrap(p)});
      t += d;
    }
  }
  const srt = cues.map((c, i) => `${i + 1}\n${ts(c.start)} --> ${ts(c.end)}\n${c.text}\n`).join('\n');
  fs.writeFileSync(path.join(outDir, `captions_${lang}.srt`), srt);
  const totalWords = script.reduce((n, s) => n + s.words, 0);
  const spoken = script.reduce((n, s) => n + (s.end - s.start), 0);
  const txt = [
    `VOICE-OVER SCRIPT (${lang.toUpperCase()}) — Dr. Dian SIDIBE pitch video`,
    `${totalWords} words · ${(totalWords / (spoken / 60)).toFixed(0)} wpm average within the timed windows`,
    'Record each block inside its window. Leave the Trust scene (music only) silent.',
    '',
    ...script.map((s) => `[${mmss(s.start)} → ${mmss(s.end)}] (${s.words} words, ${((s.words / (s.end - s.start)) * 60).toFixed(0)} wpm)\n${s.text}\n`),
  ].join('\n');
  fs.writeFileSync(path.join(outDir, `vo_script_${lang}.txt`), txt);
  console.log(lang, cues.length, 'cues,', totalWords, 'words');
}
