import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {C} from './theme';
import {COPY, Lang} from './copy';
import {headline, kicker, metallicText} from './styles';
import {Grain} from './components/Grain';

// 1920×1080 thumbnail: portrait + headline (LinkedIn / YouTube custom cover).
export const Thumbnail: React.FC<{lang: Lang}> = ({lang}) => {
  const copy = COPY[lang];
  const x = 1150;
  const w = 600;
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 30% 45%, ${C.graphite} 0%, ${C.noir} 62%)`}}>
      <div
        style={{
          position: 'absolute',
          left: x,
          top: 140,
          width: w,
          height: 940,
          borderRadius: `${w / 2}px ${w / 2}px 0 0`,
          overflow: 'hidden',
          background: `radial-gradient(circle at 50% 30%, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 60%), ${C.anthracite}`,
        }}
      >
        <Img src={staticFile('portrait_cutout.png')} style={{position: 'absolute', width: 780, left: (w - 780) / 2, bottom: 0}} />
      </div>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <path d={`M-20 760H${x - 60}Q${x - 28} 760 ${x - 28} 728V${140 + w / 2}A${w / 2 + 28} ${w / 2 + 28} 0 0 1 ${x + w + 28} ${140 + w / 2}V1100`} stroke={C.or} strokeWidth={3} fill="none" />
      </svg>
      <div style={{position: 'absolute', left: 120, bottom: 1080 - 760 + 52, width: 980}}>
        <div style={headline(94)}>{copy.hook.lead}</div>
        <div style={{...headline(94), fontStyle: 'italic', ...metallicText, backgroundPosition: '30% 0', paddingBottom: '0.08em'}}>{copy.hook.accent}</div>
      </div>
      <div style={{position: 'absolute', left: 120, top: 804, display: 'flex', alignItems: 'center', gap: 26}}>
        <Img src={staticFile('logo_monogram.png')} style={{height: 84}} />
        <div style={{display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 860}}>
          <div style={{...kicker('landscape', C.ivoire), letterSpacing: '0.14em'}}>{copy.reveal.name}</div>
          <div style={{...kicker('landscape', C.sable), letterSpacing: '0.04em', textTransform: 'none', fontWeight: 500}}>{copy.reveal.title}</div>
        </div>
      </div>
      <Grain opacity={0.03} />
    </AbsoluteFill>
  );
};
