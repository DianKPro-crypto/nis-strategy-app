import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {getLength, getPointAtLength} from '@remotion/paths';
import {C, easeIn, easeInOut} from '../theme';

// The "strategic thread": one fine gold line that draws itself through every
// scene (problem -> person -> proof -> offer -> contact). It draws in with a
// glowing spark at its head and leaves by retracting its tail.
type Props = {
  d: string;
  draw: [number, number];
  retract?: [number, number];
  initial?: number; // head position at frame 0 (lets the cover frame show a drawn line)
  color?: string;
  width?: number;
  spark?: boolean;
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export const Thread: React.FC<Props> = ({d, draw, retract, initial = 0, color = C.or, width = 3, spark = true}) => {
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const len = useMemo(() => getLength(d), [d]);
  const head = interpolate(frame, draw, [initial, 1], {...clamp, easing: easeInOut});
  const tail = retract ? interpolate(frame, retract, [0, 1], {...clamp, easing: easeIn}) : 0;
  const visible = head - tail;
  if (visible <= 0.0005) return null;
  const tip = getPointAtLength(d, Math.min(head, 0.9999) * len) ?? {x: 0, y: 0};
  const sparkOpacity = spark ? interpolate(head, [0, 0.02, 0.97, 1], [0, 1, 1, 0], clamp) : 0;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <defs>
        <radialGradient id="spark">
          <stop offset="0%" stopColor={C.champagne} stopOpacity={0.9} />
          <stop offset="100%" stopColor={C.champagne} stopOpacity={0} />
        </radialGradient>
      </defs>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeDasharray={`${visible * len} ${len * 2}`}
        strokeDashoffset={-tail * len}
      />
      {sparkOpacity > 0 ? (
        <g opacity={sparkOpacity}>
          <circle cx={tip.x} cy={tip.y} r={width * 9} fill="url(#spark)" />
          <circle cx={tip.x} cy={tip.y} r={width * 1.4} fill={C.ivoire} />
        </g>
      ) : null}
    </svg>
  );
};
