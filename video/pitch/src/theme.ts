import {Easing} from 'remotion';
import brand from '../assets/brand.json';

// Brand tokens — DIAN K. PRO Charte chromatique V1.0 (assets/brand.json).
export const C = brand.palette;
export const METALLIC = brand.metallicGradient;

// Motion language: expo-out entrances, ease-in exits. No bounce, no elastic.
export const easeOut = Easing.bezier(0.22, 1, 0.36, 1);
export const easeIn = Easing.bezier(0.64, 0, 0.78, 0);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);
