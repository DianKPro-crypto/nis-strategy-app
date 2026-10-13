import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';

// Real field photograph with a slow push-in. Readability comes from localised
// gradients placed by the scene, never from a heavy global veil (≤ 35 %).
export const Photo: React.FC<{
  src: string;
  position?: string;
  dur: number;
  zoom?: [number, number];
  filter?: string;
  style?: React.CSSProperties;
}> = ({src, position = '50% 50%', dur, zoom = [1.0, 1.06], filter, style}) => {
  const frame = useCurrentFrame();
  const s = interpolate(frame, [0, dur], zoom);
  return (
    <div style={{position: 'absolute', overflow: 'hidden', ...style}}>
      <Img
        src={staticFile(src)}
        style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: position, transform: `scale(${s})`, filter}}
      />
    </div>
  );
};
