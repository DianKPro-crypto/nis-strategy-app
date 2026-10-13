import React from 'react';
import {AbsoluteFill, useVideoConfig} from 'remotion';
import {C} from '../theme';
import {DISPLAY, NUMERIC} from '../fonts';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear, SceneExit} from '../components/Appear';
import {Counter} from '../components/Counter';
import {LabelPos, MapAfricaME} from '../components/MapAfricaME';
import {body, kicker, SceneProps} from '../styles';

// Scene 4 — Proof in numbers. Counters roll in on the beat; the five NIS.COST
// countries light up on the map when "5" lands; Casablanca (base) pulses.
const ROW_GAP = 30; // frames between counters

export const S4Proof: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const {width: W, height: H} = useVideoConfig();
  const L = pick(f, {
    landscape: {
      kicker: {left: T.margin, top: 96},
      list: {left: T.margin, top: 196, width: 780},
      num: 120,
      numW: 230,
      rowGap: 40,
      map: {left: 870, top: 50, w: 930, h: 980},
      mapLabels: true,
      threadY: 160,
    },
    square: {
      kicker: {left: T.margin, top: 78},
      list: {left: T.margin, top: 180, width: 470},
      num: 88,
      numW: 140,
      rowGap: 26,
      map: {left: 470, top: 150, w: 600, h: 880},
      mapLabels: false,
      threadY: 140,
    },
    portrait: {
      kicker: {left: T.margin, top: 268},
      list: {left: T.margin, top: 930, width: 900},
      num: 92,
      numW: 170,
      rowGap: 18,
      map: {left: 60, top: 372, w: 520, h: 540},
      mapLabels: true,
      threadY: 352,
    },
  });
  const labelPos: Record<string, LabelPos> = {
    '262': {dx: 70, dy: -40, anchor: 'start'},
    '140': {dx: -40, dy: -90, anchor: 'end'},
    '108': {dx: -80, dy: 50, anchor: 'end'},
    '174': {dx: -40, dy: 56, anchor: 'end'},
    '450': {dx: -10, dy: 140, anchor: 'end'},
  };
  const highlightAt = 14 + ROW_GAP + 6;
  return (
    <AbsoluteFill>
      <SceneExit dur={dur} frames={14}>
        <div style={{position: 'absolute', left: L.map.left, top: L.map.top}}>
          <MapAfricaME
            w={L.map.w}
            h={L.map.h}
            at={4}
            highlightAt={highlightAt}
            labels={
              f === 'landscape'
                ? copy.proof.countries
                : f === 'portrait'
                  ? copy.proof.countriesShort
                  : Object.fromEntries(Object.keys(copy.proof.countries).map((k) => [k, '']))
            }
            labelPos={labelPos}
            legend={f === 'portrait' ? {x: 600, y: 130, gap: 70} : undefined}
            baseLabel={f === 'square' ? '' : copy.proof.base}
            basePos={f === 'portrait' ? {dx: 22, dy: -30, anchor: 'start'} : {dx: -26, dy: 0, anchor: 'end'}}
            fontSize={T.label}
            spacing={f === 'landscape' ? 13 : 11}
          />
        </div>
        {f === 'square' ? (
          <div style={{position: 'absolute', left: L.map.left - 2, top: 0, width: 300, height: H, background: `linear-gradient(90deg, ${C.noir} 0%, rgba(10,10,10,0.85) 35%, rgba(10,10,10,0) 100%)`}} />
        ) : null}
        <Appear at={4} dy={0} style={{position: 'absolute', ...L.kicker}}>
          <div style={kicker(f)}>{copy.proof.kicker}</div>
        </Appear>
        <div style={{position: 'absolute', ...L.list, display: 'flex', flexDirection: 'column', gap: L.rowGap}}>
          {copy.proof.items.map((it, i) => {
            const at = 14 + i * ROW_GAP;
            return (
              <Appear key={i} at={at} dx={-30} dy={0}>
                <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
                  <div style={{width: L.numW, flexShrink: 0, fontFamily: DISPLAY, fontWeight: 500, fontSize: L.num, lineHeight: 1, color: C.champagne, ...NUMERIC}}>
                    <Counter at={at} value={it.value} suffix={it.suffix} dur={26} />
                  </div>
                  <div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
                    <div style={body(T.label, C.ivoire, 500)}>{it.label}</div>

                  </div>
                </div>
              </Appear>
            );
          })}
        </div>
      </SceneExit>
      <Thread d={`M-20 ${L.threadY}H${f === 'landscape' ? 860 : W + 20}`} draw={[0, 30]} retract={[dur - 18, dur]} />
    </AbsoluteFill>
  );
};
