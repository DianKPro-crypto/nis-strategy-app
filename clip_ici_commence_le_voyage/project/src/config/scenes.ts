/**
 * « Ici commence le voyage » — configuration du montage.
 *
 * Toutes les heures sont en secondes, mesurées sur la chanson originale
 * (ICI_COMMENCE_LE_VOYAGE.mp3, 266,28 s). Les coupes de scène tombent dans
 * les respirations entre les phrases chantées (alignement mot à mot Suno).
 *
 * Cadrage 16:9 (h) : l'image couvre le cadre ; s = zoom (1 = couverture
 * minimale), fx/fy = point de l'image (0–1) placé au centre du cadre.
 * Cadrage 9:16 (v) : l'image est intégrée en bande sur un fond flou dérivé ;
 * k = largeur de la bande / largeur du cadre, fx = point horizontal centré,
 * by = centre vertical de la bande (0–1 de la hauteur).
 */

export const FPS = 25;
export const SONG_DURATION_S = 266.28; // durée réelle du fichier audio
export const DURATION_FRAMES = Math.round(SONG_DURATION_S * FPS); // 6657

export type ImageId =
  | 'scene_01' | 'scene_02' | 'scene_03' | 'scene_04' | 'scene_05'
  | 'scene_06' | 'scene_07' | 'scene_08' | 'scene_09' | 'scene_10'
  | 'scene_11' | 'scene_12' | 'scene_13' | 'portrait_ref';

/** Dimensions réelles des fichiers dans public/scenes (vignettes ×4 Lanczos). */
export const IMAGES: Record<ImageId, {w: number; h: number; sourcePx: string}> = {
  scene_01: {w: 1444, h: 892, sourcePx: '361×223'},
  scene_02: {w: 1444, h: 892, sourcePx: '361×223'},
  scene_03: {w: 1444, h: 892, sourcePx: '361×223'},
  scene_04: {w: 1436, h: 892, sourcePx: '359×223'},
  scene_05: {w: 1444, h: 864, sourcePx: '361×216'},
  scene_06: {w: 1444, h: 864, sourcePx: '361×216'},
  scene_07: {w: 1444, h: 864, sourcePx: '361×216'},
  scene_08: {w: 1436, h: 864, sourcePx: '359×216'},
  scene_09: {w: 1444, h: 860, sourcePx: '361×215'},
  scene_10: {w: 1444, h: 860, sourcePx: '361×215'},
  scene_11: {w: 1444, h: 860, sourcePx: '361×215'},
  scene_12: {w: 1436, h: 860, sourcePx: '359×215'},
  scene_13: {w: 6456, h: 940, sourcePx: '1614×235'},
  portrait_ref: {w: 1672, h: 941, sourcePx: '1672×941'},
};

export type CamH = {s: number; fx: number; fy: number};
export type CamV = {k: number; fx: number; by?: number};

export type Shot = {
  img: ImageId;
  start: number; // début (s) ; la fin = début du plan suivant
  /** fondu d'entrée (s), centré sur la coupe ; 0 = coupe franche */
  xfade: number;
  h: {from: CamH; to: CamH};
  v: {from: CamV; to: CamV};
  breathe?: boolean; // micro-respiration (scène 01 uniquement)
};

export type Scene = {
  n: number;
  title: string;
  lyric: string; // repère chanté
  shots: Shot[];
};

const XS = 0.7; // fondu entre scènes
const XI = 0.4; // fondu interne

export const SCENES: Scene[] = [
  {
    n: 1, title: 'Intro — le recueillement', lyric: 'Ya Allah… Je reviens à Ton amour',
    shots: [
      // Page de garde : mer et soleil du portrait de référence, sans visage, titre.
      {img: 'portrait_ref', start: 0, xfade: 0,
        h: {from: {s: 3.15, fx: 0.15, fy: 0.4}, to: {s: 3.05, fx: 0.16, fy: 0.41}},
        v: {from: {k: 3.05, fx: 0.15}, to: {k: 3.0, fx: 0.16}}},
      {img: 'scene_01', start: 5.6, xfade: 0.8, breathe: true,
        h: {from: {s: 1.0, fx: 0.5, fy: 0.5}, to: {s: 1.08, fx: 0.48, fy: 0.47}},
        v: {from: {k: 1.55, fx: 0.48}, to: {k: 1.68, fx: 0.47}}},
      {img: 'scene_01', start: 15.6, xfade: 0.6, breathe: true,
        h: {from: {s: 1.2, fx: 0.42, fy: 0.42}, to: {s: 1.26, fx: 0.43, fy: 0.42}},
        v: {from: {k: 2.0, fx: 0.42}, to: {k: 2.08, fx: 0.43}}},
    ],
  },
  {
    n: 2, title: 'Les départs', lyric: 'Je regardais les départs sur la mer',
    shots: [
      {img: 'scene_02', start: 23.0, xfade: XS,
        h: {from: {s: 1.1, fx: 0.52, fy: 0.5}, to: {s: 1.0, fx: 0.5, fy: 0.5}},
        v: {from: {k: 1.28, fx: 0.52}, to: {k: 1.18, fx: 0.5}}},
      {img: 'scene_02', start: 33.1, xfade: XI, // « Et mes valises… »
        h: {from: {s: 1.42, fx: 0.5, fy: 0.72}, to: {s: 1.45, fx: 0.53, fy: 0.72}},
        v: {from: {k: 1.9, fx: 0.5, by: 0.5}, to: {k: 1.95, fx: 0.53, by: 0.5}}},
      {img: 'scene_02', start: 37.9, xfade: XI, // « Je regardais les départs »
        h: {from: {s: 1.35, fx: 0.6, fy: 0.38}, to: {s: 1.4, fx: 0.7, fy: 0.38}},
        v: {from: {k: 1.7, fx: 0.55}, to: {k: 1.75, fx: 0.68}}},
    ],
  },
  {
    n: 3, title: 'Le souffle', lyric: 'Un vent léger a traversé mon voile',
    shots: [
      {img: 'scene_03', start: 47.5, xfade: XS,
        h: {from: {s: 1.12, fx: 0.42, fy: 0.5}, to: {s: 1.12, fx: 0.54, fy: 0.5}},
        v: {from: {k: 1.5, fx: 0.4}, to: {k: 1.5, fx: 0.5}}},
      {img: 'scene_03', start: 57.5, xfade: XI, // « J'ai fait silence »
        h: {from: {s: 1.36, fx: 0.48, fy: 0.36}, to: {s: 1.42, fx: 0.48, fy: 0.34}},
        v: {from: {k: 1.85, fx: 0.48}, to: {k: 1.95, fx: 0.48}}},
    ],
  },
  {
    n: 4, title: 'Le cœur', lyric: 'Ici, ici commence le voyage',
    shots: [
      {img: 'scene_04', start: 67.6, xfade: XS,
        h: {from: {s: 1.0, fx: 0.55, fy: 0.5}, to: {s: 1.1, fx: 0.58, fy: 0.45}},
        v: {from: {k: 1.45, fx: 0.6}, to: {k: 1.6, fx: 0.6}}},
      {img: 'portrait_ref', start: 76.9, xfade: 0.6, // « Ya Allah, allège mes bagages »
        h: {from: {s: 1.72, fx: 0.53, fy: 0.5}, to: {s: 1.8, fx: 0.53, fy: 0.47}},
        v: {from: {k: 2.3, fx: 0.52, by: 0.5}, to: {k: 2.4, fx: 0.52, by: 0.5}}},
    ],
  },
  {
    n: 5, title: 'Le premier pas', lyric: 'Je fais un pas, je laisse entrer le jour',
    shots: [
      {img: 'scene_05', start: 86.6, xfade: XS,
        h: {from: {s: 1.08, fx: 0.42, fy: 0.55}, to: {s: 1.08, fx: 0.55, fy: 0.55}},
        v: {from: {k: 1.5, fx: 0.38}, to: {k: 1.5, fx: 0.5}}},
      {img: 'scene_05', start: 96.4, xfade: 0.6, // « Au creux du monde, une lumière veille »
        h: {from: {s: 1.32, fx: 0.7, fy: 0.5}, to: {s: 1.26, fx: 0.66, fy: 0.5}},
        v: {from: {k: 1.7, fx: 0.62}, to: {k: 1.62, fx: 0.6}}},
    ],
  },
  {
    n: 6, title: 'Déposer les regrets', lyric: "J'ai déposé mes regrets sur la table",
    shots: [
      {img: 'scene_06', start: 106.0, xfade: XS,
        h: {from: {s: 1.0, fx: 0.5, fy: 0.5}, to: {s: 1.07, fx: 0.52, fy: 0.5}},
        v: {from: {k: 1.35, fx: 0.48}, to: {k: 1.45, fx: 0.5}}},
      {img: 'scene_06', start: 115.8, xfade: XI, // détail des mains et du carnet
        h: {from: {s: 1.45, fx: 0.6, fy: 0.74}, to: {s: 1.48, fx: 0.62, fy: 0.74}},
        v: {from: {k: 1.9, fx: 0.6}, to: {k: 1.95, fx: 0.62}}},
      {img: 'scene_06', start: 120.8, xfade: XI, // « J'apprends enfin à regarder plus clair »
        h: {from: {s: 1.36, fx: 0.42, fy: 0.34}, to: {s: 1.4, fx: 0.42, fy: 0.33}},
        v: {from: {k: 1.85, fx: 0.42}, to: {k: 1.9, fx: 0.42}}},
    ],
  },
  {
    n: 7, title: 'Offrir une place', lyric: 'Le même banc, mais une place offerte',
    shots: [
      {img: 'scene_07', start: 125.5, xfade: XS,
        h: {from: {s: 1.0, fx: 0.5, fy: 0.5}, to: {s: 1.06, fx: 0.55, fy: 0.48}},
        v: {from: {k: 1.12, fx: 0.5}, to: {k: 1.18, fx: 0.53}}},
      {img: 'scene_07', start: 135.6, xfade: XI, // le geste offert, les deux femmes dans le cadre
        h: {from: {s: 1.28, fx: 0.58, fy: 0.5}, to: {s: 1.3, fx: 0.6, fy: 0.5}},
        v: {from: {k: 1.25, fx: 0.6}, to: {k: 1.3, fx: 0.62}}},
    ],
  },
  {
    n: 8, title: "S'ouvrir au monde", lyric: 'Ici commence le voyage (2e refrain)',
    shots: [
      {img: 'scene_08', start: 145.6, xfade: XS,
        h: {from: {s: 1.1, fx: 0.42, fy: 0.5}, to: {s: 1.1, fx: 0.54, fy: 0.5}},
        v: {from: {k: 1.5, fx: 0.42}, to: {k: 1.5, fx: 0.55}}},
      {img: 'scene_08', start: 155.0, xfade: XI, // visage et salut
        h: {from: {s: 1.32, fx: 0.52, fy: 0.38}, to: {s: 1.36, fx: 0.52, fy: 0.37}},
        v: {from: {k: 1.85, fx: 0.52}, to: {k: 1.9, fx: 0.52}}},
    ],
  },
  {
    n: 9, title: 'Partager', lyric: 'Au creux du monde, une lumière veille',
    shots: [
      {img: 'scene_09', start: 164.6, xfade: XS,
        h: {from: {s: 1.02, fx: 0.5, fy: 0.5}, to: {s: 1.08, fx: 0.52, fy: 0.5}},
        v: {from: {k: 1.12, fx: 0.5}, to: {k: 1.18, fx: 0.52}}},
      {img: 'scene_09', start: 174.5, xfade: XI, // le verre et les mains
        h: {from: {s: 1.42, fx: 0.6, fy: 0.68}, to: {s: 1.45, fx: 0.61, fy: 0.68}},
        v: {from: {k: 1.75, fx: 0.6}, to: {k: 1.8, fx: 0.61}}},
      {img: 'scene_09', start: 179.4, xfade: XI, // les regards
        h: {from: {s: 1.16, fx: 0.52, fy: 0.4}, to: {s: 1.2, fx: 0.52, fy: 0.4}},
        v: {from: {k: 1.2, fx: 0.52}, to: {k: 1.25, fx: 0.52}}},
    ],
  },
  {
    n: 10, title: 'Pardonner', lyric: "Prend aujourd'hui la forme d'un pardon",
    shots: [
      {img: 'scene_10', start: 184.0, xfade: 0.8,
        h: {from: {s: 1.0, fx: 0.5, fy: 0.5}, to: {s: 1.04, fx: 0.5, fy: 0.48}},
        v: {from: {k: 1.15, fx: 0.5}, to: {k: 1.2, fx: 0.5}}},
      {img: 'scene_10', start: 193.9, xfade: 0.6, // mains réunies
        h: {from: {s: 1.36, fx: 0.52, fy: 0.74}, to: {s: 1.38, fx: 0.52, fy: 0.74}},
        v: {from: {k: 1.55, fx: 0.52}, to: {k: 1.58, fx: 0.52}}},
      {img: 'scene_10', start: 199.0, xfade: 0.6, // « la forme d'un pardon »
        h: {from: {s: 1.12, fx: 0.5, fy: 0.4}, to: {s: 1.15, fx: 0.5, fy: 0.4}},
        v: {from: {k: 1.3, fx: 0.5}, to: {k: 1.34, fx: 0.5}}},
    ],
  },
  {
    n: 11, title: 'Avancer', lyric: 'Ici commence le voyage (refrain final)',
    shots: [
      {img: 'scene_11', start: 204.5, xfade: XS,
        h: {from: {s: 1.36, fx: 0.45, fy: 0.38}, to: {s: 1.2, fx: 0.46, fy: 0.42}},
        v: {from: {k: 1.95, fx: 0.45}, to: {k: 1.75, fx: 0.46}}},
      {img: 'scene_11', start: 214.2, xfade: XI,
        h: {from: {s: 1.14, fx: 0.47, fy: 0.45}, to: {s: 1.0, fx: 0.5, fy: 0.5}},
        v: {from: {k: 1.6, fx: 0.46}, to: {k: 1.35, fx: 0.48}}},
    ],
  },
  {
    n: 12, title: 'Cheminer ensemble', lyric: 'Mon cœur apprend une route nouvelle',
    shots: [
      {img: 'scene_12', start: 223.6, xfade: XS,
        h: {from: {s: 1.0, fx: 0.46, fy: 0.5}, to: {s: 1.06, fx: 0.5, fy: 0.5}},
        v: {from: {k: 1.25, fx: 0.48}, to: {k: 1.32, fx: 0.5}}},
      {img: 'scene_12', start: 233.6, xfade: XI, // le sac, porté avec légèreté
        h: {from: {s: 1.4, fx: 0.36, fy: 0.72}, to: {s: 1.42, fx: 0.38, fy: 0.72}},
        v: {from: {k: 1.6, fx: 0.38}, to: {k: 1.64, fx: 0.4}}},
      {img: 'scene_12', start: 238.6, xfade: XI, // les visages
        h: {from: {s: 1.26, fx: 0.55, fy: 0.34}, to: {s: 1.3, fx: 0.55, fy: 0.33}},
        v: {from: {k: 1.35, fx: 0.55}, to: {k: 1.4, fx: 0.55}}},
    ],
  },
  {
    n: 13, title: 'Être ici', lyric: 'Le voyage commence au cœur de ma vie',
    shots: [
      {img: 'scene_13', start: 243.0, xfade: XS, // panoramique : de la femme âgée vers elle
        h: {from: {s: 1.0, fx: 0.33, fy: 0.5}, to: {s: 1.0, fx: 0.47, fy: 0.5}},
        v: {from: {k: 6.0, fx: 0.29, by: 0.5}, to: {k: 6.0, fx: 0.47, by: 0.5}}},
      {img: 'portrait_ref', start: 251.6, xfade: 0.8, // portrait final, lent recul révélant la mer
        h: {from: {s: 1.85, fx: 0.52, fy: 0.42}, to: {s: 1.0, fx: 0.5, fy: 0.5}},
        v: {from: {k: 3.3, fx: 0.52, by: 0.5}, to: {k: 1.75, fx: 0.5, by: 0.5}}},
    ],
  },
];

/** Titres : page de garde (visible dès l'image 0) et titre final. */
export const TITLE_TEXT = ['Ici commence', 'le voyage'];
export const OPENING_TITLE = {in: 0, holdUntil: 4.4, out: 5.4};
export const FINAL_TITLE = {in: 255.5, fadeIn: 1.6};
/** Fondu au noir final (image + titre), terminé avant la fin de la queue de réverbération. */
export const FADE_TO_BLACK = {start: 262.6, end: 265.8};

/** Liste aplatie des plans avec leur fin. */
export const flatShots = () => {
  const all = SCENES.flatMap((sc, si) => sc.shots.map((s) => ({...s, scene: sc.n, sceneIndex: si})));
  return all.map((s, i) => ({
    ...s,
    end: i + 1 < all.length ? all[i + 1].start : SONG_DURATION_S,
    nextXfade: i + 1 < all.length ? all[i + 1].xfade : 0,
  }));
};
