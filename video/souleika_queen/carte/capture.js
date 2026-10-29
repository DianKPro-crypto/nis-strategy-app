// Contrôle visuel de la carte (work/carte_site) dans un navigateur de téléphone simulé :
//  - image d'aperçu WhatsApp (media/apercu.jpg, 1200 × 630) ;
//  - captures iPhone et Android de chaque étape (work/carte_qa/) ;
//  - synchronisation : instant du son quand chaque mot s'affiche, comparé à work/carte_voix/mots.json ;
//  - vidéo de démonstration du parcours complet, avec la voix de la lettre (work/carte_qa/demo.mp4).
// Usage : node carte/capture.js            (tout)
//         node carte/capture.js --apercu   (image d'aperçu WhatsApp seulement)
//         node carte/capture.js --demo     (aperçu et démonstration seulement)
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const SITE = path.resolve(__dirname, "..", "work", "carte_site");
const QA = path.resolve(__dirname, "..", "work", "carte_qa");
const TOKEN = "dk3110";
const TYPES = { ".html": "text/html; charset=utf-8", ".jpg": "image/jpeg", ".png": "image/png", ".woff": "font/woff",
                ".mp3": "audio/mpeg", ".mp4": "video/mp4", ".txt": "text/plain" };

function serveur() {
  return http.createServer((req, res) => {
    const url = decodeURIComponent(req.url.split("?")[0]);
    const f = path.join(SITE, url.endsWith("/") ? url + "index.html" : url);
    if (!f.startsWith(SITE) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
    const size = fs.statSync(f).size, type = TYPES[path.extname(f)] || "application/octet-stream";
    const range = req.headers.range && /bytes=(\d*)-(\d*)/.exec(req.headers.range);
    if (range) {
      const a = range[1] ? +range[1] : 0, b = range[2] ? +range[2] : size - 1;
      res.writeHead(206, { "Content-Type": type, "Content-Range": `bytes ${a}-${b}/${size}`, "Accept-Ranges": "bytes", "Content-Length": b - a + 1 });
      if (req.method === "HEAD") return res.end();
      return fs.createReadStream(f, { start: a, end: b }).pipe(res);
    }
    res.writeHead(200, { "Content-Type": type, "Content-Length": size, "Accept-Ranges": "bytes" });
    if (req.method === "HEAD") return res.end();
    fs.createReadStream(f).pipe(res);
  });
}

const attendre = (ms) => new Promise((r) => setTimeout(r, ms));
// instants des mots dits (carte/voix.py) ; sans voix, la lettre suit le rythme posé (environ 44 s)
const MOTS_JSON = path.resolve(__dirname, "..", "work", "carte_voix", "mots.json");
const VOIX = fs.existsSync(path.join(SITE, "media", "lettre.mp3")) && fs.existsSync(MOTS_JSON) ? JSON.parse(fs.readFileSync(MOTS_JSON)).mots : null;
const LECTURE = +(process.env.LECTURE_MS || (VOIX ? Math.round((VOIX[VOIX.length - 1] + 3) * 1000) : 47000));
const MAGIE = ["souleika.", "étoiles,", "lanternes", "d'artifice", "jeclahay.", "karim."];     // mots qui déclenchent un effet

(async () => {
  fs.mkdirSync(QA, { recursive: true });
  const srv = serveur().listen(0);
  const base = `http://127.0.0.1:${srv.address().port}`;
  const browser = await chromium.launch();

  // 1. aperçu WhatsApp
  {
    const p = await browser.newPage({ viewport: { width: 1200, height: 630 } });
    await p.goto(`${base}/apercu.html`); await p.evaluate(() => document.fonts.ready); await attendre(300);
    await p.screenshot({ path: path.join(SITE, "media", "apercu.jpg"), type: "jpeg", quality: 88 });
    await p.close();
  }

  if (process.argv.includes("--apercu")) { await browser.close(); srv.close(); return; }   // image d'aperçu seulement

  // 2. captures iPhone et Android
  // « iphone_safari » : hauteur réellement visible avec les barres de Safari ou de WhatsApp
  const appareils = [["iphone", { width: 390, height: 844 }, 3], ["iphone_safari", { width: 390, height: 664 }, 3],
                     ["android", { width: 412, height: 915 }, 2.625]];
  const demo = process.argv.includes("--demo");
  for (const [nom, viewport, dpr] of demo ? [] : appareils) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: dpr, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    const erreurs = [];
    p.on("pageerror", (e) => erreurs.push(String(e)));
    await p.goto(`${base}/?apercu=${TOKEN}&horloge=2026-10-30T12:34:56Z`);
    await p.evaluate(() => document.fonts.ready); await attendre(1500);
    await p.screenshot({ path: path.join(QA, `${nom}_1_compte_a_rebours.png`) });
    await p.tap("#sceau"); await attendre(900);
    await p.screenshot({ path: path.join(QA, `${nom}_2_patience.png`) });
    await p.goto(`${base}/?apercu=${TOKEN}`); await attendre(1200);
    await p.screenshot({ path: path.join(QA, `${nom}_3_pret.png`) });
    await p.tap("#sceau"); await attendre(LECTURE);       // fin de la lettre : le bouton du film apparaît
    await p.screenshot({ path: path.join(QA, `${nom}_9_film_appel.png`) });
    await p.tap("#voir-film"); await attendre(1200);
    await p.screenshot({ path: path.join(QA, `${nom}_10_film.png`) });
    await p.tap("#fermer"); await attendre(1500);
    await p.screenshot({ path: path.join(QA, `${nom}_11_fin.png`) });
    console.log(nom, erreurs.length ? "ERREURS : " + erreurs.join(" | ") : "aucune erreur JavaScript");
    await ctx.close();
  }

  // 3. étapes intermédiaires (iPhone) : ouverture, puis chaque mot magique ; journal de synchronisation
  if (!demo) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    await p.goto(`${base}/?apercu=${TOKEN}`); await attendre(1200);
    const textes = await p.evaluate(() => {
      window.journal = [];                       // instant du son quand chaque mot apparaît
      const son = document.getElementById("lettre");
      new MutationObserver((ms) => { for (const m of ms) {
        const el = m.target;
        if (!el.vu && (el.classList.contains("mot") && el.classList.contains("dit") || el.dataset.mot && el.classList.contains("visible"))) {
          el.vu = true; window.journal.push({ t: son.currentTime, joue: !son.paused && son.currentTime > 0 });
        }
      } }).observe(document.body, { attributes: true, attributeFilter: ["class"], subtree: true });
      return [...document.querySelectorAll("[data-lire], [data-mot]")]
        .flatMap((el) => el.dataset.mot ? [el.dataset.mot] : [...el.querySelectorAll(".mot")].map((s) => s.textContent));
    });
    const instants = VOIX || [];
    const etapes = [[0.7, "a_sceau_brise"], [1.6, "b_rabat"], [2.3, "c_lettre"]];
    textes.forEach((w, i) => { if (MAGIE.includes(w.toLowerCase()) && instants[i] !== undefined) etapes.push([instants[i] + 0.7, `mot_${String(i).padStart(2, "0")}`]); });
    await p.tap("#sceau");
    const t0 = Date.now();
    for (const [s, etiquette] of etapes) {
      await attendre(Math.max(0, s * 1000 - (Date.now() - t0)));
      await p.screenshot({ path: path.join(QA, `iphone_etape_${etiquette}.png`) });
    }
    await attendre(Math.max(0, LECTURE - (Date.now() - t0)));
    const journal = await p.evaluate(() => window.journal);
    if (VOIX) {
      const ecarts = journal.map((j, i) => j.t - VOIX[i]);
      const joues = journal.filter((j) => j.joue).length;
      console.log(`synchronisation : ${journal.length}/${VOIX.length} mots affichés, ${joues} pendant que la voix joue ; ` +
                  `écart affichage − mot dit : min ${Math.min(...ecarts).toFixed(3)} s, max ${Math.max(...ecarts).toFixed(3)} s`);
    }
    await ctx.close();
  }

  // 4. démonstration filmée : compte à rebours, minuit, sceau, lettre, film, fin.
  // Images de l'écran horodatées (Chromium sans écran les livre en 1× ; l'enregistreur vidéo de Playwright, lui,
  // les pose dans un cadre gris), agrandies ×2, puis voix de la lettre calée sur le premier mot : work/carte_qa/demo.mp4
  {
    const IMG = path.join(QA, "demo_images");
    fs.rmSync(IMG, { recursive: true, force: true }); fs.mkdirSync(IMG);
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    const cdp = await ctx.newCDPSession(p);
    const images = [];                          // [fichier, heure de l'image en s]
    cdp.on("Page.screencastFrame", ({ data, metadata, sessionId }) => {
      const f = path.join(IMG, `${String(images.length).padStart(5, "0")}.jpg`);
      fs.writeFileSync(f, Buffer.from(data, "base64")); images.push([f, metadata.timestamp]);
      cdp.send("Page.screencastFrameAck", { sessionId }).catch(() => {});
    });
    await p.goto(`${base}/?apercu=${TOKEN}&horloge=2026-10-30T20:59:54Z`);
    await p.evaluate(() => {                    // heure d'apparition du premier mot (pour caler le son)
      new MutationObserver((ms, obs) => { if (ms.some((m) => m.target.classList.contains("dit"))) { window.premier = Date.now(); obs.disconnect(); } })
        .observe(document.body, { attributes: true, attributeFilter: ["class"], subtree: true });
    });
    await cdp.send("Page.startScreencast", { format: "jpeg", quality: 92 });
    await attendre(7600);                       // le compte à rebours atteint minuit, le sceau s'illumine
    const toucher = Date.now() / 1000;
    await p.tap("#sceau");
    await attendre(LECTURE + 1500);             // la lettre lue mot à mot
    const premier = await p.evaluate(() => window.premier) / 1000;
    const film = Date.now() / 1000;
    await p.tap("#voir-film"); await attendre(2500);
    await p.tap("#fermer"); await attendre(4500);
    await cdp.send("Page.stopScreencast");
    await ctx.close();
    const t0 = images[0][1], duree = images[images.length - 1][1] - t0 + 0.04;
    const liste = images.map(([f, t], i) => `file '${f}'\nduration ${((i + 1 < images.length ? images[i + 1][1] : t + 0.04) - t).toFixed(4)}`);
    fs.writeFileSync(path.join(QA, "demo_images.txt"), liste.join("\n") + `\nfile '${images[images.length - 1][0]}'\n`);
    const v = { toucher: toucher - t0, premier: premier - t0, film: film - t0, duree };
    fs.writeFileSync(path.join(QA, "demo.json"), JSON.stringify(v, null, 1));
    const image = "fps=30,scale=780:-2:flags=lanczos,unsharp=5:5:0.5,format=yuv420p";
    const sortie = ["-c:v", "libx264", "-preset", "medium", "-crf", "22", "-movflags", "+faststart", path.join(QA, "demo.mp4")];
    if (VOIX) {                                 // la voix commence au premier mot moins son instant ; elle s'efface quand le film s'ouvre
      const d = Math.round((v.premier - VOIX[0]) * 1000);
      execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(QA, "demo_images.txt"),
        "-i", path.join(SITE, "media", "lettre.mp3"), "-filter_complex",
        `[0:v]${image}[v];[1:a]adelay=${d}|${d},afade=t=out:st=${v.film.toFixed(3)}:d=0.7,apad,atrim=0:${duree.toFixed(3)}[a]`,
        "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "128k", ...sortie]);
    } else {
      execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(QA, "demo_images.txt"), "-vf", image, ...sortie]);
    }
    fs.rmSync(IMG, { recursive: true, force: true });     // quelques milliers d'images : seule la vidéo est gardée
    console.log(`démonstration : ${images.length} images en ${duree.toFixed(1)} s ; toucher du sceau à ${v.toucher.toFixed(2)} s, ` +
                `premier mot à ${v.premier.toFixed(2)} s, film à ${v.film.toFixed(2)} s → work/carte_qa/demo.mp4`);
  }
  await browser.close(); srv.close();
})();
