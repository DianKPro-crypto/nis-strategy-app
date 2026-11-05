import React from 'react';
import {Composition} from 'remotion';
import {Film} from './Film';
import {DURATION_FRAMES, FPS} from './config/scenes';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Voyage16x9" component={Film} durationInFrames={DURATION_FRAMES} fps={FPS}
      width={1920} height={1080} defaultProps={{format: 'h' as const}} />
    <Composition id="Voyage9x16" component={Film} durationInFrames={DURATION_FRAMES} fps={FPS}
      width={1080} height={1920} defaultProps={{format: 'v' as const}} />
  </>
);
