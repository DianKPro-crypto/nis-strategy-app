import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, easeIn, easeOut} from '../theme';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear} from '../components/Appear';
import {body, headline, SceneProps} from '../styles';

// Scene 3 — The reveal. Ivory wipes in along the thread; the thread draws an
// arch around the portrait; slow 3 % push-in.
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const archPath = (x: number, w: number, top: number, base: number, pad: number, W: number, entryY: number) => {
  const l = x - pad;
  const r = x + w + pad;
  const R = w / 2 + pad;
  const cy = top + w / 2;
  const k = 36; // corner radius
  return [
    `M-20 ${entryY}`,
    `H${l - k}`,
    `Q${l} ${entryY} ${l} ${entryY - k}`,
    `V${cy}`,
    `A${R} ${R} 0 0 1 ${r} ${cy}`,
    `V${base - k}`,
    `Q${r} ${base} ${r + k} ${base}`,
    `H${W + 20}`,
  ].join('');
};

export const S3Reveal: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const L = pick(f, {
    landscape: {
      panel: {x: 1080, w: 620, top: 130, bottom: H},
      cut: 780,
      entryY: 905,
      base: H + 60,
      text: {left: T.margin, top: 0, bottom: 0, width: 860, justify: 'center' as const, align: 'flex-start' as const, textAlign: 'left' as const},
      name: 100,
    },
    square: {
      panel: {x: 330, w: 420, top: 60, bottom: 640},
      cut: 520,
      entryY: 668,
      base: 668,
      text: {left: T.margin, top: 700, bottom: 60, width: W - 2 * T.margin, justify: 'flex-start' as const, align: 'center' as const, textAlign: 'center' as const},
      name: 76,
    },
    portrait: {
      panel: {x: 210, w: 660, top: 280, bottom: 1060},
      cut: 820,
      entryY: 1088,
      base: 1088,
      text: {left: T.margin, top: 1130, bottom: H - 1600, width: W - 2 * T.margin, justify: 'flex-start' as const, align: 'center' as const, textAlign: 'center' as const},
      name: 92,
    },
  });
  const wipeIn = interpolate(frame, [0, 18], [100, 0], {...clamp, easing: easeOut});
  const wipeOut = interpolate(frame, [dur - 16, dur], [0, 100], {...clamp, easing: easeIn});
  const rise = interpolate(frame, [10, 44], [0, 1], {...clamp, easing: easeOut});
  const push = interpolate(frame, [0, dur], [1, 1.03]);
  const {x, w, top, bottom} = L.panel;
  const cutH = L.cut / (1122 / 1402);
  // Frame from the head: keep ~9 % of the arch width as head-room under the arch
  // top (head top sits at ~6.8 % of the source image), let the chest run off the
  // bottom of the panel when needed.
  const panelH = bottom - top;
  const cutTop = Math.max(w * 0.09 - 0.068 * cutH, panelH - cutH);
  const pad = f === 'landscape' ? 30 : 22;
  return (
    <AbsoluteFill style={{clipPath: `inset(0 ${wipeIn}% 0 ${wipeOut}%)`, background: C.ivoire}}>
      <div
        style={{
          position: 'absolute',
          left: x,
          top,
          width: w,
          height: bottom - top,
          borderRadius: `${w / 2}px ${w / 2}px 0 0`,
          overflow: 'hidden',
          background: `radial-gradient(circle at 50% 30%, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 60%), ${C.sable}`,
          opacity: interpolate(frame, [6, 24], [0, 1], clamp),
        }}
      >
        <Img
          src={staticFile('portrait_cutout.png')}
          style={{
            position: 'absolute',
            width: L.cut,
            height: cutH,
            left: (w - L.cut) / 2,
            top: cutTop,
            opacity: rise,
            transform: `translateY(${(1 - rise) * 70}px) scale(${push})`,
            transformOrigin: '50% 100%',
          }}
        />
      </div>
      <Thread d={archPath(x, w, top, L.base, pad, W, L.entryY)} draw={[4, 58]} color={C.orProfond} width={3} />
      <div
        style={{
          position: 'absolute',
          left: L.text.left,
          top: L.text.top,
          bottom: L.text.bottom,
          width: L.text.width,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: L.text.justify,
          alignItems: L.text.align,
          textAlign: L.text.textAlign,
          gap: f === 'landscape' ? 30 : 18,
        }}
      >
        <Appear at={26} dy={26}>
          <div style={{...headline(L.name, C.graphite), fontWeight: 500}}>{copy.reveal.name}</div>
        </Appear>
        <Appear at={34} dy={0}>
          <div style={{width: interpolate(frame, [34, 54], [0, 140], {...clamp, easing: easeOut}), height: 3, background: C.orProfond}} />
        </Appear>
        <Appear at={40} dy={20}>
          <div style={{...body(f === 'portrait' ? 58 : f === 'square' ? 46 : 56, C.graphite, 500), maxWidth: f === 'landscape' ? 760 : undefined}}>
            {copy.reveal.title}
          </div>
        </Appear>
        <Appear at={52} dy={16}>
          <div style={body(T.label, C.anthracite, 500)}>
            {copy.reveal.base.split('|').map((part, i) => (
              <React.Fragment key={i}>
                {i > 0 ? <span style={{color: C.orProfond}}>{'\u00a0· '}</span> : null}
                <span style={{whiteSpace: 'nowrap'}}>{part}</span>
              </React.Fragment>
            ))}
          </div>
        </Appear>
      </div>
    </AbsoluteFill>
  );
};
