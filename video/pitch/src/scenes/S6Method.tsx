import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {C} from '../theme';
import {DISPLAY, NUMERIC} from '../fonts';
import {Format, pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear, SceneExit} from '../components/Appear';
import {Counter} from '../components/Counter';
import {Network, RING_COLORS} from '../components/Network';
import {Gauge} from '../components/Gauge';
import {body, headline, kicker, SceneProps} from '../styles';

// Scene 6 — The method (Djibouti NIS 2027–2030 case). A radial traceability
// network grows 26 -> 110 -> 348; the workshop quality gauge sweeps
// 77.8 -> 89.1; the method line types itself in.
const RADII: [number, number, number] = [0.3, 0.66, 0.96];

const Arrow: React.FC<{size: number}> = ({size}) => (
  <svg width={size * 0.62} height={size * 0.5} viewBox="0 0 62 50" fill="none">
    <path d="M2 25H58M40 7L58 25L40 43" stroke={C.or} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const Dot: React.FC<{i: number; size: number}> = ({i, size}) => (
  <span style={{display: 'inline-block', width: size, height: size, borderRadius: '50%', background: RING_COLORS[i], flexShrink: 0}} />
);

// "26 objectives -> 110 interventions -> 348 activities"
const Chain: React.FC<{f: Format; chain: {value: number; label: string}[]; num: number; layout: 'row' | 'rows' | 'stacked'}> = ({f, chain, num, layout}) => {
  const T = TYPE[f];
  if (layout === 'row') {
    return (
      <div style={{display: 'flex', alignItems: 'flex-start', gap: 30}}>
        {chain.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 ? (
              <Appear at={i * 30} dy={0} style={{paddingTop: num * 0.28}}>
                <Arrow size={num * 0.8} />
              </Appear>
            ) : null}
            <Appear at={8 + i * 30} dy={16}>
              <div style={{display: 'flex', flexDirection: 'column', gap: 10}}>
                <div style={{fontFamily: DISPLAY, fontWeight: 500, fontSize: num, lineHeight: 1, color: C.champagne, ...NUMERIC}}>
                  <Counter at={8 + i * 30} value={c.value} dur={24} />
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
                  <Dot i={i} size={T.label * 0.32} />
                  <span style={body(T.label, C.ivoire, 500)}>{c.label}</span>
                </div>
              </div>
            </Appear>
          </React.Fragment>
        ))}
      </div>
    );
  }
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap: layout === 'rows' ? 14 : 18}}>
      {chain.map((c, i) => (
        <Appear key={i} at={8 + i * 30} dx={-20} dy={0}>
          <div style={{display: 'flex', alignItems: layout === 'rows' ? 'baseline' : 'flex-start', flexDirection: layout === 'rows' ? 'row' : 'column', gap: layout === 'rows' ? 18 : 2}}>
            <div style={{fontFamily: DISPLAY, fontWeight: 500, fontSize: num, lineHeight: 1, color: C.champagne, minWidth: layout === 'rows' ? num * 1.75 : undefined, ...NUMERIC}}>
              <Counter at={8 + i * 30} value={c.value} dur={24} />
            </div>
            <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
              <Dot i={i} size={T.label * 0.32} />
              <span style={body(T.label, C.ivoire, 500)}>{c.label}</span>
            </div>
          </div>
        </Appear>
      ))}
    </div>
  );
};

export const S6Method: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W} = useVideoConfig();
  const m = copy.method;
  const counts: [number, number, number] = [m.chain[0].value, m.chain[1].value, m.chain[2].value];
  const L = pick(f, {
    landscape: {
      kicker: {left: T.margin, top: 96},
      chain: {left: T.margin, top: 196},
      chainLayout: 'row' as const,
      num: 96,
      net: {left: 380, top: 400, size: 450},
      traced: {left: T.margin, top: 870, width: 1000},
      gauge: {left: 1180, top: 330},
      r: 230,
      gaugeNum: 110,
      tag: {left: T.margin, top: 960, width: W - 2 * T.margin},
      threadY: 160,
      threadEnd: 1120,
    },
    square: {
      kicker: {left: T.margin, top: 78},
      chain: {left: 560, top: 180},
      chainLayout: 'rows' as const,
      num: 64,
      net: {left: 70, top: 190, size: 430},
      traced: {left: 70, top: 640, width: 430},
      gauge: {left: 545, top: 470},
      r: 135,
      gaugeNum: 78,
      tag: {left: T.margin, top: 850, width: W - 2 * T.margin},
      threadY: 140,
      threadEnd: W + 20,
    },
    portrait: {
      kicker: {left: T.margin, top: 268},
      chain: {left: 190, top: 828},
      chainLayout: 'rows' as const,
      num: 72,
      net: {left: 320, top: 372, size: 440},
      traced: {left: T.margin, top: 0, width: 0},
      gauge: {left: 0, top: 1128, width: W},
      r: 130,
      gaugeNum: 76,
      tag: {left: T.margin, top: 1392, width: W - 2 * T.margin},
      threadY: 352,
      threadEnd: W + 20,
    },
  });
  const typeAt = 150;
  const chars = Math.floor(interpolate(frame, [typeAt, typeAt + 54], [0, m.tagline.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const caretOn = frame >= typeAt && (frame < typeAt + 60 || Math.floor(frame / 15) % 2 === 0);
  const parts = m.tagline.split(/(?<=\.)\s+/);
  return (
    <AbsoluteFill>
      <SceneExit dur={dur} frames={14}>
        <Appear at={2} dy={0} style={{position: 'absolute', ...L.kicker}}>
          <div style={kicker(f)}>{m.kicker}</div>
        </Appear>
        <div style={{position: 'absolute', ...L.chain}}>
          <Chain f={f} chain={m.chain} num={L.num} layout={L.chainLayout} />
        </div>
        <div style={{position: 'absolute', left: L.net.left, top: L.net.top}}>
          <Network size={L.net.size} counts={counts} radii={RADII} at={10} />
        </div>
        {f !== 'portrait' ? (
          <Appear at={100} dy={12} style={{position: 'absolute', ...L.traced}}>
            <div style={{...headline(T.label + 4, C.sable), fontStyle: 'italic', textAlign: 'center'}}>{m.traced}</div>
          </Appear>
        ) : null}
        <div style={{position: 'absolute', ...L.gauge, display: 'flex', flexDirection: f === 'portrait' ? 'row' : 'column', alignItems: 'center', justifyContent: 'center', gap: f === 'portrait' ? 44 : 18}}>
          <Gauge at={70} from={m.gauge.from} to={m.gauge.to} r={L.r} numSize={L.gaugeNum} labelSize={T.label} outOf={m.gauge.outOf} decimal={copy.decimal} stack={f === 'portrait'} />
          <Appear at={100} dy={14}>
            <div style={{...body(T.label, C.ivoire, 500), textAlign: f === 'portrait' ? 'left' : 'center', maxWidth: f === 'portrait' ? 400 : L.r * 2.6}}>{m.gauge.label}</div>
          </Appear>
        </div>
        {f === 'landscape' ? (
          <div style={{position: 'absolute', left: L.tag.left, top: L.tag.top, ...body(52, C.ivoire, 500), whiteSpace: 'nowrap'}}>
            {m.tagline.slice(0, chars)}
            <span style={{display: 'inline-block', width: 4, height: 52, marginLeft: 6, background: C.or, verticalAlign: 'middle', opacity: caretOn ? 1 : 0}} />
          </div>
        ) : (
          <div style={{position: 'absolute', ...L.tag, ...body(f === 'square' ? 48 : 56, C.ivoire, 600), textAlign: 'center'}}>
            {parts.map((t, i) => (
              <React.Fragment key={i}>
                {i > 0 ? ' ' : null}
                <span style={{opacity: interpolate(frame, [typeAt + i * 16, typeAt + i * 16 + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}), color: i === 2 ? C.champagne : C.ivoire, whiteSpace: 'nowrap'}}>
                  {t}
                </span>
              </React.Fragment>
            ))}
          </div>
        )}
      </SceneExit>
      <Thread d={`M-20 ${L.threadY}H${L.threadEnd}`} draw={[0, 30]} retract={[dur - 18, dur]} />
    </AbsoluteFill>
  );
};
