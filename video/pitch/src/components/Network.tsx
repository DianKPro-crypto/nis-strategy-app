import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, easeOut} from '../theme';

// Radial traceability network: 26 objectives (inner ring) -> 110 interventions
// (middle ring) -> 348 activities (outer ring). Every child links to exactly one
// parent, so the whole structure is traced end to end.
export const RING_COLORS = [C.champagne, C.or, C.sable];

type Pt = {x: number; y: number; a: number};

export const Network: React.FC<{
  size: number;
  counts: [number, number, number];
  radii: [number, number, number]; // fractions of size/2
  at: number;
}> = ({size, counts, radii, at}) => {
  const frame = useCurrentFrame();
  const c = size / 2;
  const g = useMemo(() => {
    const ring = (n: number, r: number): Pt[] =>
      Array.from({length: n}, (_, i) => {
        const a = -Math.PI / 2 + ((i + 0.5) * 2 * Math.PI) / n;
        return {x: c + r * c * Math.cos(a), y: c + r * c * Math.sin(a), a};
      });
    const [na, nb, nc] = counts;
    const A = ring(na, radii[0]);
    const B = ring(nb, radii[1]);
    const Cc = ring(nc, radii[2]);
    const link = (p: Pt, q: Pt, rp: number, rq: number) => {
      const rm = ((rp + rq) / 2) * c;
      return `M${p.x} ${p.y}C${c + rm * Math.cos(p.a)} ${c + rm * Math.sin(p.a)} ${c + rm * Math.cos(q.a)} ${c + rm * Math.sin(q.a)} ${q.x} ${q.y}`;
    };
    const ab = B.map((b, i) => link(A[Math.floor((i * na) / nb)], b, radii[0], radii[1]));
    const bc = Cc.map((q, j) => link(B[Math.floor((j * nb) / nc)], q, radii[1], radii[2]));
    const hub = A.map((p) => `M${c} ${c}L${p.x} ${p.y}`);
    return {A, B, C: Cc, ab, bc, hub};
  }, [size, counts, radii]);

  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const pA = interpolate(frame, [at, at + 22], [0, 1], {...clamp, easing: easeOut});
  const pAB = interpolate(frame, [at + 16, at + 52], [0, 1], clamp);
  const pBC = interpolate(frame, [at + 46, at + 92], [0, 1], clamp);
  const local = (p: number, i: number, n: number) => Math.max(0, Math.min(1, p * 1.6 - (i / n) * 0.6));
  const dash = (l: number) => ({pathLength: 1, strokeDasharray: '1 1', strokeDashoffset: 1 - l});

  return (
    <svg width={size} height={size} style={{overflow: 'visible'}}>
      {radii.map((r, i) => (
        <circle key={i} cx={c} cy={c} r={r * c} fill="none" stroke={C.anthracite} strokeWidth={1} opacity={pA} />
      ))}
      {g.hub.map((d, i) => (
        <path key={`h${i}`} d={d} {...dash(local(pA, i, g.hub.length))} stroke={C.champagne} strokeOpacity={0.35} strokeWidth={1.2} fill="none" />
      ))}
      {g.bc.map((d, j) => {
        const l = local(pBC, j, g.bc.length);
        return l > 0 ? <path key={`bc${j}`} d={d} {...dash(l)} stroke={C.or} strokeOpacity={0.32} strokeWidth={1} fill="none" /> : null;
      })}
      {g.ab.map((d, i) => {
        const l = local(pAB, i, g.ab.length);
        return l > 0 ? <path key={`ab${i}`} d={d} {...dash(l)} stroke={C.or} strokeOpacity={0.55} strokeWidth={1.3} fill="none" /> : null;
      })}
      {g.C.map((p, j) => (
        <circle key={`c${j}`} cx={p.x} cy={p.y} r={size * 0.0048 + 0.6} fill={RING_COLORS[2]} opacity={local(pBC, j, g.C.length) >= 1 ? 1 : 0} />
      ))}
      {g.B.map((p, i) => (
        <circle key={`b${i}`} cx={p.x} cy={p.y} r={size * 0.0075 + 0.6} fill={RING_COLORS[1]} opacity={local(pAB, i, g.B.length) >= 1 ? 1 : 0} />
      ))}
      {g.A.map((p, i) => (
        <circle key={`a${i}`} cx={p.x} cy={p.y} r={size * 0.012 + 1} fill={RING_COLORS[0]} opacity={local(pA, i, g.A.length)} />
      ))}
      <circle cx={c} cy={c} r={size * 0.02} fill={C.champagne} opacity={pA} />
    </svg>
  );
};
