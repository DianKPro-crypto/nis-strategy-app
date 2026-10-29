// Contrôle visuel de la carte (work/carte_site) dans un navigateur de téléphone simulé :
//  - image d'aperçu WhatsApp (media/apercu.jpg, 1200 × 630) ;
//  - captures iPhone et Android de chaque étape (work/carte_qa/) ;
//  - vidéo de démonstration du parcours complet (work/carte_qa/demo.webm + instant du toucher sur le sceau).
// Usage : node carte/capture.js            (tout)
//         node carte/capture.js --apercu   (image d'aperçu WhatsApp seulement)
const http = require("http");
const fs = require("fs");
const path = require("path");
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
  const appareils = [["iphone", { width: 390, height: 844 }, 3], ["android", { width: 412, height: 915 }, 2.625]];
  for (const [nom, viewport, dpr] of appareils) {
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
    await p.tap("#sceau"); await attendre(29500);         // fin de la lettre : le bouton du film apparaît
    await p.screenshot({ path: path.join(QA, `${nom}_9_film_appel.png`) });
    await p.tap("#voir-film"); await attendre(1200);
    await p.screenshot({ path: path.join(QA, `${nom}_10_film.png`) });
    await p.tap("#fermer"); await attendre(1500);
    await p.screenshot({ path: path.join(QA, `${nom}_11_fin.png`) });
    console.log(nom, erreurs.length ? "ERREURS : " + erreurs.join(" | ") : "aucune erreur JavaScript");
    await ctx.close();
  }

  // 3. étapes intermédiaires (iPhone) aux instants clés du chant
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    await p.goto(`${base}/?apercu=${TOKEN}`); await attendre(1200);
    await p.tap("#sceau");
    const t0 = Date.now();
    for (const [s, etiquette] of [[0.7, "a_sceau_brise"], [1.6, "b_rabat"], [2.3, "c_lettre"], [3.2, "d_titre_feux"], [12.0, "e_lettre"], [23.0, "f_waan_coeurs"]]) {
      await attendre(Math.max(0, s * 1000 - (Date.now() - t0)));
      await p.screenshot({ path: path.join(QA, `iphone_etape_${etiquette}.png`) });
    }
    await ctx.close();
  }

  // 4. démonstration filmée : compte à rebours, minuit, sceau, lettre, film, fin
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
                                           recordVideo: { dir: QA, size: { width: 780, height: 1688 } } });
    const p = await ctx.newPage();
    const t0 = Date.now();
    await p.goto(`${base}/?apercu=${TOKEN}&horloge=2026-10-30T20:59:54Z`);
    await attendre(8200);                       // le compte à rebours atteint minuit, le sceau s'illumine
    const toucher = (Date.now() - t0) / 1000;
    await p.tap("#sceau");
    await attendre(30500);                      // la lettre au rythme du chant
    await p.tap("#voir-film"); await attendre(2500);
    await p.tap("#fermer"); await attendre(4500);
    const video = p.video();
    await ctx.close();
    fs.renameSync(await video.path(), path.join(QA, "demo.webm"));
    fs.writeFileSync(path.join(QA, "demo.json"), JSON.stringify({ toucher }, null, 1));
    console.log("démonstration : toucher du sceau à", toucher.toFixed(2), "s");
  }
  await browser.close(); srv.close();
})();
