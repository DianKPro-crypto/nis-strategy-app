import React from 'react';
import {
  AbsoluteFill, Audio, Easing, Img, Sequence,
  interpolate, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {
  FADE_TO_BLACK, FINAL_TITLE, FPS, IMAGES, OPENING_TITLE, TITLE_TEXT,
  flatShots, type CamH, type CamV,
} from './config/scenes';

/* ---------- Charte ---------- */
const INK = '#0B0B0C';
const GOLD = '#E3B34C';
const IVORY = '#F7F0E3';

/* ---------- Polices locales (aucun appel réseau au rendu) ---------- */
const pf = (f: string) => staticFile(`fonts/${f}.woff2`);
loadFont({family: 'Playfair Display', url: pf('playfair-display-latin-500-normal'), weight: '500'});
loadFont({family: 'Playfair Display', url: pf('playfair-display-latin-400-italic'), weight: '400', style: 'italic'});

type Format = 'h' | 'v';
const ease = Easing.bezier(0.37, 0, 0.63, 1);
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

/* ---------- Un plan ---------- */
type FlatShot = ReturnType<typeof flatShots>[number];

const ShotView: React.FC<{shot: FlatShot; format: Format; durFrames: number}> = ({shot, format, durFrames}) => {
  const frame = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  const meta = IMAGES[shot.img];
  const p = ease(clamp(frame / Math.max(1, durFrames - 1), 0, 1));
  const t = frame / FPS;
  const breathe = shot.breathe ? 1 + 0.006 * Math.sin((2 * Math.PI * t) / 5.5) : 1;
  const opacity = shot.xfade > 0
    ? interpolate(frame, [0, shot.xfade * FPS], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
    : 1;
  const src = staticFile(`scenes/${shot.img}.jpg`);
  const imgFilter = undefined; // saturation/contraste intégrés aux fichiers (tools/bake_grade.py)

  if (format === 'h') {
    const a = shot.h.from as CamH, b = shot.h.to as CamH;
    const s = lerp(a.s, b.s, p) * breathe;
    const fx = lerp(a.fx, b.fx, p), fy = lerp(a.fy, b.fy, p);
    const base = Math.max(W / meta.w, H / meta.h);
    const dw = meta.w * base * s, dh = meta.h * base * s;
    const left = clamp(W / 2 - fx * dw, W - dw, 0);
    const top = clamp(H / 2 - fy * dh, H - dh, 0);
    return (
      <AbsoluteFill style={{opacity}}>
        <Img src={src} style={{position: 'absolute', left, top, width: dw, height: dh, filter: imgFilter}} />
      </AbsoluteFill>
    );
  }

  // Vertical : bande intégrée sur fond flou dérivé de la même image.
  const a = shot.v.from as CamV, b = shot.v.to as CamV;
  const k = lerp(a.k, b.k, p) * breathe;
  const fx = lerp(a.fx, b.fx, p);
  const by = lerp(a.by ?? 0.5, b.by ?? 0.5, p);
  const dw = W * k, dh = dw * (meta.h / meta.w);
  const left = clamp(W / 2 - fx * dw, W - dw, 0);
  const isCover = dh >= H;
  const top = isCover ? clamp(H * by - dh / 2, H - dh, 0) : H * by - dh / 2;
  const feather = isCover ? undefined
    : 'linear-gradient(to bottom, transparent 0%, #000 7%, #000 93%, transparent 100%)';
  const bgScale = 1.02 + 0.04 * p;
  return (
    <AbsoluteFill style={{opacity}}>
      {!isCover && (
        <Img src={staticFile(`scenes/bg_${shot.img}.jpg`)}
          style={{position: 'absolute', inset: 0, width: W, height: H, transform: `scale(${bgScale})`}} />
      )}
      <Img src={src} style={{
        position: 'absolute', left, top, width: dw, height: dh, filter: imgFilter,
        WebkitMaskImage: feather, maskImage: feather,
      }} />
    </AbsoluteFill>
  );
};

/* ---------- Étalonnage : frais au début, chaleureux à la fin ---------- */
const Grade: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const w = interpolate(t, [0, 45, 150, 230, 266], [0, 0.15, 0.5, 0.85, 1], {extrapolateRight: 'clamp'});
  const cool = [72, 108, 168], warm = [226, 158, 78];
  const c = cool.map((v, i) => Math.round(lerp(v, warm[i], w)));
  return (
    <>
      <AbsoluteFill style={{backgroundColor: `rgb(${c.join(',')})`, mixBlendMode: 'soft-light', opacity: 0.17}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 70% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.30) 100%)'}} />
    </>
  );
};

/* ---------- Titre ---------- */
const TitleBlock: React.FC<{format: Format; size: number; align: 'center' | 'right'}> = ({format, size, align}) => (
  <div style={{textAlign: align, lineHeight: 1.04, textShadow: '0 2px 18px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.6)'}}>
    <div style={{fontFamily: 'Playfair Display', fontWeight: 500, fontSize: size, color: IVORY, letterSpacing: 0.5}}>
      {TITLE_TEXT[0]}
    </div>
    <div style={{fontFamily: 'Playfair Display', fontStyle: 'italic', fontWeight: 400, fontSize: size * 1.08, color: GOLD}}>
      {TITLE_TEXT[1]}
    </div>
    <div style={{
      height: 2, width: format === 'h' ? 120 : 110, background: GOLD, opacity: 0.9,
      margin: align === 'center' ? `${size * 0.32}px auto 0` : `${size * 0.32}px 0 0 auto`,
    }} />
  </div>
);

const OpeningTitle: React.FC<{format: Format}> = ({format}) => {
  const t = useCurrentFrame() / FPS;
  const o = interpolate(t, [OPENING_TITLE.holdUntil, OPENING_TITLE.out], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rise = interpolate(t, [0, OPENING_TITLE.out], [0, -10]);
  if (o <= 0) return null;
  if (format === 'h') {
    return (
      <AbsoluteFill style={{opacity: o}}>
        <AbsoluteFill style={{background: 'linear-gradient(to top, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.25) 32%, rgba(0,0,0,0) 55%)'}} />
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 150, transform: `translateY(${rise}px)`}}>
          <TitleBlock format={format} size={112} align="center" />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{opacity: o}}>
      <AbsoluteFill style={{background: 'linear-gradient(to top, rgba(0,0,0,0.0) 10%, rgba(0,0,0,0.5) 22%, rgba(0,0,0,0.5) 36%, rgba(0,0,0,0) 52%)'}} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 1240, transform: `translateY(${rise}px)`}}>
        <TitleBlock format={format} size={118} align="center" />
      </div>
    </AbsoluteFill>
  );
};

const FinalTitle: React.FC<{format: Format}> = ({format}) => {
  const t = useCurrentFrame() / FPS;
  const o = interpolate(t, [FINAL_TITLE.in, FINAL_TITLE.in + FINAL_TITLE.fadeIn], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rise = interpolate(t, [FINAL_TITLE.in, FINAL_TITLE.in + 4], [12, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  if (o <= 0) return null;
  if (format === 'h') {
    return (
      <AbsoluteFill style={{opacity: o}}>
        <AbsoluteFill style={{background: 'radial-gradient(ellipse 30% 34% at 84% 26%, rgba(0,0,0,0.42) 0%, rgba(0,0,0,0.22) 55%, rgba(0,0,0,0) 100%)'}} />
        <div style={{position: 'absolute', right: 86, top: 120, transform: `translateY(${rise}px)`}}>
          <TitleBlock format={format} size={92} align="right" />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{opacity: o}}>
      <AbsoluteFill style={{background: 'linear-gradient(to top, rgba(0,0,0,0) 12%, rgba(0,0,0,0.45) 20%, rgba(0,0,0,0.35) 34%, rgba(0,0,0,0) 46%)'}} />
      <div style={{position: 'absolute', left: 60, right: 60, top: 1330, transform: `translateY(${rise}px)`}}>
        <TitleBlock format={format} size={100} align="center" />
      </div>
    </AbsoluteFill>
  );
};

const FadeToBlack: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const o = interpolate(t, [FADE_TO_BLACK.start, FADE_TO_BLACK.end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)});
  return o > 0 ? <AbsoluteFill style={{backgroundColor: INK, opacity: o}} /> : null;
};

/* ---------- Film ---------- */
export const Film: React.FC<{format: Format}> = ({format}) => {
  const {durationInFrames} = useVideoConfig();
  const shots = flatShots();
  return (
    <AbsoluteFill style={{backgroundColor: INK}}>
      {shots.map((s, i) => {
        const from = Math.max(0, Math.round((s.start - s.xfade / 2) * FPS));
        const to = Math.min(durationInFrames, Math.round((s.end + s.nextXfade / 2) * FPS));
        return (
          <Sequence key={i} from={from} durationInFrames={to - from} name={`S${String(s.scene).padStart(2, '0')} ${s.img}`}>
            <ShotView shot={s} format={format} durFrames={to - from} />
          </Sequence>
        );
      })}
      <Grade />
      <OpeningTitle format={format} />
      <FinalTitle format={format} />
      <FadeToBlack />
      <Audio src={staticFile('audio/ici_commence_le_voyage.mp3')} />
    </AbsoluteFill>
  );
};
