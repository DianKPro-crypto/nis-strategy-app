import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, easeOut} from '../theme';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear, SceneExit} from '../components/Appear';
import {Photo} from '../components/Photo';
import {Vignette} from '../components/Grain';
import {headline, SceneProps} from '../styles';

// Scene 2 — The bottleneck. Real field photo (IMG_2110, house-to-house team),
// text kept off faces; each line is struck through by the gold thread.
// The strike is a background on the inline text (box-decoration-break: clone),
// so it stays on every line even if a long translation wraps.
const Struck: React.FC<{at: number; text: string; size: number}> = ({at, text, size}) => {
  const frame = useCurrentFrame();
  const strike = interpolate(frame, [at + 16, at + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: easeOut});
  const h = Math.max(3, Math.round(size * 0.05));
  return (
    <Appear at={at} dy={22}>
      <div style={{...headline(size), opacity: 1 - strike * 0.18}}>
        <span
          style={{
            backgroundImage: `linear-gradient(${C.or}, ${C.or})`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: '0 58%',
            backgroundSize: `${strike * 100}% ${h}px`,
            WebkitBoxDecorationBreak: 'clone',
            boxDecorationBreak: 'clone',
            padding: '0 6px',
            margin: '0 -6px',
          }}
        >
          {text}
        </span>
      </div>
    </Appear>
  );
};

// Largest size (≤ the format's h2) at which the longest line fits on one line.
// Playfair Display averages ≈ 0.47 em per character.
const fitSize = (lines: string[], width: number, max: number, min: number) =>
  Math.max(min, Math.min(max, Math.floor(width / (Math.max(...lines.map((l) => l.length)) * 0.47))));

export const S2Bottleneck: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const {width: W} = useVideoConfig();
  const L = pick(f, {
    landscape: {
      photo: {left: 960, top: 0, width: 960, height: 1080},
      pos: '42% 45%',
      fade: `linear-gradient(90deg, ${C.noir} 0%, rgba(10,10,10,0.7) 12%, rgba(10,10,10,0) 36%)`,
      text: {left: T.margin, top: 250, width: 820},
      threadY: 930,
    },
    square: {
      photo: {left: 0, top: 0, width: 1080, height: 560},
      pos: '45% 35%',
      fade: `linear-gradient(0deg, ${C.noir} 0%, rgba(10,10,10,0.6) 22%, rgba(10,10,10,0) 55%)`,
      text: {left: T.margin, top: 560, width: 900},
      threadY: 1010,
    },
    portrait: {
      photo: {left: 0, top: 0, width: 1080, height: 1000},
      pos: '52% 40%',
      fade: `linear-gradient(0deg, ${C.noir} 0%, rgba(10,10,10,0.6) 18%, rgba(10,10,10,0) 45%)`,
      text: {left: T.margin, top: 1010, width: 900},
      threadY: 1590,
    },
  });
  const size = fitSize(copy.bottleneck.lines, L.text.width, T.h2, f === 'portrait' ? 60 : 56);
  return (
    <AbsoluteFill>
      <SceneExit dur={dur} frames={14}>
        <Appear at={0} dur={24} dy={0}>
          <div style={{position: 'absolute', ...L.photo}}>
            <Photo src="field/IMG_2110.jpg" position={L.pos} dur={dur} filter="grayscale(0.55) contrast(1.05) brightness(0.95)" style={{inset: 0}} />
            <div style={{position: 'absolute', inset: 0, background: L.fade}} />
            <div style={{position: 'absolute', inset: 0, background: 'rgba(10,10,10,0.12)'}} />
            <Vignette strength={0.28} />
          </div>
        </Appear>
        <div style={{position: 'absolute', ...L.text, display: 'flex', flexDirection: 'column', gap: size * 0.32}}>
          {copy.bottleneck.lines.map((line, i) => (
            <Struck key={i} at={8 + i * 30} text={line} size={size} />
          ))}
          <Appear at={8 + 3 * 30 + 12} dy={18} style={{marginTop: size * 0.25}}>
            <div style={{...headline(size * 0.88, C.champagne), fontStyle: 'italic'}}>{copy.bottleneck.coda}</div>
          </Appear>
        </div>
      </SceneExit>
      <Thread d={`M-20 ${L.threadY}H${W + 20}`} draw={[dur - 40, dur - 10]} retract={[dur - 16, dur]} />
    </AbsoluteFill>
  );
};
