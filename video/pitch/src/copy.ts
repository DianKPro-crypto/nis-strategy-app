// All on-screen copy. Facts come ONLY from the approved fact sheet (README §Facts).
// FR is an institutional adaptation (SNV, PEV, CCIA), not a literal translation.

export type Lang = 'en' | 'fr';

export type Copy = {
  lang: Lang;
  decimal: string;
  hook: {signature: string; lead: string; accent: string};
  bottleneck: {lines: string[]; coda: string};
  reveal: {name: string; title: string; base: string};
  proof: {
    kicker: string;
    items: {value: number; suffix?: string; label: string}[];
    countries: Record<string, string>; // ISO 3166-1 numeric -> label
    countriesShort: Record<string, string>; // compact legend (9:16)
    base: string;
  };
  offers: {kicker: string; items: {num: string; title: string; desc: string}[]};
  method: {
    kicker: string;
    chain: {value: number; label: string}[];
    traced: string;
    gauge: {from: number; to: number; label: string; outOf: string};
    tagline: string;
  };
  trust: {kicker: string; agencies: string[]; ministriesLabel: string; ministries: string[]};
  cta: {lines: [string, string]; invite: string; tagline: string; scan: string};
};

export const EN: Copy = {
  lang: 'en',
  decimal: '.',
  hook: {
    signature: 'Dr. Dian SIDIBE, MD',
    lead: 'What if the money was already there…',
    accent: 'and the strategy wasn’t?',
  },
  bottleneck: {
    lines: ['No endorsed strategy.', 'No costed plan.', 'No funding cycle.'],
    coda: 'And children wait.',
  },
  reveal: {
    name: 'Dr. Dian SIDIBE, MD',
    title: 'National Immunisation Strategy Architect',
    base: 'Based in Casablanca|AFRO & EMRO',
  },
  proof: {
    kicker: 'Track record',
    items: [
      {value: 28, label: 'years in public health'},
      {value: 5, label: 'countries costed with NIS.COST'},
      {value: 23, label: 'country offices overseen'},
      {value: 15, suffix: '+', label: 'country teams trained in NIS costing'},
      {value: 3, label: 'working languages: FR · EN · AR'},
    ],
    countries: {'450': 'Madagascar', '108': 'Burundi', '174': 'Comoros', '140': 'Central African Rep.', '262': 'Djibouti'},
    countriesShort: {'450': 'Madagascar', '108': 'Burundi', '174': 'Comoros', '140': 'CAR', '262': 'Djibouti'},
    base: 'Casablanca',
  },
  offers: {
    kicker: 'Three ways I work',
    items: [
      {num: '01', title: 'Unlock financing', desc: 'When funds are budgeted but not flowing.'},
      {num: '02', title: 'Architect the strategy', desc: 'Endorsed, costed, fundable.'},
      {num: '03', title: 'Build national ownership', desc: 'Countries that run their own costing.'},
    ],
  },
  method: {
    kicker: 'Djibouti NIS 2027–2030 · WHO',
    chain: [
      {value: 26, label: 'objectives'},
      {value: 110, label: 'interventions'},
      {value: 348, label: 'activities'},
    ],
    traced: 'fully traced',
    gauge: {from: 77.8, to: 89.1, label: 'Workshop quality score', outOf: '/ 100'},
    tagline: 'AI-accelerated. Human-validated. Fully traceable.',
  },
  trust: {
    kicker: 'Institutions served',
    agencies: ['WHO', 'UNICEF', 'UNFPA', 'UNDP', 'Dalberg Advisors', 'IRC', 'Save the Children', 'PSI'],
    ministriesLabel: 'Ministries of Health',
    ministries: ['Djibouti', 'Madagascar', 'Burundi', 'Comoros', 'Central African Republic', 'Mali'],
  },
  cta: {
    lines: ['Strategies ministries own.', 'Plans donors fund.'],
    invite: 'Let’s talk about your next strategy cycle.',
    tagline: 'Designed for Those Who Cannot Fail.',
    scan: 'LinkedIn',
  },
};

export const FR: Copy = {
  lang: 'fr',
  decimal: ',',
  hook: {
    signature: 'Dr Dian SIDIBÉ',
    lead: 'Et si l’argent était déjà là…',
    accent: 'mais pas la stratégie\u202f?',
  },
  bottleneck: {
    lines: ['Pas de stratégie validée.', 'Pas de plan chiffré.', 'Pas de cycle de financement.'],
    coda: 'Et les enfants attendent.',
  },
  reveal: {
    name: 'Dr Dian SIDIBÉ',
    title: 'Architecte de stratégies nationales de vaccination',
    base: 'Basé à Casablanca|Régions AFRO et EMRO',
  },
  proof: {
    kicker: 'En chiffres',
    items: [
      {value: 28, label: 'ans en santé publique'},
      {value: 5, label: 'pays chiffrés avec NIS.COST'},
      {value: 23, label: 'bureaux pays supervisés'},
      {value: 15, suffix: '+', label: 'équipes pays formées au chiffrage des SNV'},
      {value: 3, label: 'langues de travail\u00a0: FR · EN · AR'},
    ],
    countries: {'450': 'Madagascar', '108': 'Burundi', '174': 'Comores', '140': 'Centrafrique', '262': 'Djibouti'},
    countriesShort: {'450': 'Madagascar', '108': 'Burundi', '174': 'Comores', '140': 'RCA', '262': 'Djibouti'},
    base: 'Casablanca',
  },
  offers: {
    kicker: 'Trois façons d’intervenir',
    items: [
      {num: '01', title: 'Débloquer les financements', desc: 'Quand les fonds sont budgétés mais bloqués.'},
      {num: '02', title: 'Concevoir la stratégie', desc: 'Validée, chiffrée, finançable.'},
      {num: '03', title: 'Bâtir l’appropriation nationale', desc: 'Des pays qui pilotent eux-mêmes leur chiffrage.'},
    ],
  },
  method: {
    kicker: 'SNV Djibouti 2027–2030 · OMS',
    chain: [
      {value: 26, label: 'objectifs'},
      {value: 110, label: 'interventions'},
      {value: 348, label: 'activités'},
    ],
    traced: 'entièrement tracés',
    gauge: {from: 77.8, to: 89.1, label: 'Score qualité de l’atelier', outOf: '/ 100'},
    tagline: 'Accélérée par l’IA. Validée par l’humain. Entièrement traçable.',
  },
  trust: {
    kicker: 'Institutions accompagnées',
    agencies: ['OMS', 'UNICEF', 'UNFPA', 'PNUD', 'Dalberg Advisors', 'IRC', 'Save the Children', 'PSI'],
    ministriesLabel: 'Ministères de la Santé',
    ministries: ['Djibouti', 'Madagascar', 'Burundi', 'Comores', 'République centrafricaine', 'Mali'],
  },
  cta: {
    lines: ['Des stratégies que les ministères portent.', 'Des plans que les bailleurs financent.'],
    invite: 'Parlons de votre prochain cycle stratégique.',
    tagline: 'Designed for Those Who Cannot Fail.',
    scan: 'LinkedIn',
  },
};

export const COPY: Record<Lang, Copy> = {en: EN, fr: FR};

export const fmt = (v: number, decimals: number, decimal: string) =>
  v.toFixed(decimals).replace('.', decimal);
