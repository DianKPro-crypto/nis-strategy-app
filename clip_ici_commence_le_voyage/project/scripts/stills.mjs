// Génère des images témoins : node scripts/stills.mjs <Voyage16x9|Voyage9x16> <outDir> <sec1,sec2,...>
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';
const [, , id, out, list] = process.argv;
fs.mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id, inputProps: {}});
for (const s of list.split(',').map(Number)) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(s * 25));
  const output = path.join(out, `${id}_${String(s).padStart(6, '0')}.jpg`);
  await renderStill({serveUrl, composition, frame, output, imageFormat: 'jpeg', jpegQuality: 85});
  console.log(output);
}
