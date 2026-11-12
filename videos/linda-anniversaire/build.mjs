// Générateur de composition HyperFrames — « Linda, une année de plus de lumière »
// Usage : node build.mjs <youtube|whatsapp|statut>   → écrit index.html
//   youtube  : 16:9 1920×1080, chanson complète (2 min 05)
//   whatsapp : 9:16 1080×1920, chanson complète (message WhatsApp, Shorts)
//   statut   : 9:16 1080×1920, montage ≤ 90 s (Statut WhatsApp)
import { readFileSync, writeFileSync } from "node:fs";

const variant = process.argv[2] || "youtube";
const FULL = 124.82;
const VARIANTS = {
  youtube: { W: 1920, H: 1080, L: "L", segs: [[0, FULL]], audio: "assets/song.mp3", fadeOut: 2 },
  whatsapp: { W: 1080, H: 1920, L: "P", segs: [[0, FULL]], audio: "assets/song.mp3", fadeOut: 2 },
  statut: {
    W: 1080, H: 1920, L: "P",
    // coupes calées sur la mesure (16 et 32 temps à 111 BPM) — même découpe que assets/song-90s.mp3
    segs: [[5.5, 21.965], [30.605, 84.2], [101.48, 120.9]],
    audio: "assets/song-90s.mp3", fadeOut: 0,
  },
};
const V = VARIANTS[variant];
if (!V) throw new Error("variante inconnue : " + variant);
const { W, H, L } = V;
const P = L === "P";

// ── Correspondance temps chanson → temps vidéo ───────────────────────────
let acc = 0;
const SEGS = V.segs.map(([a, b]) => { const s = { a, b, o: acc }; acc += b - a; return s; });
const DUR = +acc.toFixed(3);
const map = (t) => { for (const s of SEGS) if (t >= s.a - 1e-6 && t <= s.b + 1e-6) return s.o + t - s.a; return null; };
const mapC = (t) => { // temps coupé → début du segment conservé suivant
  for (const s of SEGS) { if (t < s.a) return s.o; if (t <= s.b) return s.o + t - s.a; }
  return DUR;
};
const r3 = (x) => +x.toFixed(3);

// ── PRNG déterministe ─────────────────────────────────────────────────────
let seed = 20261112;
const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
const rr = (a, b) => a + (b - a) * rnd();

// ── Contenu ───────────────────────────────────────────────────────────────
// Chaque ligne : segments [texte, début, fin] en temps chanson (alignement mot-à-mot Suno).
// *…* = mot mis en valeur (or, italique).
const c = (lines, o = {}) => ({ lines, ...o });
const SCENES = [
  {
    id: "intro", s: 0, e: 21.55, photo: "linda", lay: "A", eyebrow: "L’OMS Djibouti célèbre",
    cards: [
      { cover: true, s: 0, e: 7.3 },
      c([[["Aujourd’hui, c’est ton jour,", 7.87, 9.3], ["*Linda !*", 9.52, 10.29]]]),
      c([[["À l’OMS *Djibouti,*", 11.96, 13.63], ["on te célèbre !", 13.72, 15.5]]]),
      c([[["*Hambalyo,* Linda !", 15.83, 17.62], ["*Hambalyo !*", 17.97, 19.2]]]),
      c([[["Joyeux *anniversaire !*", 19.69, 21.24]]]),
    ],
  },
  {
    id: "instr", s: 21.55, e: 30.55, photo: "kora", lay: "K", eyebrow: "En somali",
    cards: [{ custom: "hambalyo", s: 22.3, e: 30.2 }],
  },
  {
    id: "verse", s: 30.55, e: 56.05, photo: "linda", lay: "B", eyebrow: "Pour Linda",
    cards: [
      c([[["Chère *Linda,*", 30.9, 31.88], ["toujours attentionnée,", 32.64, 34.07]]]),
      c([[["À nos côtés,", 35.11, 36.1], ["tu sais nous *accompagner.*", 36.7, 38.41]]]),
      c([[["Auprès de la Représentante", 39.32, 41.15], ["de *l’OMS,*", 41.63, 42.94]]]),
      c([[["Ton *engagement*", 43.71, 44.84], ["fait la différence !", 45.61, 46.94]]]),
      c([[["Une année de plus,", 47.82, 48.95], ["une année de *sagesse,*", 49.83, 51.19]]]),
      c([[["Que la vie t’apporte", 52.14, 53.66], ["*joie* et *tendresse !*", 54.19, 55.54]]]),
    ],
  },
  {
    id: "chorus", s: 56.05, e: 75.45, photo: "linda", lay: "C", eyebrow: "Hambalyo · Joyeux anniversaire",
    confetti: 54, pulse: true,
    cards: [
      c([
        [["*Linda, Linda,*", 56.4, 57.36], ["joyeux anniversaire !", 57.45, 59.0]],
        [["*Hambalyo, hambalyo,*", 60.18, 62.52], ["Linda !", 62.55, 63.1]],
      ]),
      c([
        [["*Farxad iyo caafimaad !*", 63.28, 65.44]],
        [["Bonheur et santé pour toi !", 65.45, 67.33]],
      ]),
      c([
        [["*Linda, Linda,*", 67.68, 68.77], ["aujourd’hui on danse !", 69.0, 71.65]],
        [["Que tous tes *rêves*", 71.96, 73.6], ["deviennent réalité !", 73.6, 75.14]],
      ]),
    ],
  },
  {
    id: "bridge", s: 75.45, e: 84.0, photo: "kora", lay: "K", eyebrow: "Kora mandingue · Voix somalie",
    cards: [
      c([
        [["*Sanad wanaagsan,* Linda !", 75.7, 77.43]],
        [["*Guul iyo farxad badan !*", 77.69, 79.4]],
      ], { gloss: ["« Une belle année, Linda ! »", "« Réussite et beaucoup de joie ! »"] }),
      c([
        [["Que la *réussite*", 79.61, 80.4], ["illumine tes pas,", 80.4, 81.5]],
        [["Que le *bonheur*", 81.82, 82.47], ["reste auprès de toi !", 82.47, 83.8]],
      ]),
    ],
  },
  {
    id: "wishes", s: 84.0, e: 101.4, photo: "linda", lay: "A", eyebrow: "Nos vœux pour toi",
    cards: [{ custom: "wishes", s: 84.5, e: 101.0 }],
  },
  {
    id: "final", s: 101.4, e: 110.8, photo: "linda", lay: "C", eyebrow: "Toute l’OMS Djibouti",
    confetti: 46, pulse: true,
    cards: [
      c([
        [["*Linda, Linda,* hambalyo !", 101.69, 103.61]],
        [["Toute l’OMS te dit *bravo !*", 103.9, 105.7]],
      ]),
      c([
        [["Une année de plus,", 105.89, 106.82], ["de *sagesse* et *d’amour,*", 106.82, 107.88]],
        [["Que la joie t’accompagne", 107.88, 109.46], ["*toujours !*", 109.68, 110.32]],
      ]),
    ],
  },
  {
    id: "outro", s: 110.8, e: 119.0, photo: "linda", lay: "A", eyebrow: "Avec toute notre affection",
    confetti: 30,
    cards: [
      c([[["Happy Birthday,", 111.15, 112.64], ["*Linda !*", 112.82, 113.74]]], { big: true }),
      c([[["*Hambalyo,*", 115.04, 116.6], ["Linda !", 118.33, 118.85]]], { big: true }),
    ],
  },
  { id: "sig", s: 119.0, e: 999, lay: "S", cards: [] },
];

// ── Mise en page (px) ─────────────────────────────────────────────────────
const LAY = P
  ? {
      A: { txt: [70, 1085, 940, 520], align: "center" },
      B: { txt: [70, 1175, 940, 430], align: "center", strings: [70, 1130, 940, 520] },
      C: { txt: [60, 940, 960, 660], align: "center", strings: [60, 930, 960, 680] },
      K: { txt: [70, 1060, 940, 540], align: "center" },
      lyric: 74, couplet: 66, big: 104, eyebrow: 32, gloss: 36,
    }
  : {
      A: { txt: [110, 150, 900, 780], align: "left", strings: [110, 90, 880, 900] },
      B: { txt: [930, 150, 880, 780], align: "left", strings: [930, 90, 880, 900] },
      C: { txt: [160, 585, 1600, 440], align: "center", strings: [160, 600, 1600, 420] },
      K: { txt: [110, 150, 900, 780], align: "left" },
      lyric: 86, couplet: 74, big: 124, eyebrow: 30, gloss: 36,
    };

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const box = ([l, t, w, h]) => `left:${l}px;top:${t}px;width:${w}px;height:${h}px;`;

// ── Construction ──────────────────────────────────────────────────────────
const A = []; // animations : [sélecteur, from|null, to, t]
const fromTo = (sel, f, to, t) => A.push([sel, f, to, r3(Math.max(0, t))]);
const to = (sel, v, t) => A.push([sel, null, v, r3(Math.max(0, t))]);
let uid = 0;
const nid = (p) => `${p}${++uid}`;

// scènes conservées dans cette variante
const kept = [];
for (const sc of SCENES) {
  const e = Math.min(sc.e, FULL);
  let best = null;
  for (const s of SEGS) {
    const a = Math.max(sc.s, s.a), b = Math.min(e, s.b);
    if (b - a > 1.2 && (!best || b - a > best.b - best.a)) best = { a, b };
  }
  if (best) kept.push({ ...sc, os: map(best.a) });
}
kept.forEach((sc, i) => { sc.oe = i < kept.length - 1 ? kept[i + 1].os : DUR; });

const words = (segs) => { // → [{text, em, t}]
  const out = [];
  for (const [text, t0, t1] of segs) {
    const toks = [];
    let em = false;
    for (const raw of text.split(" ")) {
      let w = raw, isEm = em;
      if (w.startsWith("*")) { isEm = true; em = true; w = w.slice(1); }
      if (w.endsWith("*")) { em = false; w = w.slice(0, -1); }
      toks.push({ text: w, em: isEm });
    }
    // rattache la ponctuation isolée (« ! ») au mot précédent
    const merged = [];
    for (const tk of toks) {
      if (/^[!?:;»]+$/.test(tk.text) && merged.length) merged[merged.length - 1].text += " " + tk.text;
      else merged.push(tk);
    }
    const tot = merged.reduce((n, m) => n + m.text.length, 0);
    let k = 0;
    for (const m of merged) { m.t = t0 + ((t1 - t0) * k) / tot; k += m.text.length; out.push(m); }
  }
  return out;
};

const ornament = `<svg class="orn" viewBox="0 0 220 24" width="220" height="24" aria-hidden="true"><path d="M0 12h78M142 12h78" stroke="#E3B34C" stroke-width="2"/><path d="M110 2l10 10-10 10-10-10z" fill="#E3B34C"/><path d="M88 12l6-6 6 6-6 6zM120 12l6-6 6 6-6 6z" fill="none" stroke="#E3B34C" stroke-width="2"/></svg>`;

function photoHTML(sc, sid) {
  const img = sc.photo === "kora" ? "assets/kora.jpg" : "assets/linda.jpg";
  const dur = sc.oe - sc.os + 0.8;
  const kb = (sel, s0, s1, origin) =>
    fromTo(sel, { scale: s0, transformOrigin: origin }, { scale: s1, duration: r3(dur), ease: "none" }, sc.os - 0.4);
  const iid = nid("im");
  if (sc.lay === "K") {
    kb("#" + iid, 1.04, 1.16, P ? "55% 45%" : "60% 42%");
    return `<div class="ph ph-full"${P ? "" : ' style="left:270px"'}><img id="${iid}" src="${img}" alt="" style="object-position:${P ? "50% 40%" : "50% 46%"}"></div><div class="shade shade-k"></div>`;
  }
  if (sc.lay === "A") {
    if (P) {
      kb("#" + iid, 1.0, 1.07, "50% 28%");
      return `<div class="ph ph-full"><img id="${iid}" src="${img}" alt="" style="object-position:50% 50%"></div><div class="shade shade-pa"></div>`;
    }
    kb("#" + iid, 1.0, 1.07, "50% 28%");
    return `<div class="glow" style="left:960px;top:40px;width:1000px;height:1000px"></div><div class="frame arch" style="left:1086px;top:46px;width:748px;height:988px"></div><div class="ph arch" style="left:1100px;top:60px;width:720px;height:960px"><img id="${iid}" src="${img}" alt=""></div>`;
  }
  if (sc.lay === "B") {
    if (P) {
      kb("#" + iid, 1.12, 1.2, "50% 20%");
      return `<div class="glow" style="left:40px;top:180px;width:1000px;height:1000px"></div><div class="frame arch" style="left:126px;top:256px;width:828px;height:868px"></div><div class="ph arch" style="left:140px;top:270px;width:800px;height:840px"><img id="${iid}" src="${img}" alt="" style="object-position:50% 6%"></div>`;
    }
    kb("#" + iid, 1.28, 1.38, "50% 20%");
    return `<div class="glow" style="left:-30px;top:40px;width:1000px;height:1000px"></div><div class="frame arch" style="left:96px;top:46px;width:748px;height:988px"></div><div class="ph arch" style="left:110px;top:60px;width:720px;height:960px"><img id="${iid}" src="${img}" alt="" style="object-position:50% 0%"></div>`;
  }
  // C — médaillon
  const d = P ? 620 : 480, x = (W - d) / 2, y = P ? 275 : 62;
  kb("#" + iid, 1.42, 1.52, "50% 27%");
  const ring = nid("rg");
  if (sc.pulse) {
    for (const b of BEATS) {
      const t = map(b);
      if (t === null || t < sc.os + 0.4 || t > sc.oe - 0.3) continue;
      fromTo("#" + ring, { scale: 1.045 }, { scale: 1, duration: 0.42, ease: "power2.out" }, t);
    }
  }
  return `<div class="glow" style="left:${x - 260}px;top:${y - 260}px;width:${d + 520}px;height:${d + 520}px"></div><div id="${ring}" class="frame circ" style="left:${x - 16}px;top:${y - 16}px;width:${d + 32}px;height:${d + 32}px"></div><div class="ph circ" style="left:${x}px;top:${y}px;width:${d}px;height:${d}px"><img id="${iid}" src="${img}" alt="" style="object-position:50% 0%"></div>`;
}

function stringsHTML(sc) {
  const b = LAY[sc.lay]?.strings;
  if (!b) return "";
  const n = 21; // les 21 cordes de la kora
  const ids = [];
  let h = `<div class="strings" style="${box(b)}">`;
  for (let i = 0; i < n; i++) {
    const id = nid("st");
    ids.push(id);
    h += `<i id="${id}" style="left:${((i + 0.5) * 100 / n).toFixed(2)}%"></i>`;
  }
  h += "</div>";
  let k = Math.floor(rr(0, n));
  for (const bt of BEATS) {
    const t = map(bt);
    if (t === null || t < sc.os || t > sc.oe - 0.2) continue;
    k = (k + 5 + Math.floor(rr(0, 9))) % n;
    fromTo("#" + ids[k], { opacity: 0.5, scaleX: 2 }, { opacity: 0.1, scaleX: 1, duration: 0.9, ease: "power2.out" }, t);
  }
  return h;
}

function confettiHTML(sc) {
  if (!sc.confetti) return "";
  const cols = ["#E3B34C", "#F3D58A", "#F7F1E3", "#3D5BE0", "#E3B34C"];
  let h = `<div class="confetti">`;
  const span = sc.oe - sc.os;
  for (let i = 0; i < sc.confetti; i++) {
    const id = nid("cf");
    const w = Math.round(rr(10, 20)), ht = Math.round(rr(14, 30));
    const x = Math.round(rr(0.02, 0.98) * W);
    const dur = rr(3.2, 5.4);
    const t0 = sc.os + 0.2 + rr(0, Math.max(0.5, span - 3.2));
    h += `<i id="${id}" style="left:${x}px;width:${w}px;height:${ht}px;background:${cols[i % cols.length]};border-radius:${i % 3 === 0 ? "50%" : "2px"}"></i>`;
    fromTo("#" + id, { y: -80, x: 0, rotation: rr(0, 180), opacity: 0.95 },
      { y: H + 120, x: rr(-140, 140), rotation: rr(360, 900) * (i % 2 ? 1 : -1), duration: r3(dur), ease: "none" }, t0);
  }
  return h + "</div>";
}

function lineHTML(segs, cls, enterAt) {
  let h = `<p class="${cls}">`;
  for (const w of words(segs)) {
    const id = nid("w");
    h += `<span id="${id}" class="w${w.em ? " em" : ""}">${esc(w.text)}</span> `;
    const t = map(w.t);
    fromTo("#" + id, { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" },
      t === null ? enterAt : Math.max(enterAt, t - 0.08));
  }
  return h + "</p>";
}

function cardsHTML(sc) {
  let h = "";
  const cards = sc.cards.map((cd) => {
    const s = cd.s ?? cd.lines[0][0][1];
    return { ...cd, s };
  }).filter((cd) => {
    const lastT = cd.lines ? cd.lines.at(-1).at(-1)[2] : cd.e;
    return map(cd.s) !== null || map(lastT) !== null;
  });
  cards.forEach((cd, i) => {
    const id = nid("cd");
    const enter = Math.max(sc.os, mapC(cd.s));
    const next = cards[i + 1];
    const exit = Math.min(next ? mapC(next.s) - 0.34 : sc.oe + 0.1, cd.e !== undefined && map(cd.e) !== null ? map(cd.e) : 1e9);
    let inner = "";
    if (cd.cover) {
      inner = `<p class="cv-title">Joyeux anniversaire,${P ? "<br>" : " "}<span class="em">Linda</span></p><p class="cv-sub">Une année de plus de lumière</p><p class="cv-chip"><span>Hambalyo&nbsp;!</span></p>`;
    } else if (cd.custom === "hambalyo") {
      const a = nid("x"), b = nid("x"), d = nid("x");
      inner = `<p id="${a}" class="hb-word">Hambalyo</p><p id="${b}" class="hb-tr">«&nbsp;Félicitations&nbsp;»</p><p id="${d}" class="hb-note">Kora mandingue · Rythmes de Djibouti · Amapiano</p>`;
      fromTo("#" + a, { opacity: 0, y: 50, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "power3.out" }, enter);
      fromTo("#" + b, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }, enter + 1.7);
      fromTo("#" + d, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }, enter + 3.9);
    } else if (cd.custom === "wishes") {
      const rows = [["Farxad", "le bonheur", 85.05], ["Caafimaad", "la santé", 89.36], ["Guul", "la réussite", 93.67]];
      inner = `<div class="wishes">`;
      for (const [so, fr, t] of rows) {
        const a = nid("x");
        inner += `<p id="${a}" class="wish"><span class="em">${so}</span><span class="dash"></span><span class="fr">${fr}</span></p>`;
        fromTo("#" + a, { opacity: 0, x: P ? 0 : -60, y: P ? 40 : 0 }, { opacity: 1, x: 0, y: 0, duration: 0.8, ease: "power3.out" }, map(t) ?? enter);
      }
      const z = nid("x");
      inner += `<p id="${z}" class="wish-end">Hambalyo, Linda&nbsp;!</p></div>`;
      fromTo("#" + z, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, map(97.44) ?? enter);
    } else {
      const multi = cd.lines.length > 1;
      const cls = cd.big ? "ly big" : multi ? "ly cp" : "ly";
      cd.lines.forEach((segs, li) => {
        inner += lineHTML(segs, cls, enter);
        if (cd.gloss?.[li]) {
          const g = nid("g");
          inner += `<p id="${g}" class="gloss">${cd.gloss[li]}</p>`;
          fromTo("#" + g, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out" }, (map(segs[0][1]) ?? enter) + 0.45);
        }
      });
    }
    h += `<div class="card"><div id="${id}" class="card-in">${inner}</div></div>`;
    if (!cd.cover) fromTo("#" + id, { opacity: 0 }, { opacity: 1, duration: 0.01 }, enter - 0.02);
    if (exit < DUR - 0.05) to("#" + id, { opacity: 0, y: -26, duration: 0.3, ease: "power2.in" }, exit);
  });
  return h;
}

const BEATS = JSON.parse(readFileSync(new URL("./beats.json", import.meta.url)));

let scenesHTML = "";
kept.forEach((sc, i) => {
  const sid = "sc-" + sc.id;
  const start = i === 0 ? 0 : sc.os - 0.3;
  const end = i === kept.length - 1 ? DUR : sc.oe + 0.45;
  let inner = "";
  if (sc.lay === "S") {
    const short = DUR - sc.os < 3.5;
    const lg = P ? 760 : 700;
    inner = `<div class="sig"><img id="sig-logo" src="assets/dk_pro_logo.png" alt="Dian K. Pro" style="width:${lg}px;height:${lg}px"><div id="sig-line" class="sig-line"></div></div>`;
    fromTo("#sig-logo", { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: short ? 0.7 : 1.3, ease: "power3.out" }, sc.os + (short ? 0.05 : 0.3));
    fromTo("#sig-line", { scaleX: 0, opacity: 1 }, { scaleX: 1, duration: short ? 0.8 : 1.6, ease: "power2.inOut" }, sc.os + (short ? 0.2 : 0.7));
    if (!short) to("#sig-logo", { scale: 1.035, duration: r3(DUR - sc.os - 1.6), ease: "none" }, sc.os + 1.6);
  } else {
    const lay = LAY[sc.lay];
    const amb = sc.photo === "linda" && !(P && sc.lay === "A") ? `<div class="amb"></div>` : "";
    const eb = nid("eb");
    inner =
      amb + stringsHTML(sc) + confettiHTML(sc) + photoHTML(sc, sid) +
      `<div class="txt ${lay.align}" style="${box(lay.txt)}"><div id="${eb}" class="eyebrow">${ornament}<span>${esc(sc.eyebrow)}</span></div>${cardsHTML(sc)}</div>`;
    if (i > 0) fromTo("#" + eb, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }, sc.os + 0.15);
  }
  scenesHTML += `\n      <div id="${sid}" class="clip scene lay-${sc.lay}" data-start="${r3(start)}" data-duration="${r3(end - start)}" data-track-index="${i + 1}" style="z-index:${i + 1}">${inner}</div>`;
  if (i > 0) fromTo("#" + sid, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.inOut" }, sc.os - 0.3);
});

// lumières (bokeh) — bandes latérales, jamais au centre du cadre
let bokeh = "";
for (let i = 0; i < 16; i++) {
  const id = nid("bk");
  const side = i % 2 ? rr(0.01, 0.2) : rr(0.8, 0.99);
  const d = Math.round(rr(26, 90));
  bokeh += `<i id="${id}" style="left:${Math.round(side * W)}px;width:${d}px;height:${d}px"></i>`;
  const y0 = rr(0.25, 1.1) * H;
  fromTo("#" + id, { y: y0, opacity: rr(0.1, 0.3) }, { y: y0 - rr(0.5, 1.1) * H, opacity: rr(0.25, 0.5), duration: DUR, ease: "none" }, 0);
}

const css = `
@font-face{font-family:"Playfair Display";src:url("fonts/PlayfairDisplay.woff2") format("woff2");font-weight:400 900;font-style:normal;font-display:block}
@font-face{font-family:"Playfair Display";src:url("fonts/PlayfairDisplay-Italic.woff2") format("woff2");font-weight:400 900;font-style:italic;font-display:block}
@font-face{font-family:"Inter";src:url("fonts/Inter-Medium.otf") format("opentype");font-weight:500;font-display:block}
@font-face{font-family:"Inter";src:url("fonts/Inter-SemiBold.otf") format("opentype");font-weight:600;font-display:block}
@font-face{font-family:"Inter";src:url("fonts/Inter-Bold.otf") format("opentype");font-weight:700;font-display:block}
:root{--ink:#0B0B0C;--gold:#E3B34C;--gold2:#F3D58A;--ivory:#F7F1E3;--blue:#3D5BE0}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;overflow:hidden;background:var(--ink)}
#root{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:var(--ink);font-family:"Inter",sans-serif;color:var(--ivory)}
.scene{position:absolute;inset:0;overflow:hidden;background:var(--ink)}
.amb{position:absolute;inset:-4%;background:url("assets/linda-amb.jpg") center/cover;opacity:.55}
.glow{position:absolute;border-radius:50%;background:radial-gradient(closest-side,rgba(227,179,76,.30),rgba(61,91,224,.10) 55%,rgba(11,11,12,0) 100%)}
.ph{position:absolute;overflow:hidden;background:#141416}
.ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.ph-full{inset:0}
.arch{border-radius:${P ? 420 : 374}px ${P ? 420 : 374}px 18px 18px}
.circ{border-radius:50%}
.frame{position:absolute;border:3px solid var(--gold);box-shadow:0 0 60px rgba(227,179,76,.28)}
.shade{position:absolute;inset:0}
.shade-pa{background:linear-gradient(180deg,rgba(11,11,12,.55) 0%,rgba(11,11,12,0) 13%,rgba(11,11,12,0) 47%,rgba(11,11,12,.80) 60%,rgba(11,11,12,.93) 74%,rgba(11,11,12,.97) 100%)}
.shade-k{background:${P
    ? "linear-gradient(180deg,rgba(11,11,12,.45) 0%,rgba(11,11,12,0) 14%,rgba(11,11,12,0) 42%,rgba(11,11,12,.82) 57%,rgba(11,11,12,.94) 74%,rgba(11,11,12,.97) 100%)"
    : "linear-gradient(90deg,rgba(11,11,12,1) 0%,rgba(11,11,12,.96) 30%,rgba(11,11,12,.6) 50%,rgba(11,11,12,0) 68%)"}}
.strings{position:absolute}
.strings i{position:absolute;top:0;bottom:0;width:2px;background:linear-gradient(180deg,rgba(227,179,76,0),var(--gold) 18%,var(--gold2) 50%,var(--gold) 82%,rgba(227,179,76,0));opacity:.1}
.confetti{position:absolute;inset:0}
.confetti i{position:absolute;top:0;display:block}
.txt{position:absolute}
.txt.center{text-align:center}
.eyebrow{position:absolute;left:0;right:0;top:0;display:flex;flex-direction:column;gap:18px;align-items:${P ? "center" : "flex-start"};font-weight:700;font-size:${LAY.eyebrow}px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
.txt.center .eyebrow{align-items:center}
.card{position:absolute;left:0;right:0;top:${P ? 86 : 96}px;bottom:0;display:flex;flex-direction:column;justify-content:center}
.card-in{display:flex;flex-direction:column;gap:${P ? 14 : 18}px}
.ly{font-family:"Playfair Display",serif;font-weight:700;font-size:${LAY.lyric}px;line-height:1.14;letter-spacing:-.01em;color:var(--ivory);text-shadow:0 3px 26px rgba(0,0,0,.6)}
.ly.cp{font-size:${LAY.couplet}px}
.ly.big{font-size:${LAY.big}px;line-height:1.06}
.w{display:inline-block}
.em{font-style:italic;color:var(--gold);font-weight:700}
.gloss{font-weight:500;font-size:${LAY.gloss}px;color:var(--ivory);margin-top:-6px;margin-bottom:10px;text-shadow:0 2px 16px rgba(0,0,0,.7)}
.cv-title{font-family:"Playfair Display",serif;font-weight:800;font-size:${P ? 88 : 126}px;line-height:1.04;letter-spacing:-.015em;color:var(--ivory);text-shadow:0 4px 30px rgba(0,0,0,.6)}
.cv-sub{font-family:"Playfair Display",serif;font-style:italic;font-weight:500;font-size:${P ? 52 : 56}px;color:var(--gold2);margin-top:${P ? 12 : 18}px;text-shadow:0 3px 20px rgba(0,0,0,.6)}
.cv-chip{margin-top:${P ? 22 : 30}px}
.cv-chip span{display:inline-block;padding:14px 36px;border:2px solid var(--gold);border-radius:999px;font-weight:700;font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold2);background:rgba(11,11,12,.5)}
.hb-word{font-family:"Playfair Display",serif;font-style:italic;font-weight:800;font-size:${P ? 168 : 176}px;line-height:1;color:var(--gold);text-shadow:0 4px 40px rgba(0,0,0,.65)}
.hb-tr{font-family:"Playfair Display",serif;font-weight:600;font-size:${P ? 68 : 76}px;color:var(--ivory);text-shadow:0 3px 24px rgba(0,0,0,.65)}
.hb-note{font-weight:600;font-size:${P ? 30 : 32}px;letter-spacing:.02em;white-space:nowrap;color:var(--gold2);margin-top:${P ? 18 : 26}px;text-shadow:0 2px 16px rgba(0,0,0,.7)}
.wishes{display:flex;flex-direction:column;gap:${P ? 14 : 30}px}
.wish{display:flex;align-items:baseline;gap:26px;justify-content:${P ? "center" : "flex-start"};font-family:"Playfair Display",serif}
.wish .em{font-size:${P ? 82 : 100}px;font-weight:800;line-height:1.05}
.wish .dash{width:${P ? 50 : 70}px;height:3px;background:var(--gold);align-self:center;flex:none}
.wish .fr{font-size:${P ? 50 : 58}px;font-weight:500;color:var(--ivory)}
.wish-end{font-weight:700;font-size:${P ? 34 : 36}px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold2);margin-top:${P ? 14 : 22}px}
.wish,.wish-end{text-shadow:0 3px 22px rgba(0,0,0,.65)}
.lay-S{background:#000}
.sig{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.sig img{display:block}
.sig-line{width:${P ? 520 : 620}px;height:3px;margin-top:-30px;background:linear-gradient(90deg,rgba(227,179,76,0),var(--gold),rgba(227,179,76,0))}
#bokeh{position:absolute;inset:0;z-index:40;pointer-events:none}
#bokeh i{position:absolute;top:0;border-radius:50%;background:radial-gradient(closest-side,rgba(243,213,138,.9),rgba(227,179,76,.35) 45%,rgba(227,179,76,0) 100%)}
`;

const html = `<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${W}, height=${H}" />
    <title>Linda — Une année de plus de lumière (${variant})</title>
    <script src="vendor/gsap.min.js"></script>
    <style>${css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${DUR}" data-width="${W}" data-height="${H}">${scenesHTML}
      <div id="bokeh" class="clip" data-start="0" data-duration="${DUR}" data-track-index="20">${bokeh}</div>
      <audio id="music" src="${V.audio}" data-start="0" data-duration="${DUR}" data-track-index="30" data-volume="1"${V.fadeOut ? ` data-fade-out="${V.fadeOut}"` : ""}></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      const ANIMS = ${JSON.stringify(A)};
      for (const [sel, from, to, at] of ANIMS) {
        if (from) tl.fromTo(sel, from, to, at);
        else tl.to(sel, to, at);
      }
      tl.to({}, { duration: 0.001 }, ${DUR} - 0.001);
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
`;
writeFileSync(new URL("./index.html", import.meta.url), html);
console.log(`${variant}: ${W}x${H}, ${DUR}s, ${kept.length} scènes, ${A.length} animations`);
