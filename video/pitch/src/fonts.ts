import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fonts are bundled in assets/fonts (SIL OFL) so renders are deterministic and
// work offline. Playfair Display = headlines & large numbers; Inter = text.
export const DISPLAY = 'Playfair Display';
export const TEXT = 'Inter';

const faces: {family: string; file: string; weight: string; style: 'normal' | 'italic'}[] = [
  {family: DISPLAY, file: 'playfair-display-latin-400-normal.woff2', weight: '400', style: 'normal'},
  {family: DISPLAY, file: 'playfair-display-latin-500-normal.woff2', weight: '500', style: 'normal'},
  {family: DISPLAY, file: 'playfair-display-latin-600-normal.woff2', weight: '600', style: 'normal'},
  {family: DISPLAY, file: 'playfair-display-latin-400-italic.woff2', weight: '400', style: 'italic'},
  {family: DISPLAY, file: 'playfair-display-latin-500-italic.woff2', weight: '500', style: 'italic'},
  {family: TEXT, file: 'inter-latin-400-normal.woff2', weight: '400', style: 'normal'},
  {family: TEXT, file: 'inter-latin-500-normal.woff2', weight: '500', style: 'normal'},
  {family: TEXT, file: 'inter-latin-600-normal.woff2', weight: '600', style: 'normal'},
];

for (const f of faces) {
  loadFont({family: f.family, url: staticFile(`fonts/${f.file}`), weight: f.weight, style: f.style, format: 'woff2'});
}

// Lining, tabular figures so counters do not jitter while they roll.
export const NUMERIC: React.CSSProperties = {fontVariantNumeric: 'lining-nums tabular-nums'};
