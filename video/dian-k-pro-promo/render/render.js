// Rendu image par image de render/scene.html, puis assemblage ffmpeg.
// Usage :
//   node render/render.js --lang fr --fmt h --fps 30 --out build/fr_16x9.mp4 [--audio audio/x.wav] [--workers 4]
//   node render/render.js --lang fr --fmt h --stills 0,6,15,22,29,40 --out build/stills
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]);
  return acc;
}, []));
const LANG = args.lang || 'fr', FMT = args.fmt || 'h', FPS = +(args.fps || 30), DUR = +(args.dur || 45);
const W = FMT === 'v' ? 1080 : 1920, H = FMT === 'v' ? 1920 : 1080;
const ROOT = path.resolve(__dirname, '..');
const OUT = path.resolve(ROOT, args.out || `build/${LANG}_${FMT}.mp4`);
const WORKERS = +(args.workers || 4);

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2' };
function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(rsp);
    }).listen(0, () => res(srv));
  });
}

async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('[page]', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
  await page.goto(`http://localhost:${port}/render/scene.html?lang=${LANG}&fmt=${FMT}`);
  await page.waitForFunction(() => window.ready && window.renderAt, null, { timeout: 120000 });
  await page.evaluate(() => window.ready);
  return page;
}

const shot = (page, t) => page.evaluate(t => window.renderAt(t), t)
  .then(() => page.screenshot({ type: 'jpeg', quality: 94, clip: { x: 0, y: 0, width: W, height: H } }));

(async () => {
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

  if (args.stills) {
    fs.mkdirSync(OUT, { recursive: true });
    const page = await openPage(browser, port);
    for (const t of String(args.stills).split(',').map(Number)) {
      fs.writeFileSync(path.join(OUT, `${LANG}_${FMT}_${String(t).replace('.', '_')}.jpg`), await shot(page, t));
    }
    await browser.close(); srv.close(); return;
  }

  const total = Math.round(DUR * FPS);
  const START = Math.round(+(args.from || 0) * FPS);   // --from : ne rendre que la fin du film
  const tmp = path.join(ROOT, 'build', `tmp_${LANG}_${FMT}`);
  fs.mkdirSync(tmp, { recursive: true });
  const per = Math.ceil((total - START) / WORKERS);
  const t0 = Date.now();
  let done = 0;
  await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
    const a = START + w * per, b = Math.min(total, a + per);
    if (a >= b) return;
    const page = await openPage(browser, port);
    const seg = path.join(tmp, `seg_${w}.mp4`);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), seg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      const buf = await shot(page, f / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (++done % 60 === 0) process.stdout.write(`\r${done}/${total - START} images · ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    await page.close();
  }));
  await browser.close(); srv.close();
  console.log(`\nimages rendues en ${((Date.now() - t0) / 1000).toFixed(0)} s`);

  const list = path.join(tmp, 'list.txt');
  fs.writeFileSync(list, Array.from({ length: WORKERS }, (_, w) => `file 'seg_${w}.mp4'`).filter((_, w) => fs.existsSync(path.join(tmp, `seg_${w}.mp4`))).join('\n'));
  const ffArgs = ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list];
  if (args.audio) ffArgs.push('-i', path.resolve(ROOT, args.audio), '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-shortest');
  ffArgs.push('-c:v', 'copy', '-movflags', '+faststart', OUT);
  await new Promise((res, rej) => spawn('ffmpeg', ffArgs, { stdio: 'inherit' }).on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));
  console.log('→', OUT);
})().catch(e => { console.error(e); process.exit(1); });
