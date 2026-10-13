// Mirrors src/timeline.ts (scene starts snapped to the music beat grid).
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const plan = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const beats = JSON.parse(fs.readFileSync(path.join(root, 'assets/beats.json'), 'utf8')).beats;

const snap = (t) => {
  if (t === 0) return 0;
  let best = t;
  let bestDist = plan.snapToleranceSec;
  for (const b of beats) {
    const d = Math.abs(b - t);
    if (d <= bestDist) {
      best = b;
      bestDist = d;
    }
  }
  return best;
};

export const FPS = plan.fps;
export const TOTAL_FRAMES = Math.round(plan.total * plan.fps);
export const PRE = 10; // keep in sync with src/timeline.ts
export const SCENES = plan.scenes.map((s, i) => {
  const from = Math.round(snap(s.start) * plan.fps);
  const next = plan.scenes[i + 1];
  const to = next ? Math.round(snap(next.start) * plan.fps) : TOTAL_FRAMES;
  return {id: s.id, from, duration: to - from};
});
