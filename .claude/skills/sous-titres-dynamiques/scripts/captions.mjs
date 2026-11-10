#!/usr/bin/env node
// Sous-titres dynamiques — charte Dian K Pro, pour compositions HyperFrames.
// Outil autonome, sans dépendance (Node ≥ 18). Aide : node captions.mjs aide
//
//   check      contrôle qualité d'une transcription (langue, hallucinations, minutage)
//   fix        nettoie + applique le lexique santé publique → tableau de mots propre
//   from-srt   convertit un .srt / .vtt (phrases) en mots minutés (répartition par caractères)
//   build      génère la sous-composition HyperFrames des sous-titres (compositions/captions.html)
//   planche    génère une planche HTML statique des styles (aperçu, sans HyperFrames)
//   luminance  mesure la luminosité de la bande sous-titres d'une vidéo (ffmpeg) → voile conseillé
//   styles     liste les styles disponibles

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(HERE, "..");
const DEFAULT_LEXIQUE = path.join(SKILL_DIR, "references", "lexique-sante-publique.json");

// ───────────────────────────── Charte et formats ─────────────────────────────
const CHARTE = { noir: "#0B0B0C", or: "#E3B34C", blanc: "#FFFFFF", creme: "#F6F1E7" };
const OR_RGBA = (a) => `rgba(227,179,76,${a})`;
const NOIR_RGBA = (a) => `rgba(11,11,12,${a})`;

const FORMATS = {
  "16x9": { w: 1920, h: 1080, marge: 192 }, // 80 % title-safe → 1536 px utiles
  "9x16": { w: 1080, h: 1920, marge: 108, zoneSure: [260, 1600] }, // 864 px utiles
};

// [taille de base, taille minimale] en px, par format.
const STYLES = {
  "or-karaoke": {
    label: "Or karaoké — signature Dian K Pro",
    usage: "Narration générale, plaidoyer, Statut WhatsApp / Stories",
    energie: "moyenne",
    font: "Inter", weight: 900, upper: false, tracking: "-0.01em",
    size: { "16x9": [76, 48], "9x16": [92, 56] },
    mots: { "16x9": 5, "9x16": 3 }, car: { "16x9": 36, "9x16": 22 },
    color: CHARTE.blanc, active: CHARTE.or, emphColor: CHARTE.or,
    highlight: "couleur", activeScale: 1.04, emphScale: 1.08, lift: 6, gap: 0.1,
    enterFrom: { opacity: 0, y: 26 }, enterTo: { opacity: 1, y: 0, duration: 0.22, ease: "power3.out" },
    exit: 0.12, lines: 1, fit: true, ponctuation: "auto", scrim: 0,
  },
  pastille: {
    label: "Pastille or — mot actif surligné",
    usage: "Réseaux sociaux, accroches énergiques, jeunes publics",
    energie: "élevée",
    font: "Inter", weight: 900, upper: true, tracking: "0",
    size: { "16x9": [72, 48], "9x16": [88, 56] },
    mots: { "16x9": 3, "9x16": 2 }, car: { "16x9": 26, "9x16": 14 },
    color: CHARTE.blanc, active: CHARTE.noir, emphColor: CHARTE.or,
    highlight: "pastille", activeScale: 1.04, emphScale: 1.08, lift: 0, gap: 0.1,
    enterFrom: { opacity: 0, scale: 0.86 }, enterTo: { opacity: 1, scale: 1, duration: 0.18, ease: "back.out(1.7)" },
    exit: 0.12, lines: 1, fit: true, ponctuation: "auto", scrim: 0,
  },
  editorial: {
    label: "Éditorial Playfair — récit et témoignage",
    usage: "Témoignages, récit de terrain, plaidoyer posé, film institutionnel",
    energie: "calme",
    font: "Playfair Display", weight: 700, upper: false, tracking: "0",
    size: { "16x9": [64, 44], "9x16": [78, 52] },
    mots: { "16x9": 6, "9x16": 4 }, car: { "16x9": 42, "9x16": 26 },
    color: CHARTE.creme, active: CHARTE.or, emphColor: CHARTE.or, emphItalic: true,
    highlight: "couleur", activeScale: 1.02, emphScale: 1.04, lift: 0, gap: 0.06,
    enterFrom: { opacity: 0, y: 14 }, enterTo: { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" },
    exit: 0.25, lines: 1, fit: true, ponctuation: "auto", scrim: 0, pause: 0.25,
  },
  "chiffre-cle": {
    label: "Chiffre clé — les données frappent",
    usage: "Messages chiffrés, résultats, plaidoyer budgétaire (chiffres validés ou marqués illustratifs)",
    energie: "moyenne-élevée",
    font: "Inter", weight: 700, upper: false, tracking: "-0.005em",
    size: { "16x9": [70, 46], "9x16": [84, 54] },
    mots: { "16x9": 4, "9x16": 3 }, car: { "16x9": 32, "9x16": 20 },
    color: CHARTE.blanc, active: CHARTE.or, emphColor: CHARTE.or,
    emphFont: "Playfair Display", emphWeight: 700, emphSize: 1.45, emphSlam: true,
    highlight: "couleur", activeScale: 1.03, emphScale: 1.0, lift: 4, gap: 0.1,
    enterFrom: { opacity: 0, y: 20 }, enterTo: { opacity: 1, y: 0, duration: 0.24, ease: "power3.out" },
    exit: 0.14, lines: 1, fit: true, ponctuation: "auto", scrim: 0,
  },
  "mot-a-mot": {
    label: "Mot à mot — accroche XXL",
    usage: "Accroche des 3 premières secondes, teaser ≤ 30 s, slogans",
    energie: "très élevée",
    font: "Inter", weight: 900, upper: true, tracking: "-0.01em",
    size: { "16x9": [132, 64], "9x16": [150, 72] },
    mots: { "16x9": 2, "9x16": 2 }, car: { "16x9": 16, "9x16": 10 },
    color: CHARTE.blanc, active: CHARTE.or, emphColor: CHARTE.or,
    highlight: "couleur", activeScale: 1.0, emphScale: 1.06, lift: 0, gap: 0.12,
    enterFrom: { opacity: 0, scale: 0.6 }, enterTo: { opacity: 1, scale: 1, duration: 0.16, ease: "back.out(2.2)" },
    exit: 0.1, lines: 1, fit: true, ponctuation: "auto", scrim: 0, pause: 0.12,
  },
  institutionnel: {
    label: "Institutionnel — sous-titres classiques accessibles",
    usage: "Projection en comité, ministères, partenaires, accessibilité (personnes sourdes ou malentendantes)",
    energie: "neutre",
    font: "Inter", weight: 700, upper: false, tracking: "0",
    size: { "16x9": [52, 40], "9x16": [60, 44] },
    mots: { "16x9": 14, "9x16": 9 }, car: { "16x9": 84, "9x16": 44 },
    color: CHARTE.blanc, active: CHARTE.blanc, emphColor: CHARTE.blanc,
    highlight: "aucun", activeScale: 1, emphScale: 1, lift: 0, gap: 0, noEmphase: true,
    enterFrom: { opacity: 0 }, enterTo: { opacity: 1, duration: 0.15, ease: "power1.out" },
    exit: 0.15, lines: 2, fit: false, ponctuation: "garder", scrim: 0.7, pause: 0.6,
  },
};

// Voile local derrière le texte (pas un voile global sur la photo). Seuils validés WCAG (texte large ≥ 3:1 pour l'or, ≥ 4.5:1 pour le blanc) :
// doux 45 % jusqu'à une luminance de bande ≈ 150/255 ; plein 70 % au-delà (or ≥ 3.9:1 même sur fond blanc).
const SCRIMS = { aucun: 0, doux: 0.45, plein: 0.7 };

// ───────────────────────────── Outils texte ─────────────────────────────
const MUSIC_RE = /^[♪♫♬♩�♪-♯\s]+$/u;
const PURE_PUNCT_RE = /^[.,;:!?…%»"”)\]]+$/u;
const FILLERS = new Set(["euh", "heu", "hum", "uh", "um", "ah", "oh", "bah", "ben"]);
const FONCTION = new Set([
  "le", "la", "les", "l'", "un", "une", "des", "du", "de", "d'", "au", "aux", "à", "a", "et", "ou",
  "en", "pour", "par", "sur", "dans", "avec", "sans", "sous", "vers", "chez", "entre", "que", "qu'",
  "qui", "ce", "cet", "cette", "ces", "son", "sa", "ses", "leur", "leurs", "notre", "nos", "votre",
  "vos", "mon", "ma", "mes", "ne", "n'", "se", "s'", "nous", "vous", "ils", "elles", "il", "elle",
  "on", "y", "d'ici", "jusqu'a", "jusqu'au", "depuis", "selon", "contre", "parmi", "malgre", "afin",
  "lors", "pres", "mais", "donc", "car", "si", "plus", "tres",
  "the", "of", "to", "and", "for", "in", "at", "by",
]);
const STOP_FR = new Set("le la les de des du un une et est que qui dans pour pas sur au aux en ce cette avec nous vous ils elles sont plus par il elle ne se on son sa ses leur leurs notre nos mais ou donc car tout tous".split(" "));
const STOP_EN = new Set("the and of to is that in it for on with as are this be was we you they not have at by from or but an will can our their has".split(" "));
// Hallucinations connues de Whisper en français (sur silence ou musique).
// anchor : mot déclencheur ; voisins : mots de la formule autour de lui ; requiert : au moins un de ces mots dans la formule.
const HALLU = [
  { anchor: /amara/, voisins: ["sous-titres", "sous-titre", "sous-titrage", "realises", "realise", "par", "la", "communaute", "de", "d'", "org"], auto: true, label: "« Sous-titres réalisés par la communauté d'Amara.org »" },
  { anchor: /^st'?$/, voisins: ["sous-titrage", "501"], requiert: ["sous-titrage"], auto: true, label: "« Sous-titrage ST' 501 »" },
  { anchor: /radio-?canada/, voisins: ["sous-titrage", "sous-titres", "societe", "par", "la"], requiert: ["sous-titrage", "sous-titres"], auto: true, label: "« Sous-titrage Société Radio-Canada »" },
  { anchor: /^regarde$/, voisins: ["merci", "d'avoir", "avoir", "de", "cette", "la", "video"], requiert: ["merci"], auto: false, label: "« Merci d'avoir regardé »" },
  { anchor: /^abonnez-?vous$/, voisins: [], auto: false, label: "« Abonnez-vous »" },
  { anchor: /^thank$/, voisins: ["you"], requiert: ["you"], auto: false, label: "« Thank you. » isolé", isole: true },
  { anchor: /^merci$/, voisins: [], auto: false, label: "« Merci. » isolé", isole: true },
];

const stripAccents = (s) => s.normalize("NFD").replace(/\p{Diacritic}/gu, "");
const norm = (s) => stripAccents(String(s)).toLowerCase().replace(/[’]/g, "'").replace(/[^\p{L}\p{N}%'-]+/gu, "");
const splitPunct = (t) => {
  const m = String(t).match(/^([«"“(\[]*)(.*?)([.,;:!?…%»"”)\]]*)$/su);
  return m ? { lead: m[1], core: m[2], trail: m[3] } : { lead: "", core: String(t), trail: "" };
};
const ELISION_RE = /^((?:jusqu|lorsqu|puisqu|qu|[ldjnmstc])['’])(.+)$/iu;
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const r3 = (x) => Math.round(x * 1000) / 1000;
const NNBSP = " "; // espace fine insécable (typographie française)

function fail(msg) {
  console.error("✖ " + msg);
  process.exit(1);
}

// ───────────────────────────── Lecture des transcriptions ─────────────────────────────
function parseTimecode(tc) {
  const m = tc.trim().match(/^(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{1,3})$/);
  if (!m) return NaN;
  const [, h = "0", mi, s, ms] = m;
  return Number(h) * 3600 + Number(mi) * 60 + Number(s) + Number(ms.padEnd(3, "0")) / 1000;
}

function parseSubtitles(text) {
  const cues = [];
  const blocks = text.replace(/\r/g, "").replace(/^﻿/, "").split(/\n{2,}/);
  for (const b of blocks) {
    const lines = b.split("\n").filter((l) => l.trim() !== "");
    const i = lines.findIndex((l) => l.includes("-->"));
    if (i < 0) continue;
    const [a, z] = lines[i].split("-->");
    const start = parseTimecode(a);
    const end = parseTimecode(z.trim().split(/\s+/)[0]);
    const body = lines.slice(i + 1).join(" ").replace(/<[^>]+>/g, "").replace(/\{\\[^}]*\}/g, "").replace(/\s+/g, " ").trim();
    if (!isNaN(start) && !isNaN(end) && body) cues.push({ start, end, text: body });
  }
  return cues;
}

// Répartit le temps d'une phrase sur ses mots, au prorata des caractères (+2 par mot).
function cuesToWords(cues) {
  const out = [];
  for (const c of cues) {
    const toks = c.text.split(/\s+/).filter(Boolean);
    const weights = toks.map((t) => t.length + 2);
    const total = weights.reduce((a, b) => a + b, 0);
    let t = c.start;
    toks.forEach((tok, i) => {
      const d = ((c.end - c.start) * weights[i]) / total;
      out.push({ text: tok, start: r3(t), end: r3(t + d), approx: true });
      t += d;
    });
  }
  return out;
}

function loadWords(file) {
  if (!file) fail("Fichier de transcription manquant.");
  if (!fs.existsSync(file)) fail(`Fichier introuvable : ${file}`);
  const raw = fs.readFileSync(file, "utf8");
  const ext = path.extname(file).toLowerCase();
  if (ext === ".srt" || ext === ".vtt") return { words: cuesToWords(parseSubtitles(raw)), source: "phrases" };
  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    fail(`JSON illisible : ${file}`);
  }
  const fromList = (list) =>
    list.map((w) => ({ id: w.id, text: String(w.text ?? w.word ?? "").trim(), start: Number(w.start), end: Number(w.end) }));
  if (Array.isArray(data)) return { words: fromList(data), source: "mots" };
  if (Array.isArray(data.words)) return { words: fromList(data.words), source: "mots" };
  if (Array.isArray(data.segments) && data.segments.some((s) => Array.isArray(s.words)))
    return { words: fromList(data.segments.flatMap((s) => s.words || [])), source: "mots" };
  if (Array.isArray(data.segments))
    return { words: cuesToWords(data.segments.map((s) => ({ start: s.start, end: s.end, text: s.text }))), source: "phrases" };
  if (Array.isArray(data.transcription))
    return {
      words: cuesToWords(data.transcription.map((s) => ({ start: s.offsets.from / 1000, end: s.offsets.to / 1000, text: s.text.trim() }))),
      source: "phrases",
    };
  fail("Format non reconnu (attendu : tableau de mots, {words}, {segments}, .srt ou .vtt).");
}

// ───────────────────────────── Lexique ─────────────────────────────
function loadLexique(opt) {
  if (opt === "aucun" || opt === false) return { remplacements: new Map(), expressions: [], emphase: [] };
  const file = typeof opt === "string" ? opt : DEFAULT_LEXIQUE;
  if (!fs.existsSync(file)) return { remplacements: new Map(), expressions: [], emphase: [] };
  const j = JSON.parse(fs.readFileSync(file, "utf8"));
  const remplacements = new Map(Object.entries(j.remplacements || {}).map(([k, v]) => [norm(k), v]));
  const expressions = Object.entries(j.expressions || {})
    .map(([k, v]) => ({ keys: k.split(/\s+/).map(norm).filter(Boolean), value: v }))
    .sort((a, b) => b.keys.length - a.keys.length);
  const emphase = (j.emphase || []).map((e) => e.split(/\s+/).map(norm).filter(Boolean));
  return { remplacements, expressions, emphase };
}

function applyLexique(words, lex, log) {
  const out = [];
  for (let i = 0; i < words.length; i++) {
    let hit = null;
    for (const ex of lex.expressions) {
      if (ex.keys.length < 2 || i + ex.keys.length > words.length) continue;
      if (ex.keys.every((k, j) => norm(splitPunct(words[i + j].text).core) === k)) {
        hit = ex;
        break;
      }
    }
    if (hit) {
      const first = words[i], last = words[i + hit.keys.length - 1];
      const text = splitPunct(first.text).lead + hit.value + splitPunct(last.text).trail;
      log.push(`« ${words.slice(i, i + hit.keys.length).map((w) => w.text).join(" ")} » → « ${text} »`);
      out.push({ ...first, text, end: last.end });
      i += hit.keys.length - 1;
      continue;
    }
    const w = words[i];
    const { lead, core, trail } = splitPunct(w.text);
    let pre = "", base = core;
    const el = core.match(ELISION_RE);
    if (el) [pre, base] = [el[1], el[2]];
    const rep = lex.remplacements.get(norm(base));
    if (rep && rep !== base) {
      const text = lead + pre + rep + trail;
      log.push(`« ${w.text} » → « ${text} »`);
      out.push({ ...w, text });
    } else out.push(w);
  }
  return out;
}

// ───────────────────────────── Nettoyage ─────────────────────────────
function detectHallucinations(words) {
  const found = [];
  const n = words.map((w) => norm(w.text));
  const used = new Set();
  for (let i = 0; i < words.length; i++) {
    if (used.has(i)) continue;
    for (const h of HALLU) {
      if (!h.anchor.test(n[i])) continue;
      const vois = new Set(h.voisins);
      let a = i, z = i;
      // la formule est d'un seul tenant : pas de silence > 0,8 s entre ses mots
      while (a > 0 && vois.has(n[a - 1]) && words[a].start - words[a - 1].end < 0.8 && i - a < 8) a--;
      while (z < words.length - 1 && vois.has(n[z + 1]) && words[z + 1].start - words[z].end < 0.8 && z - i < 4) z++;
      const run = n.slice(a, z + 1);
      if (h.requiert && !h.requiert.some((r) => run.includes(r))) continue;
      if (h.isole) {
        // « Merci. » n'est suspect qu'isolé : en fin de piste ou après un long silence
        const gapBefore = a > 0 ? words[a].start - words[a - 1].end : 99;
        if (!(z >= words.length - 1 || gapBefore > 2) || z - a > 1) continue;
      }
      found.push({ i: a, len: z - a + 1, auto: h.auto, label: h.label, at: words[a].start });
      for (let k = a; k <= z; k++) used.add(k);
      break;
    }
  }
  return found;
}

function cleanWords(words, { lexique, log, fillers = true, autoHallu = true }) {
  let ws = words
    .map((w) => ({ ...w, text: String(w.text || "").replace(/\s+/g, " ").trim() }))
    .filter((w) => w.text && !MUSIC_RE.test(w.text) && Number.isFinite(w.start) && Number.isFinite(w.end));
  if (fillers)
    ws = ws.filter((w) => {
      const drop = FILLERS.has(norm(w.text)) && w.end - w.start < 0.4;
      if (drop) log.push(`hésitation retirée : « ${w.text} » (${w.start.toFixed(2)} s)`);
      return !drop;
    });
  ws.sort((a, b) => a.start - b.start);
  // ponctuation isolée → rattachée au mot précédent (« enfants ? »)
  const merged = [];
  for (const w of ws) {
    const prev = merged[merged.length - 1];
    if (prev && PURE_PUNCT_RE.test(w.text)) {
      // « Pourtant , euh , » → « Pourtant, » (pas de ponctuation doublée)
      if (/[.,;:]$/.test(prev.text) && /^[.,;:]+$/.test(w.text)) continue;
      const sp = /^[?!;:%»]/.test(w.text) ? NNBSP : "";
      prev.text = prev.text + sp + w.text;
      prev.end = Math.max(prev.end, w.end);
      continue;
    }
    // « 12 » + « 000 » → « 12 000 »
    if (prev && /^\d{1,3}$/.test(splitPunct(prev.text).core) && /^\d{3}\b/.test(w.text) && w.start - prev.end < 0.3) {
      prev.text = prev.text + NNBSP + w.text;
      prev.end = w.end;
      continue;
    }
    // élision séparée : « l' » + « UNICEF » → « l'UNICEF »
    if (prev && /^(?:jusqu|lorsqu|puisqu|qu|[ldjnmstc])['’]$/i.test(prev.text) && w.start - prev.end < 0.4) {
      prev.text = prev.text + w.text;
      prev.end = w.end;
      continue;
    }
    merged.push({ ...w });
  }
  ws = merged;
  // hallucinations connues de Whisper en français
  if (autoHallu) {
    const hs = detectHallucinations(ws).filter((h) => h.auto);
    const kill = new Set();
    for (const h of hs) {
      for (let k = 0; k < h.len; k++) kill.add(h.i + k);
      log.push(`hallucination retirée : ${h.label} (${h.at.toFixed(2)} s)`);
    }
    ws = ws.filter((_, i) => !kill.has(i));
  }
  if (lexique) ws = applyLexique(ws, lexique, log);
  // minutage monotone, sans chevauchement
  for (let i = 0; i < ws.length; i++) {
    const w = ws[i];
    if (w.end < w.start) w.end = w.start;
    const next = ws[i + 1];
    if (next && w.end > next.start) w.end = Math.max(w.start, next.start);
    if (w.end - w.start < 0.04) w.end = next ? Math.min(w.start + 0.04, Math.max(next.start, w.start)) : w.start + 0.04;
    w.start = r3(w.start);
    w.end = r3(w.end);
  }
  return ws.map((w, i) => {
    const o = { id: `w${i}`, text: w.text, start: w.start, end: w.end };
    if (w.approx) o.approx = true;
    return o;
  });
}

// ───────────────────────────── Contrôle qualité ─────────────────────────────
function checkWords(raw, { langue = "fr", whatsapp = false } = {}) {
  const res = { erreurs: [], alertes: [], infos: [] };
  if (!raw.length) {
    res.erreurs.push("Transcription vide.");
    return res;
  }
  const music = raw.filter((w) => MUSIC_RE.test(String(w.text || "")) || !String(w.text || "").trim()).length;
  const ratio = music / raw.length;
  if (ratio > 0.2) res.erreurs.push(`${Math.round(ratio * 100)} % de jetons musique/vides (> 20 %) : transcription ratée → relancer avec un modèle plus grand (medium) ou fournir le texte.`);
  const toks = raw.map((w) => norm(w.text)).filter(Boolean);
  const fr = toks.filter((t) => STOP_FR.has(t)).length, en = toks.filter((t) => STOP_EN.has(t)).length;
  if (langue === "fr" && toks.length >= 12 && en > fr)
    res.erreurs.push(`Le texte semble en ANGLAIS (${en} mots-outils anglais contre ${fr} français) alors que la voix est en français : la transcription a probablement été faite avec un modèle « .en » qui TRADUIT. Relancer : npx hyperframes transcribe <fichier> --model small --language fr`);
  let back = 0, short = 0, overlap = 0;
  for (let i = 0; i < raw.length; i++) {
    const w = raw[i];
    if (!(Number.isFinite(w.start) && Number.isFinite(w.end))) continue;
    if (w.end - w.start < 0.05) short++;
    if (i && w.start < raw[i - 1].start) back++;
    if (i && w.start < raw[i - 1].end - 0.01) overlap++;
  }
  if (back) res.alertes.push(`${back} mot(s) hors ordre chronologique (corrigé par « fix »).`);
  if (overlap) res.alertes.push(`${overlap} chevauchement(s) de mots (corrigé par « fix »).`);
  if (short / raw.length > 0.1) res.alertes.push(`${short} mot(s) de moins de 50 ms : alignement peu fiable, vérifier le karaoké à l'aperçu.`);
  const hs = detectHallucinations(raw.map((w) => ({ ...w, text: String(w.text || "") })));
  for (const h of hs) (h.auto ? res.erreurs : res.alertes).push(`Hallucination Whisper probable ${h.label} à ${h.at.toFixed(2)} s${h.auto ? " (retirée par « fix »)" : " — vérifier à l'écoute"}.`);
  const gaps = [];
  for (let i = 1; i < raw.length; i++) if (raw[i].start - raw[i - 1].end > 2) gaps.push(`${raw[i - 1].end.toFixed(1)}–${raw[i].start.toFixed(1)} s`);
  if (gaps.length) res.infos.push(`Silences > 2 s : ${gaps.slice(0, 6).join(", ")}${gaps.length > 6 ? "…" : ""} (pas de sous-titre affiché, normal).`);
  if (raw.some((w) => w.approx)) res.alertes.push("Minutage reconstitué depuis des phrases (SRT/VTT) : le karaoké mot à mot est approximatif. Préférer une transcription mot à mot de la voix off.");
  const dur = Math.max(...raw.map((w) => w.end || 0));
  res.infos.push(`${raw.length} mots, voix jusqu'à ${dur.toFixed(1)} s, ${Math.round((raw.length / Math.max(dur, 1)) * 60)} mots/min.`);
  if (whatsapp && dur > 90) res.erreurs.push(`Durée ${dur.toFixed(1)} s > 90 s : hors limite Statut WhatsApp, découper.`);
  return res;
}

function printCheck(res) {
  for (const e of res.erreurs) console.log("✖ " + e);
  for (const a of res.alertes) console.log("⚠ " + a);
  for (const i of res.infos) console.log("• " + i);
  console.log(res.erreurs.length ? "\nRésultat : À CORRIGER avant de sous-titrer." : "\nRésultat : utilisable.");
}

// ───────────────────────────── Groupes ─────────────────────────────
function displayText(t, st, ponct) {
  let s = t;
  const mode = ponct === "auto" ? st.ponctuation : ponct;
  if (mode === "auto") s = s.replace(/[.,;:]+(?=[»"”)]*$)/u, "").replace(/…$/u, "");
  s = s.replace(/\s*([?!;:»])$/u, NNBSP + "$1").replace(/(\d)\s?%/u, "$1" + NNBSP + "%").replace(/«\s*/u, "«" + NNBSP);
  return s || t;
}

const isFn = (w) => FONCTION.has(norm(splitPunct(w.text).core)) || /^(?:jusqu|lorsqu|puisqu|qu|[ldjnmstc])['’]$/i.test(splitPunct(w.text).core);

// Locutions à ne jamais couper.
const LOCUTIONS = ["parce que", "afin de", "afin que", "grace a", "il y a", "par exemple", "en effet", "au moins",
  "tout le monde", "de plus en plus", "bien que", "alors que", "tandis que", "c'est-a-dire", "a travers", "en faveur de"]
  .map((l) => l.split(" ").map(norm));

// Liaisons : mots qui ne doivent pas être séparés du suivant (locution, expression d'emphase, chiffre + nom).
function markBinds(words, lex, user) {
  const n = words.map((w) => norm(splitPunct(w.text).core));
  const phrases = [...LOCUTIONS, ...lex.emphase, ...user, ...lex.expressions.map((e) => e.keys)].filter((k) => k.length > 1);
  for (const keys of phrases)
    for (let i = 0; i + keys.length <= n.length; i++)
      if (keys.every((k, j) => n[i + j] === k)) for (let j = 0; j < keys.length - 1; j++) words[i + j].bind = true;
  words.forEach((w, i) => {
    const next = words[i + 1];
    if (next && /\d/.test(w.text) && !/[.,;:!?…]$/.test(w.text) && !isFn(next) && !/\d/.test(next.text)) w.bind = true;
  });
}

function buildGroups(words, st, fmt, o) {
  const maxW = Number(o["max-mots"]) || st.mots[fmt];
  const maxC = Number(o["max-car"]) || st.car[fmt];
  const pause = o.pause !== undefined ? Number(o.pause) : st.pause ?? 0.15;
  const len = (arr) => arr.reduce((n, w) => n + w.display.length, 0) + Math.max(0, arr.length - 1);
  // un mot-outil (« de », « l' », « et »…) compte pour un demi-mot
  const count = (arr) => arr.reduce((n, w) => n + (isFn(w) ? 0.5 : 1), 0);
  const groups = [];
  let cur = [];
  for (const w of words) {
    if (cur.length) {
      const prev = cur[cur.length - 1];
      const gap = w.start - prev.end;
      const sentence = /[.!?…]["»”)]*$/u.test(prev.text);
      const soft = /[,;:]["»”)]*$/u.test(prev.text) && len(cur) >= 0.5 * maxC;
      if (sentence || gap >= pause || soft) {
        groups.push(cur);
        cur = [];
      } else if (count([...cur, w]) > maxW || len([...cur, w]) > maxC) {
        // coupure « mécanique » : reculer avant les mots-outils finaux et les liaisons ouvertes
        let cut = cur.length;
        while (cut > 0 && (isFn(cur[cut - 1]) || cur[cut - 1].bind)) cut--;
        const onlyGlue = cur.every((x) => isFn(x) || x.bind);
        if (cut > 0) {
          groups.push(cur.slice(0, cut));
          cur = cur.slice(cut);
        } else if (len([...cur, w]) > maxC * (onlyGlue ? 1.7 : 1.3)) {
          groups.push(cur);
          cur = [];
        } // sinon : léger dépassement accepté, la taille de police s'ajuste
      }
    }
    cur.push(w);
  }
  if (cur.length) groups.push(cur);
  // mot orphelin en fin de phrase (« … une famille | entière. ») : rééquilibrer avec le groupe précédent
  for (let i = 1; i < groups.length; i++) {
    const g = groups[i], p = groups[i - 1];
    if (g.length !== 1 || p.length < 2) continue;
    const pl = p[p.length - 1];
    if (/[.!?…,;:]["»”)]*$/u.test(pl.text) || g[0].start - pl.end >= pause) continue;
    const all = [...p, ...g];
    if (len(all) <= maxC * (st.lines > 1 ? 1 : 1.2) && count(all) <= maxW + 0.5) {
      groups.splice(i - 1, 2, all);
      i--;
      continue;
    }
    let best = null;
    for (let k = 1; k < all.length - 1; k++) {
      const a = all.slice(0, k), b = all.slice(k);
      const last = a[a.length - 1];
      if (isFn(last) || last.bind || len(a) > maxC || len(b) > maxC) continue;
      const score = Math.abs(len(a) - len(b));
      if (!best || score < best.score) best = { k, score };
    }
    if (best) groups.splice(i - 1, 2, all.slice(0, best.k), all.slice(best.k));
  }
  return groups;
}

function markEmphasis(group, st, lex, user) {
  if (st.noEmphase) return;
  const n = group.map((w) => norm(splitPunct(w.text).core));
  const units = [];
  group.forEach((w, i) => {
    if (/\d/.test(w.text)) units.push({ i, len: 1, p: 3 });
  });
  const phraseMatch = (list, p) => {
    for (const keys of list)
      for (let i = 0; i + keys.length <= n.length; i++) if (keys.every((k, j) => n[i + j] === k)) units.push({ i, len: keys.length, p });
  };
  phraseMatch(user, 2.5);
  phraseMatch(lex.emphase, 1.5);
  group.forEach((w, i) => {
    const c = splitPunct(w.text).core.replace(ELISION_RE, "$2");
    if (/^\p{Lu}{2,}\d*$/u.test(c)) units.push({ i, len: 1, p: 1 });
  });
  if (!units.length) return;
  units.sort((a, b) => b.p - a.p || a.i - b.i);
  const u = units[0];
  for (let k = 0; k < u.len; k++) group[u.i + k].emph = true;
}

function charK(font, weight, upper) {
  if (font.startsWith("Playfair")) return 0.54;
  if (weight >= 800) return upper ? 0.7 : 0.6;
  return upper ? 0.66 : 0.56;
}

function layout(st, fmt, o, scrimA) {
  const F = FORMATS[fmt];
  const [base, min] = st.size[fmt];
  const pos = o.position || "bas";
  const zoneH = Math.ceil(base * (st.lines > 1 ? 3.2 : 2.6));
  let bandY;
  if (o.y !== undefined) bandY = Number(o.y);
  else if (fmt === "16x9") bandY = pos === "haut" ? 110 + base * 0.6 : pos === "milieu" ? F.h / 2 : F.h - 110 - base * (st.lines > 1 ? 1.3 : 0.6);
  else bandY = pos === "haut" ? Math.max(420, F.zoneSure[0] + 20 + zoneH / 2) : pos === "milieu" ? F.h / 2 : F.h - 640;
  bandY = Math.round(bandY);
  const top = Math.round(bandY - zoneH / 2);
  const avail = F.w - 2 * F.marge - (scrimA ? Math.round(base * 1.0) : 0);
  return { F, base, min, zoneH, top, bandY, avail, pos };
}

// ───────────────────────────── Génération de la sous-composition ─────────────────────────────
function styleCss(st, L, scrimA, compId) {
  const fam = (f) => (f.startsWith("Playfair") ? `'${f}', 'EB Garamond', Georgia, serif` : `'${f}', 'Helvetica Neue', Arial, sans-serif`);
  const shadow = scrimA
    ? `0 2px 4px ${NOIR_RGBA(0.55)}`
    : `0 3px 8px ${NOIR_RGBA(0.9)}, 0 0 26px ${NOIR_RGBA(0.6)}, 0 0 2px ${NOIR_RGBA(0.9)}`;
  const lines = [
    `#root { position: absolute; inset: 0; overflow: visible; pointer-events: none; }`,
    `#${compId}-zone { position: absolute; left: ${L.F.marge}px; right: ${L.F.marge}px; top: ${L.top}px; height: ${L.zoneH}px; overflow: visible; }`,
    `.${compId}-g { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; overflow: visible; opacity: 0; visibility: hidden; }`,
    `.${compId}-l { display: inline; font-family: ${fam(st.font)}; font-weight: ${st.weight}; letter-spacing: ${st.tracking}; line-height: ${st.lines > 1 ? 1.32 : 1.16}; word-spacing: ${st.gap}em; color: ${st.color}; ${st.upper ? "text-transform: uppercase; " : ""}${st.lines > 1 ? "white-space: normal; text-wrap: balance; " : "white-space: nowrap; "}text-shadow: ${shadow};${
      scrimA ? ` background: ${NOIR_RGBA(scrimA)}; padding: 0.12em 0.48em; border-radius: 0.3em; -webkit-box-decoration-break: clone; box-decoration-break: clone;` : ""
    } }`,
    `.${compId}-w { display: inline-block; white-space: pre;${st.highlight === "pastille" ? ` padding: 0.02em 0.16em; margin: 0 0.04em; border-radius: 0.2em; background-color: ${OR_RGBA(0)};` : ""} }`,
    `.${compId}-e { color: ${st.emphColor};${st.emphItalic ? " font-style: italic;" : ""} }`,
  ];
  // chiffre-cle : seuls les chiffres passent en Playfair XXL et « tombent » à leur prononciation
  if (st.emphSlam)
    lines.push(`.${compId}-s { opacity: 0;${st.emphFont ? ` font-family: ${fam(st.emphFont)}; font-weight: ${st.emphWeight}; font-size: ${st.emphSize}em; line-height: 1;` : ""} }`);
  return lines.join("\n    ");
}

function generate(words, st, styleName, fmt, o) {
  const compId = String(o.id || "captions").replace(/[^a-zA-Z0-9_-]/g, "");
  const scrimA = o.scrim && o.scrim !== "auto" ? SCRIMS[o.scrim] ?? Number(o.scrim) : st.scrim;
  const L = layout(st, fmt, o, scrimA);
  const lex = loadLexique(o.lexique ?? undefined);
  const user = String(o.emphase || "")
    .split(",")
    .map((s) => s.trim().split(/\s+/).map(norm).filter(Boolean))
    .filter((a) => a.length);
  const ponct = o.ponctuation || "auto";
  const ws = words.map((w) => ({ ...w, display: displayText(w.text, st, ponct) }));
  markBinds(ws, lex, user);
  const raw = buildGroups(ws, st, fmt, o);
  if (!o["sans-emphase"]) raw.forEach((g) => markEmphasis(g, st, lex, user));
  if (st.emphSlam) ws.forEach((w) => (w.slam = !!w.emph && /\d/.test(w.text)));

  const LEAD = 0.06, HOLD = 0.25;
  const k = charK(st.font, st.weight, st.upper);
  const warns = [];
  const groups = raw.map((g, gi) => ({ gi, words: g }));
  groups.forEach((g, i) => {
    const first = g.words[0], last = g.words[g.words.length - 1];
    const next = groups[i + 1];
    g.start = Math.max(0, i ? Math.max(first.start - LEAD, groups[i - 1].end) : first.start - LEAD);
    let end = last.end + HOLD;
    if (next) end = Math.min(end, next.words[0].start - LEAD);
    g.end = Math.max(end, last.end, g.start + 0.3);
    if (next && g.end > next.words[0].start) g.end = Math.max(last.end, next.words[0].start);
  });
  groups.forEach((g, i) => {
    // nouvelle passe : jamais deux groupes à l'écran
    if (i && g.start < groups[i - 1].end) g.start = groups[i - 1].end;
    const d = g.end - g.start;
    g.inDur = r3(Math.min(st.enterTo.duration, d * 0.4));
    g.outDur = r3(Math.min(st.exit, d * 0.3));
    g.start = r3(g.start);
    g.end = r3(g.end);
    g.text = g.words.map((w) => w.display).join(" ");
    const hasEmph = g.words.some((w) => w.emph);
    const hasSlam = g.words.some((w) => w.slam);
    g.scale = Math.max(st.activeScale, hasEmph ? st.emphScale : 1, hasSlam && st.emphSize ? st.emphSize : 1);
    const chars = g.text.length;
    if (st.lines > 1) {
      g.size = L.base;
      const estLines = Math.ceil((chars * k * L.base) / L.avail);
      if (estLines > st.lines) warns.push(`groupe ${g.gi} (« ${g.text} ») ≈ ${estLines} lignes > ${st.lines} : réduire --max-car.`);
    } else {
      const fitSize = Math.floor(L.avail / ((chars * k + (g.words.length - 1) * st.gap) * g.scale) / 2) * 2;
      g.size = Math.max(L.min, Math.min(L.base, fitSize));
      if (fitSize < L.min) warns.push(`groupe ${g.gi} (« ${g.text} ») trop long même à ${L.min} px : réduire --max-car ou --max-mots.`);
    }
  });

  const pfx = compId;
  const markup = groups
    .map((g) => {
      // Chaque mot animé est le DERNIER enfant d'un enveloppeur non animé, l'espace le précède.
      // GSAP, quand il mesure un élément non rendu (scène encore masquée), le retire puis le réinsère
      // devant son élément frère suivant : avec des espaces entre mots, l'espace passait devant le mot
      // (« 12 000enfants »). Sans frère suivant, l'ordre est conservé.
      const spans = g.words
        .map((w, wi) => {
          const cls = [`${pfx}-w`];
          if (w.emph) cls.push(`${pfx}-e`);
          if (w.slam) cls.push(`${pfx}-s`);
          return `<span class="${pfx}-ww">${wi ? " " : ""}<span id="${pfx}-g${g.gi}-w${wi}" class="${cls.join(" ")}">${esc(w.display)}</span></span>`;
        })
        .join("");
      return `      <div id="${pfx}-g${g.gi}" class="${pfx}-g"><span class="${pfx}-l" style="font-size: ${g.size}px">${spans}</span></div>`;
    })
    .join("\n");

  const runtimeGroups = groups.map((g) => ({
    id: `${pfx}-g${g.gi}`,
    start: g.start,
    end: g.end,
    inDur: g.inDur,
    outDur: g.outDur,
    scale: r3(g.scale),
    size: g.size,
    text: g.text,
    spaces: g.words.length - 1,
    words: g.words.map((w, wi) => ({ id: `${pfx}-g${g.gi}-w${wi}`, start: r3(w.start), end: r3(w.end), e: w.emph ? 1 : 0, s: w.slam ? 1 : 0 })),
  }));
  const S = {
    font: st.font, weight: st.weight, upper: st.upper, fit: st.fit && st.lines === 1,
    maxWidth: L.avail, base: L.base, min: L.min,
    highlight: st.highlight, color: st.color, active: st.active, emphColor: st.emphColor,
    activeScale: st.activeScale, emphScale: st.emphScale, lift: st.lift, gap: st.gap, slam: !!st.emphSlam,
    pillOn: OR_RGBA(1), pillOff: OR_RGBA(0),
    enterFrom: st.enterFrom, enterTo: { ...st.enterTo, duration: undefined },
  };
  delete S.enterTo.duration;

  const duration = r3(Math.ceil((groups[groups.length - 1].end + 0.3) * 10) / 10);
  const html = `<!--
  Sous-titres dynamiques — style « ${styleName} » (${st.label}), format ${fmt} (${L.F.w}×${L.F.h}).
  Généré par .claude/skills/sous-titres-dynamiques/scripts/captions.mjs — ${groups.length} groupes, ${words.length} mots, ${duration} s.
  Ne pas retoucher les minutages à la main : corriger la transcription puis régénérer.
-->
<template>
  <style>
    ${styleCss(st, L, scrimA, pfx)}
  </style>
  <div id="root" data-composition-id="${compId}" data-width="${L.F.w}" data-height="${L.F.h}">
    <div id="${pfx}-zone">
${markup}
    </div>
  </div>
  <script>
    (function () {
      var COMP = ${JSON.stringify(compId)};
      var S = ${JSON.stringify(S)};
      var GROUPS = ${JSON.stringify(runtimeGroups)};
      var tl = gsap.timeline({ paused: true });
      var hf = window.__hyperframes;
      var canFit = S.fit && hf && typeof hf.fitTextFontSize === "function";

      GROUPS.forEach(function (g) {
        var el = document.getElementById(g.id);
        if (!el) return;
        if (canFit) {
          var r = hf.fitTextFontSize(S.upper ? g.text.toUpperCase() : g.text, {
            fontFamily: S.font, fontWeight: S.weight, maxWidth: Math.floor((S.maxWidth - g.spaces * S.gap * S.base) / g.scale),
            baseFontSize: S.base, minFontSize: S.min, step: 2
          });
          if (r && r.fontSize) el.firstElementChild.style.fontSize = r.fontSize + "px";
        }
        // entrée du groupe
        tl.set(el, { visibility: "visible" }, g.start);
        tl.fromTo(el, S.enterFrom, Object.assign({}, S.enterTo, { duration: g.inDur }), g.start);

        // karaoké mot à mot
        g.words.forEach(function (w, i) {
          var we = document.getElementById(w.id);
          if (!we) return;
          var restColor = w.e ? S.emphColor : S.color;
          var on = Math.max(0.04, Math.min(0.1, (w.end - w.start) * 0.5));
          if (w.s) {
            tl.fromTo(we, { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: 0.28, ease: "expo.out", immediateRender: false }, Math.max(g.start, w.start - 0.04));
            return;
          }
          if (S.highlight === "aucun") return;
          var onVars = { scale: w.e ? S.emphScale : S.activeScale, yPercent: -S.lift, duration: on, ease: w.e ? "back.out(2)" : "power2.out", immediateRender: false };
          var fromVars = { scale: 1, yPercent: 0 };
          if (S.highlight === "pastille") {
            fromVars.backgroundColor = S.pillOff; fromVars.color = restColor;
            onVars.backgroundColor = S.pillOn; onVars.color = S.active;
          } else {
            fromVars.color = restColor;
            onVars.color = w.e ? S.emphColor : S.active;
          }
          tl.fromTo(we, fromVars, onVars, w.start);
          // le dernier mot du groupe reste actif jusqu'à la sortie du groupe
          if (i < g.words.length - 1) {
            var offVars = Object.assign({}, fromVars, { duration: 0.12, ease: "power1.out", immediateRender: false });
            var offFrom = Object.assign({}, onVars);
            delete offFrom.duration; delete offFrom.ease; delete offFrom.immediateRender;
            tl.fromTo(we, offFrom, offVars, Math.max(w.end, w.start + on));
          }
        });

        // sortie + arrêt franc (aucun groupe ne reste affiché)
        tl.to(el, { opacity: 0, duration: g.outDur, ease: "power2.in" }, g.end - g.outDur);
        tl.set(el, { opacity: 0, visibility: "hidden" }, g.end);
      });

      // auto-contrôle : chaque groupe doit être masqué juste après sa fin
      GROUPS.forEach(function (g, gi) {
        var el = document.getElementById(g.id);
        if (!el) return;
        tl.seek(g.end + 0.01);
        var cs = window.getComputedStyle(el);
        if (cs.opacity !== "0" && cs.visibility !== "hidden") {
          console.warn("[caption-lint] groupe " + gi + " encore visible à t=" + (g.end + 0.01).toFixed(2) + " s");
        }
      });
      tl.seek(0);
      window.__timelines[COMP] = tl;
    })();
  </script>
</template>
`;
  // contrôles de construction
  for (let i = 1; i < groups.length; i++)
    if (groups[i].start < groups[i - 1].end - 1e-6) warns.push(`groupes ${i - 1} et ${i} se chevauchent.`);
  if (fmt === "9x16") {
    const [y0, y1] = FORMATS["9x16"].zoneSure;
    if (L.top < y0 || L.top + L.zoneH > y1) warns.push(`zone sous-titres y ${L.top}–${L.top + L.zoneH} hors zone sûre ${y0}–${y1} (CLAUDE.md).`);
  }
  if (o.whatsapp && duration > 90) warns.push(`durée ${duration} s > 90 s : hors limite Statut WhatsApp, découper.`);
  return { html, groups, duration, warns, L, compId, scrimA };
}

// ───────────────────────────── Planche de styles (aperçu statique) ─────────────────────────────
const PLANCHE_TEXTES = {
  "or-karaoke": "Chaque enfant compte, chaque dose protège",
  pastille: "Vaccinez maintenant",
  editorial: "Derrière chaque chiffre, une famille",
  "chiffre-cle": "90 % des enfants protégés",
  "mot-a-mot": "Zéro dose",
  institutionnel: "La vaccination de routine protège chaque enfant contre des maladies évitables.",
};

function planche(fmt, o) {
  const tiles = [];
  for (const [name, st] of Object.entries(STYLES)) {
    for (const fond of ["sombre", "clair"]) {
      const scrimA = fond === "clair" ? SCRIMS.plein : st.scrim;
      const L = layout(st, fmt, o, scrimA);
      const words = cleanWords(
        PLANCHE_TEXTES[name].split(" ").map((t, i) => ({ text: t, start: i * 0.4, end: i * 0.4 + 0.35 })),
        { lexique: null, log: [], fillers: false, autoHallu: false },
      );
      const r = generate(words, st, name, fmt, { ...o, scrim: scrimA ? String(scrimA) : "aucun", lexique: o.lexique });
      const g = r.groups[0];
      const activeIdx = Math.min(1, g.words.length - 1);
      const id = `pl-${name}-${fond}`;
      const css = styleCss(st, L, scrimA, id).replace(/#root/g, `#${id}`).replace(`opacity: 0; visibility: hidden;`, "");
      const spans = g.words
        .map((w, wi) => {
          const cls = [`${id}-w`];
          if (w.emph) cls.push(`${id}-e`);
          let style = "";
          if (wi === activeIdx && st.highlight !== "aucun" && !w.slam) {
            const sc = w.emph ? st.emphScale : st.activeScale;
            const tf = `transform:translateY(-${st.lift}%) scale(${sc})`;
            style = st.highlight === "pastille" ? `background-color:${OR_RGBA(1)};color:${st.active};${tf}` : `color:${w.emph ? st.emphColor : st.active};${tf}`;
          }
          return `<span class="${id}-ww">${wi ? " " : ""}<span class="${cls.join(" ")}" style="${style}">${esc(w.display)}</span></span>`;
        })
        .join("");
      const bg = fond === "sombre" ? "linear-gradient(160deg,#2a3138 0%,#151a1f 55%,#0B0B0C 100%)" : "linear-gradient(160deg,#f4efe6 0%,#d8cdb8 60%,#bfae8f 100%)";
      tiles.push(`<figure><div class="frame" style="width:${L.F.w}px;height:${L.F.h}px"><div id="${id}" style="position:absolute;inset:0;background:${bg}"><style>${css}</style><div id="${id}-zone"><div class="${id}-g"><span class="${id}-l" style="font-size:${g.size}px">${spans}</span></div></div></div></div><figcaption><b>${esc(name)}</b> — ${esc(st.label)}<br>${esc(st.usage)} · fond ${fond}${scrimA ? ` · voile ${Math.round(scrimA * 100)} %` : ""}</figcaption></figure>`);
    }
  }
  const zoom = fmt === "16x9" ? 0.3 : 0.2;
  return `<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Planche des styles de sous-titres</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
<style>body{margin:0;padding:32px;background:#0B0B0C;color:#F6F1E7;font-family:Inter,Arial,sans-serif}h1{font-family:'Playfair Display',serif;color:#E3B34C;font-size:34px;margin:0 0 6px}p.sub{margin:0 0 24px;font-size:16px}.grid{display:grid;grid-template-columns:repeat(2,max-content);gap:24px}figure{margin:0}.frame{position:relative;overflow:hidden;zoom:${zoom};border:3px solid #333}figcaption{font-size:14px;line-height:1.4;margin-top:8px;max-width:${Math.round((fmt === "16x9" ? 1920 : 1080) * zoom)}px}figcaption b{color:#E3B34C}</style></head>
<body><h1>Sous-titres dynamiques — planche des styles (${fmt})</h1><p class="sub">Image arrêtée : 2ᵉ mot actif. Fonds neutres de test (pas de photo). Chiffres : données illustratives.</p><div class="grid">${tiles.join("")}</div></body></html>`;
}

// ───────────────────────────── Luminance de la bande (ffmpeg) ─────────────────────────────
function luminance(video, st, fmt, o) {
  if (!video || !fs.existsSync(video)) fail(`Vidéo introuvable : ${video}`);
  const L = layout(st, fmt, o, 0);
  const yFrac = Math.max(0, L.top / L.F.h), hFrac = Math.min(1 - yFrac, L.zoneH / L.F.h);
  const xFrac = L.F.marge / L.F.w;
  const vf = `fps=2,crop=iw*${(1 - 2 * xFrac).toFixed(4)}:ih*${hFrac.toFixed(4)}:iw*${xFrac.toFixed(4)}:ih*${yFrac.toFixed(4)},signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-`;
  let out;
  try {
    out = execFileSync("ffmpeg", ["-hide_banner", "-nostats", "-loglevel", "error", "-i", video, "-vf", vf, "-an", "-f", "null", "-"], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  } catch (e) {
    fail("ffmpeg a échoué : " + (e.stderr || e.message));
  }
  let vals = [...out.matchAll(/lavfi\.signalstats\.YAVG=([\d.]+)/g)].map((m) => Number(m[1]));
  if (!vals.length) fail("Aucune mesure (vidéo vide ?).");
  if (Math.max(...vals) > 255) vals = vals.map((v) => v / 4); // vidéo 10 bits
  vals.sort((a, b) => a - b);
  const q = (p) => vals[Math.min(vals.length - 1, Math.floor(p * vals.length))];
  const med = q(0.5), p90 = q(0.9);
  let reco;
  if (p90 < 60) reco = "fond sombre : ombre portée seule suffit (--scrim aucun).";
  else if (p90 <= 150) reco = "fond moyen : --scrim doux (voile local 45 %).";
  else reco = "fond clair : --scrim plein (voile local 70 %), ou déplacer la bande sur une zone plus sombre (--position / --y).";
  console.log(`Bande y ${L.top}–${L.top + L.zoneH} px (${fmt}), ${vals.length} images mesurées (2 i/s).`);
  console.log(`Luminance moyenne (0–255) : min ${vals[0].toFixed(0)} · médiane ${med.toFixed(0)} · 90ᵉ centile ${p90.toFixed(0)} · max ${vals[vals.length - 1].toFixed(0)}`);
  console.log("Recommandation : " + reco);
}

// ───────────────────────────── CLI ─────────────────────────────
function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const eq = a.indexOf("=");
      if (eq > -1) out[a.slice(2, eq)] = a.slice(eq + 1);
      else if (i + 1 < argv.length && !argv[i + 1].startsWith("--")) out[a.slice(2)] = argv[++i];
      else out[a.slice(2)] = true;
    } else out._.push(a);
  }
  return out;
}

const AIDE = `Sous-titres dynamiques — charte Dian K Pro (HyperFrames)

  node captions.mjs check <transcript.json|.srt|.vtt> [--langue fr] [--whatsapp]
  node captions.mjs fix <entrée> [--out mots.json] [--lexique fichier.json|aucun] [--garder-hesitations]
  node captions.mjs from-srt <fichier.srt|.vtt> [--out mots.json]
  node captions.mjs build <mots.json> --style <nom> --format 16x9|9x16
        [--out compositions/captions.html] [--id captions] [--position bas|milieu|haut] [--y <px>]
        [--scrim auto|aucun|doux|plein] [--emphase "Gavi,zéro dose"] [--sans-emphase]
        [--max-mots N] [--max-car N] [--pause 0.15] [--ponctuation auto|garder] [--whatsapp]
  node captions.mjs planche --format 16x9|9x16 [--out planche.html]
  node captions.mjs luminance <video.mp4> --style <nom> --format 16x9|9x16 [--position …]
  node captions.mjs styles
`;

function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const o = parseArgs(rest);
  const fmt = o.format ? String(o.format).replace(":", "x") : undefined;
  const needFmt = () => {
    if (!FORMATS[fmt]) fail("--format 16x9 ou 9x16 requis.");
    return fmt;
  };
  const needStyle = () => {
    const s = STYLES[o.style];
    if (!s) fail(`--style requis parmi : ${Object.keys(STYLES).join(", ")}`);
    return s;
  };
  switch (cmd) {
    case "styles":
      for (const [k, s] of Object.entries(STYLES))
        console.log(`${k.padEnd(15)} ${s.label}\n${"".padEnd(15)} usage : ${s.usage} · énergie ${s.energie} · ${s.mots["16x9"]}/${s.mots["9x16"]} mots par groupe (16:9 / 9:16)`);
      break;
    case "check": {
      const { words } = loadWords(o._[0]);
      const res = checkWords(words, { langue: o.langue || "fr", whatsapp: !!o.whatsapp });
      printCheck(res);
      if (res.erreurs.length) process.exitCode = 1;
      break;
    }
    case "fix":
    case "from-srt": {
      const { words } = loadWords(o._[0]);
      const log = [];
      const lex = cmd === "fix" ? loadLexique(o.lexique) : null;
      const clean = cleanWords(words, { lexique: lex, log, fillers: cmd === "fix" && !o["garder-hesitations"] });
      const outFile = o.out || o._[0].replace(/\.(json|srt|vtt)$/i, "") + ".propre.json";
      fs.writeFileSync(outFile, JSON.stringify(clean, null, 1) + "\n");
      for (const l of log) console.log("• " + l);
      console.log(`✔ ${clean.length} mots → ${outFile}`);
      const res = checkWords(clean, { langue: o.langue || "fr", whatsapp: !!o.whatsapp });
      if (res.erreurs.length || res.alertes.length) printCheck(res);
      break;
    }
    case "build": {
      const st = needStyle();
      needFmt();
      const { words, source } = loadWords(o._[0]);
      const clean = cleanWords(words, { lexique: null, log: [], fillers: false, autoHallu: false });
      if (!clean.length) fail("Aucun mot exploitable.");
      const r = generate(clean, st, o.style, fmt, o);
      const outFile = o.out || "compositions/captions.html";
      fs.mkdirSync(path.dirname(path.resolve(outFile)), { recursive: true });
      fs.writeFileSync(outFile, r.html);
      console.log(`✔ ${outFile} — style ${o.style}, ${fmt}, ${r.groups.length} groupes, ${r.duration} s${source === "phrases" ? " (minutage approximatif : source en phrases)" : ""}`);
      console.log(`  bande sous-titres : y ${r.L.top}–${r.L.top + r.L.zoneH} px, largeur utile ${r.L.avail} px, voile ${r.scrimA ? Math.round(r.scrimA * 100) + " %" : "aucun"}`);
      const emph = r.groups.flatMap((g) => g.words.filter((w) => w.emph).map((w) => w.display));
      if (emph.length) console.log(`  mots en emphase (${emph.length}) : ${emph.slice(0, 20).join(" · ")}${emph.length > 20 ? " …" : ""}`);
      for (const w of r.warns) console.log("⚠ " + w);
      console.log(`\nHôte à placer dans index.html (data-start = instant où démarre la voix off) :\n
<div id="${r.compId}" data-composition-id="${r.compId}" data-composition-src="${outFile.replace(/^\.\//, "")}"
     data-start="0" data-duration="${r.duration}" data-track-index="20" data-track-kind="captions"
     data-width="${r.L.F.w}" data-height="${r.L.F.h}" style="z-index: 40"></div>`);
      break;
    }
    case "planche": {
      needFmt();
      const outFile = o.out || `planche-sous-titres-${fmt}.html`;
      fs.writeFileSync(outFile, planche(fmt, o));
      console.log(`✔ ${outFile}`);
      break;
    }
    case "luminance":
      luminance(o._[0], needStyle(), needFmt(), o);
      break;
    default:
      console.log(AIDE);
  }
}

main();
