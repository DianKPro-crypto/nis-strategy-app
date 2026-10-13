import React, {useMemo} from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {geoNaturalEarth1, geoPath} from 'd3-geo';
import {feature} from 'topojson-client';
import countries50 from 'world-atlas/countries-50m.json';
import land50 from 'world-atlas/land-50m.json';
import {C, easeOut} from '../theme';
import {TEXT} from '../fonts';

// Minimalist Africa + Middle East dot-matrix map (SVG, from world-atlas TopoJSON).
// Land is drawn as one continuous dot field with NO internal borders — this keeps
// the map neutral on disputed boundaries. Only the five NIS.COST countries are
// drawn as shapes; Casablanca (base) pulses.
export type LabelPos = {dx: number; dy: number; anchor: 'start' | 'end' | 'middle'};

const CASABLANCA: [number, number] = [-7.59, 33.57];

export const MapAfricaME: React.FC<{
  w: number;
  h: number;
  at: number;
  highlightAt: number;
  labels: Record<string, string>;
  labelPos: Record<string, LabelPos>;
  baseLabel: string;
  basePos: LabelPos;
  fontSize: number;
  spacing?: number;
  // Legend mode: labels stacked at (x, y + rank * gap), ranked north -> south,
  // each tied to its country by a thin leader line.
  legend?: {x: number; y: number; gap: number};
}> = ({w, h, at, highlightAt, labels, labelPos, baseLabel, basePos, fontSize, spacing = 13, legend}) => {
  const frame = useCurrentFrame();
  const ids = Object.keys(labels);
  const geo = useMemo(() => {
    const topoLand = land50 as any;
    const topoCountries = countries50 as any;
    const land = feature(topoLand, topoLand.objects.land) as any;
    const countries = feature(topoCountries, topoCountries.objects.countries) as any;
    const frameBox = {
      type: 'Feature',
      properties: {},
      geometry: {type: 'MultiPoint', coordinates: [[-18, -35], [56, -35], [-18, 37], [56, 37], [19, 38], [19, -36]]},
    };
    const proj = geoNaturalEarth1().rotate([-19, 0]).fitExtent([[0, 0], [w, h]], frameBox as any);
    const path = geoPath(proj);

    // Rasterise land once, then sample a regular grid -> dot field.
    const canvas = document.createElement('canvas');
    canvas.width = Math.ceil(w);
    canvas.height = Math.ceil(h);
    const ctx = canvas.getContext('2d')!;
    ctx.fill(new Path2D(path(land) ?? ''));
    const px = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    const r = spacing * 0.27;
    let dots = '';
    for (let y = spacing / 2; y < h; y += spacing) {
      for (let x = spacing / 2; x < w; x += spacing) {
        if (px[(Math.floor(y) * canvas.width + Math.floor(x)) * 4 + 3] > 120) {
          dots += `M${(x - r).toFixed(1)} ${y.toFixed(1)}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0`;
        }
      }
    }
    const hi = ids.map((id) => {
      const f = countries.features.find((c: any) => Number(c.id) === Number(id));
      return {id, d: f ? path(f) ?? '' : '', c: f ? path.centroid(f) : [0, 0]};
    });
    const casa = proj(CASABLANCA) ?? [0, 0];
    return {dots, hi, casa};
  }, [w, h, spacing, ids.join(',')]);

  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const reveal = interpolate(frame, [at, at + 40], [0, 1], {...clamp, easing: easeOut});
  const revealR = reveal * Math.hypot(w, h) * 1.05;

  const pulse = (offset: number) => {
    const t = ((frame - at + offset) % 36) / 36;
    return {r: 10 + t * 46, o: (1 - t) * 0.8};
  };

  return (
    <svg width={w} height={h} style={{overflow: 'visible'}}>
      <defs>
        <radialGradient id="map-reveal" gradientUnits="userSpaceOnUse" cx={geo.casa[0]} cy={geo.casa[1]} r={Math.max(1, revealR)}>
          <stop offset="0.82" stopColor="#fff" />
          <stop offset="1" stopColor="#fff" stopOpacity={0} />
        </radialGradient>
        <mask id="map-mask">
          <rect x={-w} y={-h} width={w * 3} height={h * 3} fill="url(#map-reveal)" />
        </mask>
      </defs>
      <g mask="url(#map-mask)">
        <path d={geo.dots} fill={C.pierre} opacity={0.55} />
      </g>
      {geo.hi.map((c, i) => {
        const p = interpolate(frame, [highlightAt + i * 6, highlightAt + i * 6 + 16], [0, 1], {...clamp, easing: easeOut});
        if (p <= 0) return null;
        const rank = [...geo.hi].sort((a, b) => a.c[1] - b.c[1]).findIndex((x) => x.id === c.id);
        const lp: LabelPos = legend
          ? {dx: legend.x - c.c[0], dy: legend.y + rank * legend.gap - c.c[1], anchor: 'start'}
          : labelPos[c.id] ?? {dx: 30, dy: 0, anchor: 'start'};
        const lx = c.c[0] + lp.dx;
        const ly = c.c[1] + lp.dy;
        return (
          <g key={c.id} opacity={p}>
            <path d={c.d} fill={C.or} stroke={C.champagne} strokeWidth={1.5} />
            {c.id === '174' ? <circle cx={c.c[0]} cy={c.c[1]} r={14} fill="none" stroke={C.champagne} strokeWidth={2.5} /> : null}
            {labels[c.id] ? (
              legend ? (
                <path d={`M${c.c[0]} ${c.c[1]}L${lx - 46} ${ly}H${lx - 14}`} fill="none" stroke={C.sable} strokeWidth={1.5} opacity={0.7} />
              ) : (
                <line
                  x1={c.c[0]}
                  y1={c.c[1]}
                  x2={lx + (lp.anchor === 'start' ? -10 : lp.anchor === 'end' ? 10 : 0)}
                  y2={ly}
                  stroke={C.sable}
                  strokeWidth={1.5}
                  opacity={0.8}
                />
              )
            ) : null}
            <text
              x={lx}
              y={ly}
              fill={C.ivoire}
              fontFamily={TEXT}
              fontWeight={500}
              fontSize={fontSize}
              textAnchor={lp.anchor}
              dominantBaseline="middle"
              stroke={C.noir}
              strokeWidth={10}
              paintOrder="stroke"
              strokeLinejoin="round"
            >
              {labels[c.id]}
            </text>
          </g>
        );
      })}
      <g opacity={reveal}>
        {[0, 18].map((o) => {
          const {r, o: op} = pulse(o);
          return <circle key={o} cx={geo.casa[0]} cy={geo.casa[1]} r={r} fill="none" stroke={C.champagne} strokeWidth={2.5} opacity={op} />;
        })}
        <circle cx={geo.casa[0]} cy={geo.casa[1]} r={9} fill={C.champagne} />
        {baseLabel ? <text
          x={geo.casa[0] + basePos.dx}
          y={geo.casa[1] + basePos.dy}
          fill={C.champagne}
          fontFamily={TEXT}
          fontWeight={600}
          fontSize={fontSize}
          textAnchor={basePos.anchor}
          dominantBaseline="middle"
          stroke={C.noir}
          strokeWidth={10}
          paintOrder="stroke"
        >
          {baseLabel}
        </text> : null}
      </g>
    </svg>
  );
};
