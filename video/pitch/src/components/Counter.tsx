import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {easeOut} from '../theme';
import {fmt} from '../copy';

export const useCount = (at: number, dur: number, from: number, to: number, decimals = 0) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [at, at + dur], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: easeOut});
  const k = Math.pow(10, decimals);
  return Math.round(v * k) / k;
};

export const Counter: React.FC<{
  at: number;
  value: number;
  from?: number;
  dur?: number;
  decimals?: number;
  decimal?: string;
  suffix?: string;
  style?: React.CSSProperties;
}> = ({at, value, from = 0, dur = 30, decimals = 0, decimal = '.', suffix = '', style}) => {
  const v = useCount(at, dur, from, value, decimals);
  return (
    <span style={style}>
      {fmt(v, decimals, decimal)}
      {suffix}
    </span>
  );
};
