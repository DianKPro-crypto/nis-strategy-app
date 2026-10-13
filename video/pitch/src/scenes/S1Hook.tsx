import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C} from '../theme';
import {DISPLAY} from '../fonts';
import {pick, TYPE, useFormat} from '../format';
import {Thread} from '../components/Thread';
import {SceneExit} from '../components/Appear';
import {headline, kicker, metallicText, SceneProps} from '../styles';

// Scene 1 — Hook. Frame 0 is a complete cover (it doubles as the thumbnail /
// WhatsApp poster frame): the question is fully legible from the first image.
export const S1Hook: React.FC<SceneProps> = ({dur, copy}) => {
  const f = useFormat();
  const T = TYPE[f];
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const L = pick(f, {
    landscape: {threadY: 700, maxW: 1500, mono: 84, size: T.display},
    square: {threadY: 700, maxW: 900, mono: 70, size: 82},
    portrait: {threadY: 1290, maxW: 900, mono: 92, size: T.display},
  });
  const push = interpolate(frame, [0, dur], [1, 1.03]);
  const shimmer = interpolate(frame, [6, 70], [100, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 28% 42%, ${C.graphite} 0%, ${C.noir} 62%)`}}>
      <SceneExit dur={dur} frames={16}>
        <div
          style={{
            position: 'absolute',
            left: T.margin,
            width: L.maxW,
            bottom: H - L.threadY + 52,
            transform: `scale(${push})`,
            transformOrigin: 'left bottom',
          }}
        >
          <div style={headline(L.size)}>{copy.hook.lead}</div>
          <div style={{...headline(L.size), fontStyle: 'italic', ...metallicText, backgroundPosition: `${shimmer}% 0`, paddingBottom: '0.08em'}}>
            {copy.hook.accent}
          </div>
        </div>
        <div style={{position: 'absolute', left: T.margin, top: L.threadY + 44, display: 'flex', alignItems: 'center', gap: 26}}>
          <Img src={staticFile('logo_monogram.png')} style={{height: L.mono}} />
          <div style={{...kicker(f, C.sable), letterSpacing: '0.14em'}}>{copy.hook.signature}</div>
        </div>
      </SceneExit>
      <Thread d={`M-20 ${L.threadY}H${W + 20}`} draw={[0, 80]} initial={0.56} retract={[dur - 22, dur]} />
    </AbsoluteFill>
  );
};
