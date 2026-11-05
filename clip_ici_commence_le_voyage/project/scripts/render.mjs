// Rendu robuste par segments (relance automatique d'un segment en cas d'échec), puis assemblage sans réencodage.
// Usage : node scripts/render.mjs <Voyage16x9|Voyage9x16> <sortie.mp4> [taille_segment=500]
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const [, , id, out, chunkArg] = process.argv;
const CHUNK = Number(chunkArg || 500);
const tmp = path.resolve(`../work/chunks_${id}`);
fs.mkdirSync(tmp, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id, inputProps: {}});
const N = composition.durationInFrames;
const parts = [];
for (let start = 0, i = 0; start < N; start += CHUNK, i++) {
  const end = Math.min(N - 1, start + CHUNK - 1);
  const file = path.join(tmp, `part_${String(i).padStart(3, '0')}.mp4`);
  parts.push(file);
  if (fs.existsSync(file + '.ok')) continue; // reprise
  for (let attempt = 1; ; attempt++) {
    try {
      await renderMedia({
        serveUrl, composition, codec: 'h264', outputLocation: file, frameRange: [start, end],
        muted: true, crf: 14, pixelFormat: 'yuv420p', imageFormat: 'jpeg', jpegQuality: 95,
        concurrency: 4, timeoutInMilliseconds: 60000, overwrite: true,
      });
      fs.writeFileSync(file + '.ok', '');
      console.log(`${id} segment ${i} [${start}-${end}] ok`);
      break;
    } catch (e) {
      console.log(`${id} segment ${i} tentative ${attempt} échouée : ${String(e.message).slice(0, 160)}`);
      if (attempt >= 4) throw e;
    }
  }
}
const list = path.join(tmp, 'list.txt');
fs.writeFileSync(list, parts.map((p) => `file '${p}'`).join('\n'));
execFileSync('ffmpeg', ['-hide_banner', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', path.resolve(out)]);
console.log('assemblé :', out);
