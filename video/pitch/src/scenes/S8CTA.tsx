import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import contact from '../../assets/contact.json';
import {C, easeOut} from '../theme';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {Appear} from '../components/Appear';
import {QR} from '../components/QR';
import {MailIcon, PhoneIcon, ProfileIcon} from '../components/Icons';
import {body, headline, metallicText, SceneProps} from '../styles';

// Scene 8 — Call to action + Dian K Pro animated signature. The thread closes
// into a circle around the DK monogram, which reveals with a metallic sheen
// (charter: the metallic gradient is reserved for logo animations). The final
// composition holds ≥ 3 s.
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const circlePath = (cx: number, cy: number, r: number) => `M-20 ${cy}H${cx - r}A${r} ${r} 0 1 1 ${cx + r} ${cy}A${r} ${r} 0 1 1 ${cx - r} ${cy}`;

const Monogram: React.FC<{h: number; at: number}> = ({h, at}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + 24], [0, 1], {...clamp, easing: easeOut});
  const sheen = interpolate(frame, [at + 10, at + 50], [-60, 160], clamp);
  const w = h * (490 / 449);
  const mask: React.CSSProperties = {
    WebkitMaskImage: `url(${staticFile('logo_monogram.png')})`,
    WebkitMaskSize: '100% 100%',
    maskImage: `url(${staticFile('logo_monogram.png')})`,
    maskSize: '100% 100%',
  };
  return (
    <div style={{position: 'relative', width: w, height: h, opacity: p, transform: `scale(${0.94 + 0.06 * p})`}}>
      <Img src={staticFile('logo_monogram.png')} style={{width: w, height: h}} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          ...mask,
          background: `linear-gradient(115deg, rgba(255,255,255,0) ${sheen - 18}%, rgba(255,244,214,0.85) ${sheen}%, rgba(255,255,255,0) ${sheen + 18}%)`,
          mixBlendMode: 'screen',
        }}
      />
    </div>
  );
};

export const S8CTA: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const L = pick(f, {
    landscape: {
      circle: {cx: 430, cy: 400, r: 205},
      under: {top: 650},
      col: {left: 860, top: 150, width: 960},
      head: 80,
      invite: 46,
      qrSize: 190,
      li: contact.linkedin.replace('linkedin.com/', ''),
      stack: false,
    },
    square: {
      circle: {cx: 540, cy: 172, r: 104},
      under: {top: 292},
      col: {left: T.margin, top: 362, width: W - 2 * T.margin},
      head: 62,
      invite: 44,
      qrSize: 170,
      li: contact.linkedin.replace('linkedin.com/', ''),
      stack: true,
    },
    portrait: {
      circle: {cx: 540, cy: 418, r: 148},
      under: {top: 588},
      col: {left: T.margin, top: 680, width: W - 2 * T.margin},
      head: 80,
      invite: 56,
      qrSize: 180,
      li: contact.linkedin.replace('linkedin.com/', ''),
      stack: true,
    },
  });
  const {cx, cy, r} = L.circle;
  const shimmer = interpolate(frame, [26, 80], [100, 0], clamp);
  const iconSize = T.label * 1.15;
  const contactRows = [
    {Icon: MailIcon, text: contact.email},
    {Icon: PhoneIcon, text: contact.phone},
    {Icon: ProfileIcon, text: L.li},
  ];
  const contactAt = 78;
  // Long (FR) CTA lines get a smaller size in 1:1 so the contact row keeps its room.
  const head = f === 'square' && copy.cta.lines.some((l) => l.length > 30) ? 54 : L.head;
  return (
    <AbsoluteFill>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${(cx / W) * 100}% ${(cy / H) * 100}%, ${C.graphite} 0%, ${C.noir} 55%)`,
          opacity: interpolate(frame, [0, 14], [0, 1], clamp),
        }}
      />
      <Thread d={circlePath(cx, cy, r)} draw={[0, 44]} width={3} />
      <div style={{position: 'absolute', left: cx, top: cy, transform: 'translate(-50%, -50%)'}}>
        <Monogram h={r * 1.1} at={22} />
      </div>
      {!L.stack ? (
        <div style={{position: 'absolute', left: cx - 400, width: 800, top: L.under.top, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, textAlign: 'center'}}>
          <Appear at={40} dy={14}>
            <div style={{...headline(54), fontWeight: 500}}>{copy.reveal.name}</div>
          </Appear>
          <Appear at={50} dy={10}>
            <div style={{...headline(T.label, C.champagne), fontStyle: 'italic'}}>{copy.cta.tagline}</div>
          </Appear>
        </div>
      ) : (
        <Appear at={40} dy={10} style={{position: 'absolute', left: 0, width: W, top: L.under.top, textAlign: 'center'}}>
          <div style={{...headline(f === 'portrait' ? 60 : 48), fontWeight: 500}}>{copy.reveal.name}</div>
        </Appear>
      )}
      <div
        style={{
          position: 'absolute',
          ...L.col,
          display: 'flex',
          flexDirection: 'column',
          gap: f === 'landscape' ? 0 : 0,
          alignItems: L.stack ? 'center' : 'flex-start',
          textAlign: L.stack ? 'center' : 'left',
        }}
      >
        <Appear at={14} dy={20}>
          <div style={headline(head)}>{copy.cta.lines[0]}</div>
        </Appear>
        <Appear at={30} dy={20}>
          <div style={{...headline(head), fontStyle: 'italic', ...metallicText, backgroundPosition: `${shimmer}% 0`, paddingBottom: '0.06em'}}>
            {copy.cta.lines[1]}
          </div>
        </Appear>
        <Appear at={56} dy={16} style={{marginTop: f === 'landscape' ? 34 : 22}}>
          <div style={body(L.invite, C.ivoire, 500)}>{copy.cta.invite}</div>
        </Appear>
        <div
          style={{
            marginTop: f === 'landscape' ? 52 : f === 'square' ? 32 : 50,
            display: 'flex',
            alignItems: 'flex-start',
            gap: f === 'portrait' ? 34 : 48,
            alignSelf: L.stack ? 'center' : 'flex-start',
          }}
        >
          <div style={{display: 'flex', flexDirection: 'column', gap: f === 'portrait' ? 18 : 14}}>
            {contactRows.map(({Icon, text}, i) => (
              <Appear key={text} at={contactAt + i * 8} dx={-20} dy={0}>
                <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
                  <Icon size={iconSize} progress={interpolate(frame, [contactAt + i * 8, contactAt + i * 8 + 24], [0, 1], clamp)} />
                  <span style={{...body(T.label, C.ivoire, 500), whiteSpace: 'nowrap'}}>{text}</span>
                </div>
              </Appear>
            ))}
          </div>
          <Appear at={contactAt + 30} dy={0}>
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
              <div style={{borderRadius: 8, overflow: 'hidden', boxShadow: `0 0 0 2px ${C.or}`}}>
                <QR value={contact.linkedinUrl} size={L.qrSize} />
              </div>
              <span style={body(T.label, C.sable, 500)}>{copy.cta.scan}</span>
            </div>
          </Appear>
        </div>
      </div>
    </AbsoluteFill>
  );
};
