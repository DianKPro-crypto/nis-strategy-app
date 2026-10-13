import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile} from 'remotion';
import {C, FPS} from './theme';
import {COPY, Lang} from './copy';
import {PRE, SCENES, TOTAL_FRAMES, SceneId} from './timeline';
import {Grain} from './components/Grain';
import {SceneProps} from './styles';
import vo from './vo.json';
import {S1Hook} from './scenes/S1Hook';
import {S2Bottleneck} from './scenes/S2Bottleneck';
import {S3Reveal} from './scenes/S3Reveal';
import {S4Proof} from './scenes/S4Proof';
import {S5Offers} from './scenes/S5Offers';
import {S6Method} from './scenes/S6Method';
import {S7Trust} from './scenes/S7Trust';
import {S8CTA} from './scenes/S8CTA';

const SCENE_COMPONENTS: Record<SceneId, React.FC<SceneProps>> = {
  hook: S1Hook,
  bottleneck: S2Bottleneck,
  reveal: S3Reveal,
  proof: S4Proof,
  offers: S5Offers,
  method: S6Method,
  trust: S7Trust,
  cta: S8CTA,
};

export type PitchProps = {lang: Lang; music: boolean; voiceover: boolean};

type VoBlock = {scene: string; startOffset: number; endOffset?: number; endScene?: string; endAt?: number};

// VO windows (frames) from src/vo.json — used to duck the music under the voice.
const voWindows = (lang: Lang): [number, number][] =>
  (vo[lang] as VoBlock[]).map((b) => {
    const s = SCENES.find((x) => x.id === b.scene)!;
    const start = s.from / FPS + b.startOffset;
    const end = b.endScene
      ? SCENES.find((x) => x.id === b.endScene)!.from / FPS + (b.endAt ?? 0)
      : b.endAt !== undefined
        ? s.from / FPS + b.endAt
        : (s.from + s.duration) / FPS + (b.endOffset ?? 0);
    return [Math.round(start * FPS), Math.round(end * FPS)];
  });

const DUCK = Math.pow(10, -10 / 20); // -10 dB
const RAMP = 6; // 200 ms at 30 fps

export const Pitch: React.FC<PitchProps> = ({lang, music, voiceover}) => {
  const copy = COPY[lang];
  const windows = voiceover ? voWindows(lang) : [];
  const duck = (fr: number) => {
    let g = 1;
    for (const [a, b] of windows) {
      const k = interpolate(fr, [a - RAMP, a, b, b + RAMP], [1, DUCK, DUCK, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
      g = Math.min(g, k);
    }
    return g;
  };
  return (
    <AbsoluteFill style={{background: C.noir}}>
      {SCENES.map((s, i) => {
        const Scene = SCENE_COMPONENTS[s.id];
        const pre = i === 0 ? 0 : PRE;
        return (
          <Sequence key={s.id} from={s.from - pre} durationInFrames={s.duration + pre} name={s.id}>
            <Scene dur={s.duration + pre} copy={copy} />
          </Sequence>
        );
      })}
      <Grain opacity={0.03} />
      {music ? (
        <Audio
          src={staticFile('music.mp3')}
          volume={(fr) =>
            interpolate(fr, [0, 12, TOTAL_FRAMES - 105, TOTAL_FRAMES - 6], [0, 0.9, 0.9, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }) * duck(fr)
          }
        />
      ) : null}
      {voiceover ? <Audio src={staticFile(`vo_${lang}.mp3`)} /> : null}
    </AbsoluteFill>
  );
};
