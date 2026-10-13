import {useVideoConfig} from 'remotion';

export type Format = 'landscape' | 'square' | 'portrait';

export const useFormat = (): Format => {
  const {width, height} = useVideoConfig();
  if (width > height) return 'landscape';
  if (width === height) return 'square';
  return 'portrait';
};

export const pick = <T,>(f: Format, v: Record<Format, T>): T => v[f];

// Type scale. Minimum on-screen text: 42 px at 1080p, 54 px in 9:16.
export const TYPE: Record<Format, {display: number; h1: number; h2: number; h3: number; num: number; body: number; label: number; margin: number}> = {
  landscape: {display: 116, h1: 96, h2: 80, h3: 60, num: 116, body: 46, label: 42, margin: 120},
  square: {display: 92, h1: 80, h2: 68, h3: 54, num: 100, body: 44, label: 42, margin: 90},
  portrait: {display: 108, h1: 96, h2: 80, h3: 64, num: 120, body: 56, label: 54, margin: 90},
};

// 9:16 text safe zone (WhatsApp / Stories UI): y 260 – 1600.
export const SAFE_TOP = 260;
export const SAFE_BOTTOM = 1600;
