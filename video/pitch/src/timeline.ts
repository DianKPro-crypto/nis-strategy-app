import beats from '../assets/beats.json';
import plan from './timeline.json';

// Scene cuts land on the music's beat grid: each nominal start snaps to the
// nearest detected beat when one is within `snapToleranceSec`.
const snap = (t: number) => {
  if (t === 0) return 0;
  let best = t;
  let bestDist = plan.snapToleranceSec;
  for (const b of beats.beats) {
    const d = Math.abs(b - t);
    if (d <= bestDist) {
      best = b;
      bestDist = d;
    }
  }
  return best;
};

export type SceneId = 'hook' | 'bottleneck' | 'reveal' | 'proof' | 'offers' | 'method' | 'trust' | 'cta';

export const TOTAL_FRAMES = Math.round(plan.total * plan.fps);

// Each scene (after the first) starts PRE frames before its cut so it can draw in
// while the previous scene fades out — a crossfade instead of a dip to black.
export const PRE = 10;

export const SCENES = plan.scenes.map((s, i) => {
  const from = Math.round(snap(s.start) * plan.fps);
  const next = plan.scenes[i + 1];
  const to = next ? Math.round(snap(next.start) * plan.fps) : TOTAL_FRAMES;
  return {id: s.id as SceneId, from, duration: to - from};
});

export const BEATS_SEC: number[] = beats.beats;
