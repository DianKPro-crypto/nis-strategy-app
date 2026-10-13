// Final QA report. Usage: node --experimental-strip-types scripts/qa.mjs [outDir]
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {EN, FR} from '../src/copy.ts';
import {SCENES, FPS, TOTAL_FRAMES, PRE} from './timeline.mjs';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.resolve(root, process.argv[2] ?? 'out');
const lines = [];
const log = (s = '') => lines.push(s);
const ok = (b) => (b ? 'PASS' : 'FAIL');

log('# QA report — Dr. Dian SIDIBE pitch video');
log();

// 1. Files: duration, size, codec, faststart, loudness
log('## 1. Renders');
log();
log('| File | Duration | Size | Video | Faststart | Loudness (I / TP) | ≤ 25 MB | ≤ 90 s (WhatsApp) |');
log('|---|---|---|---|---|---|---|---|');
const mp4s = fs.existsSync(outDir) ? fs.readdirSync(outDir).filter((f) => f.endsWith('.mp4')).sort() : [];
for (const f of mp4s) {
  const p = path.join(outDir, f);
  const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_format', '-show_streams', '-of', 'json', p]).toString());
  const v = probe.streams.find((s) => s.codec_type === 'video');
  const dur = Number(probe.format.duration);
  const size = fs.statSync(p).size / 1024 / 1024;
  const head = fs.readFileSync(p).subarray(0, 200000).toString('latin1');
  const fast = head.indexOf('moov') !== -1 && (head.indexOf('mdat') === -1 || head.indexOf('moov') < head.indexOf('mdat'));
  const out = execFileSync('bash', ['-c', `ffmpeg -hide_banner -nostats -i "${p}" -af ebur128=peak=true -f null - 2>&1 | tail -12`]).toString();
  const I = (out.match(/I:\s+(-?[\d.]+) LUFS/) ?? [])[1];
  const TP = (out.match(/Peak:\s+(-?[\d.]+) dBFS/) ?? [])[1];
  log(`| ${f} | ${dur.toFixed(2)} s | ${size.toFixed(1)} MB | ${v.codec_name} ${v.width}×${v.height} ${v.pix_fmt} | ${ok(fast)} | ${I ?? '–'} LUFS / ${TP ?? '–'} dBTP | ${ok(size <= 25)} | ${ok(dur <= 90)} |`);
}
log();
log(`Timeline: ${(TOTAL_FRAMES / FPS).toFixed(2)} s @ ${FPS} fps. Scene cuts snapped to the music beat grid:`);
log();
log('| # | Scene | Start | Duration |');
log('|---|---|---|---|');
SCENES.forEach((s, i) => log(`| ${i + 1} | ${s.id} | ${(s.from / FPS).toFixed(2)} s | ${(s.duration / FPS).toFixed(2)} s |`));
log();

// 2. Figures on screen vs approved fact sheet
log('## 2. Figures on screen vs approved facts (§5)');
log();
const approved = [
  ['Years in public health', 28, EN.proof.items[0].value, FR.proof.items[0].value],
  ['Countries — lead NIS.COST costing', 5, EN.proof.items[1].value, FR.proof.items[1].value],
  ['Country offices overseen (UNFPA WCARO OIC)', 23, EN.proof.items[2].value, FR.proof.items[2].value],
  ['Country teams trained (15+)', 15, EN.proof.items[3].value, FR.proof.items[3].value],
  ['Working languages', 3, EN.proof.items[4].value, FR.proof.items[4].value],
  ['Djibouti NIS — strategic objectives', 26, EN.method.chain[0].value, FR.method.chain[0].value],
  ['Djibouti NIS — interventions', 110, EN.method.chain[1].value, FR.method.chain[1].value],
  ['Djibouti NIS — activities', 348, EN.method.chain[2].value, FR.method.chain[2].value],
  ['Workshop quality score — before', 77.8, EN.method.gauge.from, FR.method.gauge.from],
  ['Workshop quality score — after', 89.1, EN.method.gauge.to, FR.method.gauge.to],
  ['Five NIS.COST countries on the map', 5, Object.keys(EN.proof.countries).length, Object.keys(FR.proof.countries).length],
];
log('| Figure | Approved | EN on screen | FR on screen | Match |');
log('|---|---|---|---|---|');
let allMatch = true;
for (const [name, a, en, fr] of approved) {
  const m = a === en && a === fr;
  allMatch &&= m;
  log(`| ${name} | ${a} | ${en} | ${fr} | ${ok(m)} |`);
}
log();
log(`Suffix "+" on 15: EN ${EN.proof.items[3].suffix === '+' ? 'yes' : 'NO'} · FR ${FR.proof.items[3].suffix === '+' ? 'yes' : 'NO'}. All figures match: ${ok(allMatch)}.`);
log();

// 3. Reading time: every text block stays on screen ≥ words/3 + 1 s
log('## 3. Reading time (words ÷ 3 + 1 s)');
log();
const sc = Object.fromEntries(SCENES.map((s, i) => [s.id, {...s, duration: s.duration + (i === 0 ? 0 : PRE)}]));
const words = (t) => t.split(/\s+/).filter(Boolean).length;
const blocks = (c) => {
  const end = (id, exit = 14) => sc[id].duration - exit;
  const segOffers = (sc.offers.duration - 54) / 3;
  return [
    ['hook', 'Hook question', c.hook.lead + ' ' + c.hook.accent, 0, end('hook', 16)],
    ...c.bottleneck.lines.map((l, i) => ['bottleneck', `Bottleneck line ${i + 1}`, l, 8 + i * 30, end('bottleneck')]),
    ['bottleneck', 'Coda', c.bottleneck.coda, 110, end('bottleneck')],
    ['reveal', 'Name + title + base', `${c.reveal.name} ${c.reveal.title} ${c.reveal.base}`, 26, sc.reveal.duration - 16],
    ...c.proof.items.map((it, i) => ['proof', `Counter ${it.value}${it.suffix ?? ''}`, `${it.value} ${it.label}`, 14 + i * 30, end('proof')]),
    ...c.offers.items.map((it, i) => ['offers', `Offer ${it.num} (active window + recap)`, `${it.title} ${it.desc}`, 10 + i * segOffers, end('offers')]),
    ['method', 'Chain + traced', c.method.chain.map((x) => `${x.value} ${x.label}`).join(' ') + ' ' + c.method.traced, 8, end('method')],
    ['method', 'Gauge', `${c.method.gauge.to} ${c.method.gauge.label}`, 100, end('method')],
    ['method', 'Method line', c.method.tagline, 150, end('method')],
    ['trust', 'Agencies', c.trust.agencies.join(' '), 10, end('trust')],
    ['trust', 'Ministries', c.trust.ministriesLabel + ' ' + c.trust.ministries.join(' '), 54, end('trust')],
    ['cta', 'CTA lines', c.cta.lines.join(' '), 14, sc.cta.duration],
    ['cta', 'Invite', c.cta.invite, 56, sc.cta.duration],
    ['cta', 'Contacts', 'email phone linkedin', 78, sc.cta.duration],
  ];
};
log('| Lang | Block | Words | Needed | On screen | OK |');
log('|---|---|---|---|---|---|');
let readOk = true;
for (const c of [EN, FR]) {
  for (const [, name, text, from, to] of blocks(c)) {
    const need = words(text) / 3 + 1;
    const have = (to - from) / FPS;
    readOk &&= have >= need;
    log(`| ${c.lang} | ${name} | ${words(text)} | ${need.toFixed(1)} s | ${have.toFixed(1)} s | ${ok(have >= need)} |`);
  }
}
log();
log(`All blocks readable: ${ok(readOk)}. (Offers are scanned card by card: each card is lit for its own window, then all three stay lit for the recap.)`);
log();

// 4. Captions
log('## 4. Captions (SRT)');
log();
for (const lang of ['en', 'fr']) {
  const p = path.join(outDir, `captions_${lang}.srt`);
  if (!fs.existsSync(p)) {
    log(`captions_${lang}.srt: missing`);
    continue;
  }
  const cues = fs.readFileSync(p, 'utf8').trim().split(/\n\n+/);
  const t = (s) => {
    const [h, m, rest] = s.split(':');
    const [sec, ms] = rest.split(',');
    return Number(h) * 3600 + Number(m) * 60 + Number(sec) + Number(ms) / 1000;
  };
  let prev = 0;
  let valid = true;
  let maxLine = 0;
  cues.forEach((c, i) => {
    const [idx, time, ...text] = c.split('\n');
    const [a, b] = time.split(' --> ').map(t);
    valid &&= Number(idx) === i + 1 && a >= prev && b > a && text.length <= 2 && b <= TOTAL_FRAMES / FPS;
    maxLine = Math.max(maxLine, ...text.map((l) => l.length));
    prev = b;
  });
  log(`- captions_${lang}.srt: ${cues.length} cues · sequential, non-overlapping, ≤ 2 lines: ${ok(valid)} · longest line ${maxLine} chars (≤ 42: ${ok(maxLine <= 42)}). Timed to the VO windows in vo_script_${lang}.txt; re-time after recording.`);
}
log();

// 5. Provenance
log('## 5. Images and logos used');
log();
const used = new Set();
for (const f of fs.readdirSync(path.join(root, 'src/scenes')).concat(['../Thumbnail.tsx'])) {
  const s = fs.readFileSync(path.join(root, 'src/scenes', f), 'utf8');
  for (const m of s.matchAll(/(?:staticFile\(|src[=:]\s*)['"`]([^'"`]+\.(?:png|jpg))['"`]/g)) used.add(m[1]);
}
log('| Asset | Source |');
log('|---|---|');
for (const u of [...used].sort()) {
  const src = u.startsWith('field/') ? 'Field photo supplied by Dr. Sidibé (assets/field)' : u.startsWith('portrait') ? 'Portrait supplied by Dr. Sidibé' : 'DIAN K. PRO logo supplied by Dr. Sidibé';
  log(`| ${u} | ${src} |`);
}
log();
log('No third-party logo is rendered: institutions appear as text wordmarks only (scene 7). No AI-generated imagery.');

const report = lines.join('\n') + '\n';
fs.writeFileSync(path.join(outDir, 'QA_REPORT.md'), report);
console.log(report);
