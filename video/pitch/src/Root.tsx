import React from 'react';
import {Composition, Still} from 'remotion';
import {Pitch, PitchProps} from './Pitch';
import {Thumbnail} from './Thumbnail';
import {TOTAL_FRAMES} from './timeline';
import {FPS} from './theme';
import './fonts';

const FORMATS = [
  {id: '16x9', width: 1920, height: 1080},
  {id: '1x1', width: 1080, height: 1080},
  {id: '9x16', width: 1080, height: 1920},
] as const;

export const RemotionRoot: React.FC = () => (
  <>
    {(['en', 'fr'] as const).map((lang) =>
      FORMATS.map((fm) => (
        <Composition
          key={`${lang}-${fm.id}`}
          id={`Pitch-${lang.toUpperCase()}-${fm.id}`}
          component={Pitch}
          durationInFrames={TOTAL_FRAMES}
          fps={FPS}
          width={fm.width}
          height={fm.height}
          defaultProps={{lang, music: true, voiceover: false} satisfies PitchProps}
        />
      )),
    )}
    <Still id="Thumbnail-EN" component={Thumbnail} width={1920} height={1080} defaultProps={{lang: 'en' as const}} />
    <Still id="Thumbnail-FR" component={Thumbnail} width={1920} height={1080} defaultProps={{lang: 'fr' as const}} />
  </>
);
