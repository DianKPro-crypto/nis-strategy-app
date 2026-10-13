import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {easeIn, easeOut} from '../theme';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const useEnter = (at: number, dur = 18) =>
  interpolate(useCurrentFrame(), [at, at + dur], [0, 1], {...clamp, easing: easeOut});

// Fades and slides an element in at `at` (frames); optional exit at `out`.
export const Appear: React.FC<{
  at: number;
  dur?: number;
  dx?: number;
  dy?: number;
  out?: number;
  outDur?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({at, dur = 18, dx = 0, dy = 28, out, outDur = 12, style, children}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + dur], [0, 1], {...clamp, easing: easeOut});
  const o = out === undefined ? 1 : interpolate(frame, [out, out + outDur], [1, 0], {...clamp, easing: easeIn});
  return (
    <div style={{opacity: p * o, transform: `translate(${dx * (1 - p)}px, ${dy * (1 - p)}px)`, ...style}}>
      {children}
    </div>
  );
};

// Whole-scene exit: everything except the thread fades out over the last frames.
export const SceneExit: React.FC<{dur: number; frames?: number; children: React.ReactNode}> = ({dur, frames = 12, children}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [dur - frames, dur], [1, 0], {...clamp, easing: easeIn});
  return <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>;
};
