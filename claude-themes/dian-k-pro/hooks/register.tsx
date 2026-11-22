import type { EngineInterface, Register, ThemeSetArgs, ThemeSound } from 'claude-code'

import { makeColors } from './make-colors.js'

// Thème Dian K Pro : noir et or la nuit, papier ivoire le jour.
// Fond animé : graines de lumière qui montent et lignes de circuit qui s'allument,
// reprises du « D » du logo, placées dans les coins, loin du texte et du champ de saisie.

const { theme, problems } = makeColors({
  label: 'Dian K Pro',
  roles: { accent: '#e3b34c', danger: '#c8553d', success: '#6f9a4a', warning: '#d9932b', pro: '#9a7bc0' },
  light: {
    gray: {
      anchors: {
        'surface-0': '#efe7d6',
        'surface-1': '#f5eedf',
        'surface-2': '#fbf7ee',
        'text-primary': '#1d1a15',
        'text-secondary': '#4a4236',
        'text-muted': '#665c4c',
      },
    },
    roles: { accent: '#9c7420' },
  },
  dark: {
    gray: {
      anchors: {
        'surface-0': '#0e0d0b',
        'surface-1': '#15130f',
        'surface-2': '#1b1814',
        'surface-3': '#211d18',
        'text-primary': '#f4ecdc',
        'text-secondary': '#d6cbb5',
        'text-muted': '#b0a48d',
      },
    },
  },
})

// ---------- Scène ----------

type Seed = { x: number; y: number; r: number; dur: number; delay: number }

// Positions fixes : la scène est identique à chaque chargement.
const LEFT_SEEDS: Seed[] = [
  { x: 70, y: 960, r: 4, dur: 24, delay: -2 },
  { x: 130, y: 900, r: 3, dur: 30, delay: -11 },
  { x: 190, y: 980, r: 5, dur: 27, delay: -19 },
  { x: 250, y: 930, r: 3, dur: 33, delay: -6 },
  { x: 310, y: 990, r: 4, dur: 26, delay: -15 },
  { x: 370, y: 950, r: 3, dur: 31, delay: -24 },
  { x: 105, y: 990, r: 2, dur: 22, delay: -9 },
]
const RIGHT_SEEDS: Seed[] = [
  { x: 1240, y: 970, r: 3, dur: 29, delay: -4 },
  { x: 1300, y: 920, r: 4, dur: 25, delay: -13 },
  { x: 1360, y: 990, r: 3, dur: 32, delay: -21 },
  { x: 1420, y: 940, r: 5, dur: 28, delay: -8 },
  { x: 1480, y: 985, r: 3, dur: 34, delay: -17 },
  { x: 1540, y: 930, r: 4, dur: 23, delay: -1 },
]

function seeds(list: Seed[]): string {
  return list
    .map(
      s =>
        `<circle class="seed" cx="${s.x}" cy="${s.y - 260}" r="${s.r}" opacity=".55" style="animation-duration:${s.dur}s;animation-delay:${s.delay}s"/>`,
    )
    .join('')
}

// Lignes de circuit du coin bas gauche ; le coin haut droit les reprend, retournées.
const WIRES = [
  { d: 'M40 1000V760L90 710V520', node: [90, 520], dur: 14, delay: 0 },
  { d: 'M95 1000V830L155 770V620', node: [155, 620], dur: 17, delay: -5 },
  { d: 'M150 1000V890L225 815V720', node: [225, 720], dur: 12, delay: -9 },
  { d: 'M0 610H25L55 580V420', node: [55, 420], dur: 19, delay: -3 },
]

function circuit(): string {
  return WIRES.map(
    w =>
      `<path class="wire" d="${w.d}"/>` +
      `<circle class="node" cx="${w.node[0]}" cy="${w.node[1]}" r="7"/>` +
      `<path class="pulse" d="${w.d}" style="animation-duration:${w.dur}s;animation-delay:${w.delay}s"/>`,
  ).join('')
}

const SCENE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice">
<style>
svg { --bg: #0e0d0b; --glow: #3b2a0e; --line: #e3b34c; --seed: #f3d389; }
@media (prefers-color-scheme: light) {
  svg { --bg: #efe7d6; --glow: #ead6a4; --line: #9c7420; --seed: #b8892c; }
}
.bg { fill: var(--bg); }
.halo-stop { stop-color: var(--glow); }
.halo-end { stop-color: var(--glow); stop-opacity: 0; }
.wire { fill: none; stroke: var(--line); stroke-width: 2; opacity: .22; }
.node { fill: none; stroke: var(--line); stroke-width: 2; opacity: .4; }
.pulse { fill: none; stroke: var(--line); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 60 1400; stroke-dashoffset: 1460; opacity: .9; animation: flow 14s linear infinite; }
.seed { fill: var(--seed); animation: rise 28s linear infinite; }
@keyframes flow { from { stroke-dashoffset: 1460; } to { stroke-dashoffset: 0; } }
@keyframes rise {
  0% { transform: translateY(260px); opacity: 0; }
  12% { opacity: .85; }
  80% { opacity: .6; }
  100% { transform: translateY(-420px); opacity: 0; }
}
@media (max-aspect-ratio: 4/5) {
  .bl { transform: translate(540px, 0); }
  .tr { transform: translate(-540px, 0); }
  .br { transform: translate(-540px, 0); }
}
</style>
<defs>
<radialGradient id="glowBL" cx="0" cy="1" r=".75"><stop offset="0" class="halo-stop"/><stop offset="1" class="halo-end"/></radialGradient>
<radialGradient id="glowTR" cx="1" cy="0" r=".6"><stop offset="0" class="halo-stop"/><stop offset="1" class="halo-end"/></radialGradient>
</defs>
<!-- fond -->
<rect class="bg" width="1600" height="1000"/>
<rect width="1600" height="1000" fill="url(#glowBL)" opacity=".9"/>
<rect width="1600" height="1000" fill="url(#glowTR)" opacity=".55"/>
<!-- circuit du coin bas gauche, graines -->
<g class="bl">${circuit()}${seeds(LEFT_SEEDS)}</g>
<!-- circuit du coin haut droit -->
<g class="tr"><g transform="rotate(180 800 500)">${circuit()}</g></g>
<!-- graines du coin bas droit -->
<g class="br">${seeds(RIGHT_SEEDS)}</g>
</svg>`

// ---------- Son : ambiance kora, ré mineur ----------

const SOUND: ThemeSound = {
  ambience: {
    layers: [
      { wave: 'sine', notes: ['D3', 'A3'], drone: true, gain: 0.1, filter: { type: 'lowpass', hz: 500 }, tremolo: { hz: 0.08, depth: 0.3 } },
      {
        wave: 'triangle',
        notes: ['D4', 'F4', 'G4', 'A4', 'C5', 'D5', 'F5'],
        scatter: 0.16,
        gain: 0.16,
        attack: 0.003,
        release: 1.6,
        filter: { type: 'lowpass', hz: 2600 },
      },
      { wave: 'pink', drone: true, gain: 0.04, filter: { type: 'lowpass', hz: 800 } },
    ],
    reverb: 0.35,
  },
  cues: {
    send: { layers: [{ wave: 'triangle', notes: ['A4', 'D5'], step: 0.07, gain: 0.22, release: 0.5 }] },
    tool: { layers: [{ wave: 'sine', notes: ['D5'], gain: 0.07, release: 0.15 }] },
    done: { layers: [{ wave: 'bell', notes: ['D5', 'F5', 'A5'], step: 0.12, gain: 0.22, release: 1.2 }], reverb: 0.3 },
    ask: { layers: [{ wave: 'triangle', notes: ['F4', 'C5'], step: 0.12, gain: 0.22, release: 0.6 }] },
    error: { layers: [{ wave: 'sine', notes: ['A3', 'F3'], step: 0.15, gain: 0.18, release: 0.5 }] },
    compact: { layers: [{ wave: 'pink', gain: 0.08, attack: 0.2, release: 0.8, filter: { type: 'lowpass', hz: 1200 } }] },
    click: { layers: [{ wave: 'bell', notes: ['D4', 'F4', 'G4', 'A4', 'C5', 'D5'], gain: 0.18, release: 0.9 }] },
  },
}

// ---------- Look ----------

const BASE: ThemeSetArgs = {
  colors: theme,
  backdrop: { scene: 'graines', glass: { blur: 18, opacity: 0.72 } },
}

const STYLE: ThemeSetArgs['style'] = {
  Heading: { fontFamily: ['serif'], fontWeight: 'semibold' },
  UserMessage: { backgroundColor: 'surface-2', borderColor: '#e3b34c80', borderWidth: 1, radius: 14, paddingX: 14, paddingY: 10 },
  AssistantMessage: { backgroundColor: 'surface-0', radius: 12, padding: 12 },
  ToolUse: { backgroundColor: 'surface-1', radius: 8, paddingX: 8 },
}

// Du plus complet au plus simple : chaque version de l'app reçoit le plus riche qu'elle accepte.
// Niveau 2 : son et style ; 1 : son ; 0 : couleurs et fond seuls.
const LEVELS: ThemeSetArgs[] = [BASE, { ...BASE, sound: SOUND }, { ...BASE, sound: SOUND, style: STYLE }]
const LEVEL_KEY = 'niveau'

// Une app qui refuse le son ou le style est une ancienne version : on y dessine le fond sans effet GPU.
let plain = false

async function apply($: EngineInterface): Promise<void> {
  const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))

  if (unpainted !== undefined) {
    $.ui.toast(unpainted)
  }

  const stored = Number((await $.store.get(LEVEL_KEY)) ?? 2)
  let level = Number.isInteger(stored) && stored >= 0 && stored <= 2 ? stored : 2

  while (level > 0) {
    try {
      const set = await $.theme.set(LEVELS[level] ?? BASE)
      plain = level < 2

      if (!set.isDrawn) {
        $.ui.status(set.reason)
      }

      return
    } catch (error) {
      if (!/does not know the attribute/.test(String(error))) {
        $.ui.log(String(error))
      }
      level -= 1
      await $.store.set(LEVEL_KEY, level)
    }
  }

  plain = true
  const set = await $.theme.set(BASE)

  if (!set.isDrawn) {
    $.ui.status(set.reason)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await apply($)
    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, ($, e, next) => {
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }

    if (e.props.plugin !== 'dian-k-pro') {
      return next(e)
    }

    const { Shader, Svg } = $.ui.resolve(e)
    const alt = "Graines de lumière dorées qui montent et lignes de circuit qui s'allument"

    if (plain) {
      return <Svg source={SCENE} alt={alt} isInteractive />
    }

    return (
      <Shader module="./seeds.ts">
        <Svg source={SCENE} alt={alt} isInteractive />
      </Shader>
    )
  })
}
