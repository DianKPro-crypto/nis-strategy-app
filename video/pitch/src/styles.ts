import React from 'react';
import {C} from './theme';
import {DISPLAY, TEXT} from './fonts';
import {Format, TYPE} from './format';

export type SceneProps = {dur: number; copy: import('./copy').Copy};

// Labels: uppercase, +12 % tracking. In 9:16 the 54 px minimum makes uppercase
// too wide for the column, so kickers switch to sentence case there.
export const kicker = (f: Format, color: string = C.or): React.CSSProperties => ({
  fontFamily: TEXT,
  fontWeight: 600,
  fontSize: TYPE[f].label,
  letterSpacing: f === 'portrait' ? '0.01em' : '0.12em',
  textTransform: f === 'portrait' ? 'none' : 'uppercase',
  color,
  lineHeight: 1.1,
});

export const headline = (size: number, color: string = C.ivoire): React.CSSProperties => ({
  fontFamily: DISPLAY,
  fontWeight: 400,
  fontSize: size,
  lineHeight: 1.08,
  letterSpacing: '-0.01em',
  color,
  textWrap: 'balance',
} as React.CSSProperties);

export const body = (size: number, color: string = C.ivoire, weight = 500): React.CSSProperties => ({
  fontFamily: TEXT,
  fontWeight: weight,
  fontSize: size,
  lineHeight: 1.22,
  color,
  textWrap: 'balance',
} as React.CSSProperties);

export const metallicText: React.CSSProperties = {
  backgroundImage: 'linear-gradient(115deg, #A87C33 0%, #D4A44C 30%, #ECBA5B 46%, #F7E2AE 50%, #ECBA5B 54%, #D4A44C 70%, #A87C33 100%)',
  backgroundSize: '250% 100%',
  WebkitBackgroundClip: 'text',
  backgroundClip: 'text',
  color: 'transparent',
};
