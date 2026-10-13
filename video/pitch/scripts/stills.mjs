// Render QA stills (start / middle / end of every scene) for one or more compositions.
// Usage: node scripts/stills.mjs <CompositionId,...> [outDir] [scene,...]
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {SCENES} from './timeline.mjs';

const [ids = 'Pitch-EN-16x9', outDir = 'previews', only] = process.argv.slice(2);
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || null;
const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'assets')});
fs.mkdirSync(path.join(root, outDir), {recursive: true});
for (const id of ids.split(',')) {
  const composition = await selectComposition({serveUrl, id, browserExecutable});
  for (const [i, s] of SCENES.entries()) {
    if (only && !only.split(',').includes(s.id)) continue;
    const frames = {
      start: i === 0 ? 0 : s.from + 10,
      mid: s.from + Math.round(s.duration / 2),
      end: s.from + s.duration - 18,
    };
    for (const [k, frame] of Object.entries(frames)) {
      const output = path.join(root, outDir, `${id}_${i + 1}-${s.id}_${k}.png`);
      await renderStill({composition, serveUrl, output, frame, browserExecutable, imageFormat: 'png', overwrite: true});
    }
    process.stdout.write(`${id} ${s.id} ✓\n`);
  }
}
