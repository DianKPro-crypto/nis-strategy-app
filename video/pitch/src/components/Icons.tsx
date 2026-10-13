import React from 'react';
import {C} from '../theme';

// Line icons drawn in SVG (no stock icons). `progress` 0 -> 1 draws the strokes.
type IconProps = {size: number; progress?: number; color?: string; stroke?: number};

const Draw: React.FC<IconProps & {paths: string[]}> = ({size, progress = 1, color = C.or, stroke = 2.4, paths}) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    {paths.map((d, i) => {
      // stagger strokes slightly so the icon "writes" itself
      const local = Math.max(0, Math.min(1, progress * 1.3 - (i / paths.length) * 0.3));
      return (
        <path
          key={i}
          d={d}
          pathLength={1}
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray="1 1"
          strokeDashoffset={1 - local}
        />
      );
    })}
  </svg>
);

export const KeyIcon: React.FC<IconProps> = (p) => (
  <Draw {...p} paths={['M9 32a11 11 0 1 0 22 0a11 11 0 1 0 -22 0', 'M16 32a4 4 0 1 0 8 0a4 4 0 1 0 -8 0', 'M31 32H56', 'M48 32V41', 'M55 32V39']} />
);

export const BlueprintIcon: React.FC<IconProps> = (p) => (
  <Draw
    {...p}
    paths={['M10 12H54V52H10Z', 'M18 20H36V36H18Z', 'M36 28H46V44H26V36', 'M18 46H28', 'M18 44V48', 'M28 44V48', 'M46 16L50 20']}
  />
);

export const RootsIcon: React.FC<IconProps> = (p) => (
  <Draw
    {...p}
    paths={[
      'M8 34H56',
      'M32 34V14',
      'M32 24C24 24 20 18 20 11C27 11 32 16 32 24',
      'M32 20C40 20 44 14 44 8C37 8 32 12 32 20',
      'M32 34V56',
      'M32 40C28 44 22 46 18 52',
      'M32 42C36 46 42 48 46 54',
    ]}
  />
);

export const MailIcon: React.FC<IconProps> = (p) => <Draw {...p} paths={['M10 18H54V46H10Z', 'M10 18L32 34L54 18']} />;

export const PhoneIcon: React.FC<IconProps> = (p) => (
  <Draw {...p} paths={['M22 10h8l4 10l-5 4c2 6 6 10 12 12l4 -5l10 4v8c0 2 -2 4 -4 4C30 47 17 34 18 14c0 -2 2 -4 4 -4z']} />
);

export const ProfileIcon: React.FC<IconProps> = (p) => (
  <Draw
    {...p}
    paths={[
      'M14 12H50a4 4 0 0 1 4 4V48a4 4 0 0 1 -4 4H14a4 4 0 0 1 -4 -4V16a4 4 0 0 1 4 -4Z',
      'M26 26a6 6 0 1 0 12 0a6 6 0 1 0 -12 0',
      'M20 44c2 -7 8 -10 12 -10s10 3 12 10',
    ]}
  />
);

export const OFFER_ICONS = [KeyIcon, BlueprintIcon, RootsIcon];
