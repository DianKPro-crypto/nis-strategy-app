import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {C} from '../theme';
import {TEXT} from '../fonts';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear, SceneExit} from '../components/Appear';
import {Photo} from '../components/Photo';
import {Vignette} from '../components/Grain';
import {body, kicker, SceneProps} from '../styles';

// Scene 7 — Trust. Institutions as TEXT wordmarks in the video's own typeface,
// uniform ivory, slow horizontal drift. No logos.
export const S7Trust: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const L = pick(f, {
    landscape: {
      photo: {left: 0, top: 0, width: 780, height: H},
      pos: '55% 50%',
      fade: `linear-gradient(270deg, ${C.noir} 0%, rgba(10,10,10,0.7) 14%, rgba(10,10,10,0) 45%)`,
      text: {left: 860, top: 220, width: 960},
      mark: 56,
      min: 46,
      threadX: 860,
    },
    square: {
      photo: {left: 0, top: 0, width: W, height: 420},
      pos: '50% 40%',
      fade: `linear-gradient(0deg, ${C.noir} 0%, rgba(10,10,10,0.6) 22%, rgba(10,10,10,0) 55%)`,
      text: {left: T.margin, top: 452, width: W - 2 * T.margin},
      mark: 50,
      min: 44,
      threadX: 0,
    },
    portrait: {
      photo: {left: 0, top: 0, width: W, height: 760},
      pos: '50% 40%',
      fade: `linear-gradient(0deg, ${C.noir} 0%, rgba(10,10,10,0.6) 20%, rgba(10,10,10,0) 50%)`,
      text: {left: T.margin, top: 790, width: W - 2 * T.margin},
      mark: 62,
      min: 54,
      threadX: 0,
    },
  });
  const drift = interpolate(frame, [0, dur], [26, -26]);
  const sep = <span style={{color: C.or}}>{'\u00a0· '}</span>;
  return (
    <AbsoluteFill>
      <SceneExit dur={dur} frames={14}>
        <Appear at={0} dur={22} dy={0}>
          <div style={{position: 'absolute', ...L.photo}}>
            <Photo src="field/IMG_3338.jpg" position={L.pos} dur={dur} filter="saturate(0.85) brightness(0.95)" style={{inset: 0}} />
            <div style={{position: 'absolute', inset: 0, background: L.fade}} />
            <Vignette strength={0.25} />
          </div>
        </Appear>
        <div style={{position: 'absolute', ...L.text, transform: `translateX(${drift}px)`, display: 'flex', flexDirection: 'column', gap: f === 'portrait' ? 26 : 22}}>
          <Appear at={4} dy={0}>
            <div style={kicker(f)}>{copy.trust.kicker}</div>
          </Appear>
          <div style={{display: 'flex', flexWrap: 'wrap', columnGap: L.mark * 0.75, rowGap: L.mark * 0.28}}>
            {copy.trust.agencies.map((a, i) => (
              <Appear key={a} at={10 + i * 4} dy={14}>
                <span style={{fontFamily: TEXT, fontWeight: 600, fontSize: L.mark, letterSpacing: '0.02em', color: C.ivoire, lineHeight: 1.15, whiteSpace: 'nowrap'}}>{a}</span>
              </Appear>
            ))}
          </div>
          <Appear at={44} dy={0}>
            <div style={{width: 140, height: 2, background: C.or, margin: `${L.mark * 0.2}px 0`}} />
          </Appear>
          <Appear at={48} dy={12}>
            <div style={{...kicker(f, C.sable), letterSpacing: '0.1em'}}>{copy.trust.ministriesLabel}</div>
          </Appear>
          <Appear at={54} dy={12}>
            <div style={{...body(L.min, C.ivoire, 500), lineHeight: 1.3}}>
              {copy.trust.ministries.map((m, i) => (
                <React.Fragment key={m}>
                  {i > 0 ? sep : null}
                  <span style={{whiteSpace: 'nowrap'}}>{m}</span>
                </React.Fragment>
              ))}
            </div>
          </Appear>
        </div>
      </SceneExit>
      <Thread
        d={f === 'landscape' ? `M-20 ${H - 120}H${W + 20}` : `M-20 ${f === 'square' ? 420 : 760}H${W + 20}`}
        draw={[0, 28]}
        retract={[dur - 18, dur]}
      />
    </AbsoluteFill>
  );
};
