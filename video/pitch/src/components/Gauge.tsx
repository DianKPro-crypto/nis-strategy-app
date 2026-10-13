import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, easeOut} from '../theme';
import {DISPLAY, NUMERIC, TEXT} from '../fonts';
import {fmt} from '../copy';

// Semicircular quality gauge. Progress uses the charter's functional green
// (gold is never a status colour).
const arc = (cx: number, cy: number, r: number, v0: number, v1: number) => {
  const p = (v: number) => {
    const t = Math.PI * (1 - v / 100);
    return [cx + r * Math.cos(t), cy - r * Math.sin(t)];
  };
  const [x0, y0] = p(v0);
  const [x1, y1] = p(v1);
  // A semicircular gauge never spans more than 180°, so the large-arc flag is always 0.
  return `M${x0} ${y0}A${r} ${r} 0 0 1 ${x1} ${y1}`;
};

export const Gauge: React.FC<{
  at: number;
  from: number;
  to: number;
  r: number;
  numSize: number;
  labelSize: number;
  outOf: string;
  decimal: string;
}> = ({at, from, to, r, numSize, labelSize, outOf, decimal}) => {
  const frame = useCurrentFrame();
  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const appear = interpolate(frame, [at, at + 18], [0, 1], {...clamp, easing: easeOut});
  const base = interpolate(frame, [at, at + 24], [0, from], {...clamp, easing: easeOut});
  const sweep = interpolate(frame, [at + 30, at + 72], [from, to], {...clamp, easing: easeOut});
  const value = frame < at + 30 ? base : sweep;
  const sw = r * 0.09;
  const W = r * 2 + sw * 2 + labelSize * 3.2;
  const cx = W / 2;
  const cy = r + sw;
  const tick = (() => {
    const t = Math.PI * (1 - from / 100);
    return {x1: cx + (r - sw) * Math.cos(t), y1: cy - (r - sw) * Math.sin(t), x2: cx + (r + sw * 1.4) * Math.cos(t), y2: cy - (r + sw * 1.4) * Math.sin(t), t};
  })();
  return (
    <div style={{position: 'relative', width: W, height: cy + numSize * 0.35, opacity: appear}}>
      <svg width={W} height={cy + sw} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <path d={arc(cx, cy, r, 0, 100)} stroke={C.anthracite} strokeWidth={sw} fill="none" strokeLinecap="butt" />
        <path d={arc(cx, cy, r, 0, Math.min(value, from))} stroke={C.pierre} strokeWidth={sw} fill="none" />
        {value > from ? <path d={arc(cx, cy, r, from, value)} stroke={C.succes} strokeWidth={sw} fill="none" /> : null}
        <line x1={tick.x1} y1={tick.y1} x2={tick.x2} y2={tick.y2} stroke={C.ivoire} strokeWidth={3} opacity={frame > at + 26 ? 1 : 0} />
        <text
          x={cx + (r + sw * 1.9) * Math.cos(tick.t)}
          y={cy - (r + sw * 1.9) * Math.sin(tick.t) - labelSize * 0.35}
          fill={C.sable}
          fontFamily={TEXT}
          fontSize={labelSize}
          fontWeight={500}
          textAnchor="start"
          dominantBaseline="middle"
          opacity={interpolate(frame, [at + 26, at + 40], [0, 1], clamp)}
          style={NUMERIC}
        >
          {fmt(from, 1, decimal)}
        </text>
      </svg>
      <div
        style={{
          position: 'absolute',
          left: 0,
          width: W,
          top: cy - numSize * 0.95,
          textAlign: 'center',
          fontFamily: DISPLAY,
          fontWeight: 500,
          fontSize: numSize,
          lineHeight: 1,
          color: C.champagne,
          ...NUMERIC,
        }}
      >
        {fmt(value, 1, decimal)}
        <span style={{fontFamily: TEXT, fontSize: labelSize, color: C.sable, fontWeight: 500, marginLeft: 12}}>{outOf}</span>
      </div>
    </div>
  );
};
