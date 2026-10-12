// Deterministic frame renderer: headless Chromium -> PNG frames -> ffmpeg.
// node render.mjs --stills 0,12,20            -> frames/still_<t>.png
// node render.mjs --from 0 --to 10 --fps 60 --out out/seg0.mp4 [--partners 0]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { chromium } from 'playwright';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith('--') ? [...a, [v.slice(2), arr[i + 1]]] : a), []));
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.ttf': 'font/ttf' };

const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'],
});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') console.error('[page]', m.text()); });
page.on('pageerror', (e) => console.error('[pageerror]', e.message));
await page.goto(`http://localhost:${port}/src/index.html?partners=${args.partners ?? '1'}`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });

if (args.stills) {
  fs.mkdirSync(path.join(ROOT, 'frames'), { recursive: true });
  for (const t of args.stills.split(',').map(Number)) {
    await page.evaluate((t) => window.renderAt(t), t);
    await page.screenshot({ path: path.join(ROOT, 'frames', `still_${t.toFixed(2)}.png`) });
    console.log('still', t);
  }
} else {
  const fps = Number(args.fps || 60), from = Number(args.from || 0), to = Number(args.to || 58.4);
  const f0 = Math.round(from * fps), f1 = Math.round(to * fps);
  fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', args.out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    await page.evaluate((t) => window.renderAt(t), f / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    if ((f - f0) % 60 === 0) console.log(`frame ${f}/${f1}  ${((Date.now() - t0) / 1000 / Math.max(1, f - f0 + 1)).toFixed(2)} s/frame`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
}
await browser.close();
server.close();
