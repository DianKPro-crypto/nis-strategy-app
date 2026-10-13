import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, easeOut} from '../theme';
import {DISPLAY, NUMERIC} from '../fonts';
import {Format, pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear, SceneExit} from '../components/Appear';
import {Photo} from '../components/Photo';
import {OFFER_ICONS} from '../components/Icons';
import {body, headline, kicker, SceneProps} from '../styles';

// Scene 5 — Three offers. Cards slide out of the thread; the active card is
// lit, the others dim; a short recap lights all three before the cut.
const PHOTOS = [
  {src: 'field/IMG_2065.jpg', pos: '35% 30%'},
  {src: 'field/IMG_3341.jpg', pos: '60% 45%'},
  {src: 'field/IMG_4598.jpg', pos: '50% 30%'},
];
const RECAP = 54;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const Card: React.FC<{
  f: Format;
  i: number;
  item: {num: string; title: string; desc: string};
  active: number; // 0..1
  descOpacity?: number;
  drawAt: number;
  enterAt: number;
  box: {left: number; top: number; width: number; height: number};
}> = ({f, i, item, active, descOpacity = 1, drawAt, enterAt, box}) => {
  const frame = useCurrentFrame();
  const T = TYPE[f];
  const enter = interpolate(frame, [enterAt, enterAt + 22], [0, 1], {...clamp, easing: easeOut});
  const iconP = interpolate(frame, [drawAt, drawAt + 30], [0, 1], clamp);
  const Icon = OFFER_ICONS[i];
  const dim = 0.4 + 0.6 * active;
  const column = f === 'landscape';
  const photoW = column ? box.width : f === 'square' ? 250 : 320;
  const photoH = column ? 300 : box.height;
  const iconSize = column ? 92 : f === 'square' ? 76 : 96;
  return (
    <div
      style={{
        position: 'absolute',
        ...box,
        clipPath: `inset(0 0 ${(1 - enter) * 100}% 0)`,
        transform: `translateY(${(1 - enter) * -40 - active * (column ? 10 : 0)}px)`,
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: C.graphite,
          border: `2px solid ${active > 0.5 ? C.or : C.anthracite}`,
          borderColor: `rgba(212,164,76,${0.15 + 0.85 * active})`,
          borderRadius: 6,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: column ? 'column' : 'row',
          opacity: dim,
        }}
      >
        <div style={{position: 'relative', width: photoW, height: photoH, flexShrink: 0}}>
          <Photo
            src={PHOTOS[i].src}
            position={PHOTOS[i].pos}
            dur={600}
            zoom={[1.04, 1.04]}
            filter={`grayscale(${1 - active * 0.85}) brightness(${0.85 + 0.15 * active})`}
            style={{inset: 0}}
          />
          <div style={{position: 'absolute', inset: 0, background: column ? 'linear-gradient(0deg, rgba(26,26,26,0.85) 0%, rgba(26,26,26,0) 40%)' : 'linear-gradient(0deg, rgba(10,10,10,0.75) 0%, rgba(10,10,10,0) 38%)'}} />
          {!column ? (
            <div style={{position: 'absolute', left: 18, bottom: 16, width: iconSize, height: iconSize, borderRadius: '50%', background: C.noir, border: `2px solid ${C.or}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <Icon size={iconSize * 0.66} progress={iconP} />
            </div>
          ) : null}
        </div>
        <div style={{position: 'relative', flex: 1, padding: column ? '0 40px 36px' : f === 'square' ? '10px 28px' : '24px 30px', display: 'flex', flexDirection: 'column', gap: column ? 18 : f === 'square' ? 6 : 12, justifyContent: column ? 'flex-start' : 'center'}}>
          {column ? (
            <div style={{display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: -iconSize / 2}}>
              <div style={{width: iconSize, height: iconSize, borderRadius: '50%', background: C.noir, border: `2px solid ${C.or}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <Icon size={iconSize * 0.66} progress={iconP} />
              </div>
              <div style={{fontFamily: DISPLAY, fontSize: 60, color: C.champagne, lineHeight: 1, ...NUMERIC}}>{item.num}</div>
            </div>
          ) : null}
          <div style={{...headline(column ? 54 : f === 'square' ? 52 : 58), fontWeight: 500, marginTop: column ? 8 : 0}}>
            {!column ? <span style={{color: C.champagne, ...NUMERIC}}>{item.num}&nbsp;</span> : null}
            {item.title}
          </div>
          <div
            style={{
              ...body(T.label, C.sable, 400),
              opacity: f === 'portrait' ? descOpacity : 1,
              maxHeight: f === 'portrait' ? descOpacity * 300 : undefined,
              overflow: 'hidden',
            }}
          >
            {item.desc}
          </div>
        </div>
      </div>
    </div>
  );
};

export const S5Offers: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W} = useVideoConfig();
  const seg = (dur - RECAP) / 3;
  const L = pick(f, {
    landscape: {kicker: {left: T.margin, top: 96}, threadY: 196, top: 240, height: 740, gap: 40},
    square: {kicker: {left: T.margin, top: 78}, threadY: 146, top: 182, height: 258, gap: 22},
    portrait: {kicker: {left: T.margin, top: 268}, threadY: 352, top: 392, height: 382, gap: 24},
  });
  const states = copy.offers.items.map((_, i) => {
    const start = 10 + i * seg;
    const end = 10 + (i + 1) * seg;
    const on = interpolate(frame, [start - 4, start + 8], [0, 1], clamp);
    const off = i === 2 ? 0 : interpolate(frame, [end - 4, end + 8], [0, 1], clamp);
    const recap = interpolate(frame, [dur - RECAP, dur - RECAP + 12], [0, 1], clamp);
    const focus = on * (1 - off) * (1 - recap); // the one card being presented
    return {start, focus, active: Math.max(on * (1 - off), recap)};
  });
  // 9:16 accordion: the presented card expands (photo + description), the
  // others collapse to their titles, so long FR copy never overflows.
  const COLLAPSED = 240;
  const EXPANDED = 1600 - L.top - 2 * COLLAPSED - 2 * L.gap;
  let y = L.top;
  const boxes = [0, 1, 2].map((i) => {
    if (f === 'landscape') {
      const w = (W - 2 * T.margin - 2 * L.gap) / 3;
      return {left: T.margin + i * (w + L.gap), top: L.top, width: w, height: L.height};
    }
    if (f === 'portrait') {
      const anyFocus = Math.max(...states.map((st) => st.focus));
      const h = anyFocus > 0.001 ? COLLAPSED + (EXPANDED - COLLAPSED) * states[i].focus : COLLAPSED;
      const b = {left: T.margin, top: y, width: W - 2 * T.margin, height: h};
      y += h + L.gap;
      return b;
    }
    return {left: T.margin, top: L.top + i * (L.height + L.gap), width: W - 2 * T.margin, height: L.height};
  });
  return (
    <AbsoluteFill>
      <SceneExit dur={dur} frames={14}>
        <Appear at={2} dy={0} style={{position: 'absolute', ...L.kicker}}>
          <div style={kicker(f)}>{copy.offers.kicker}</div>
        </Appear>
        {copy.offers.items.map((item, i) => (
          <Card
            key={i}
            f={f}
            i={i}
            item={item}
            active={states[i].active}
            descOpacity={interpolate(states[i].focus, [0.6, 1], [0, 1], clamp)}
            drawAt={states[i].start}
            enterAt={4 + i * 6}
            box={boxes[i]}
          />
        ))}
      </SceneExit>
      <Thread d={`M-20 ${L.threadY}H${W + 20}`} draw={[0, 26]} retract={[dur - 18, dur]} />
    </AbsoluteFill>
  );
};
