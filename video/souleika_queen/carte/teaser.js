// Animation « Pour Souleika » à envoyer dans WhatsApp juste avant le lien : WhatsApp la joue en boucle, sans son.
// carte/teaser.html est rendue image par image (instant exact de chaque image : boucle sans raccord), puis encodée :
//   exports/enchante/Souleika_Animation_WhatsApp.mp4   1080 × 1350, 5 s : à envoyer avec l'option « GIF » de WhatsApp
//   exports/enchante/Souleika_Animation_WhatsApp.gif   720 × 900 : vrai GIF, si l'on préfère
// Usage : node carte/teaser.js   (après python3 carte/build.py, qui prépare polices et monogramme dans work/carte_site/media)
const http = require("http");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const RACINE = path.resolve(__dirname, "..");
const MEDIA = path.join(RACINE, "work", "carte_site", "media");
const IMAGES = path.join(RACINE, "work", "carte_teaser");
const SORTIE = path.join(RACINE, "exports", "enchante", "Souleika_Animation_WhatsApp");
const DUREE = 5, IPS = 30;
const TYPES = { ".html": "text/html; charset=utf-8", ".png": "image/png", ".woff": "font/woff" };

const srv = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split("?")[0]);
  const f = url.startsWith("/media/") ? path.join(MEDIA, url.slice(7)) : path.join(__dirname, url);
  if (!fs.existsSync(f) || !fs.statSync(f).isFile()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(res);
}).listen(0);

(async () => {
  fs.rmSync(IMAGES, { recursive: true, force: true }); fs.mkdirSync(IMAGES, { recursive: true });
  const browser = await chromium.launch();
  const p = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  const erreurs = []; p.on("pageerror", (e) => erreurs.push(String(e)));
  await p.goto(`http://127.0.0.1:${srv.address().port}/teaser.html`);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForFunction(() => document.getElementById("dk").complete);
  const n = DUREE * IPS;
  for (let i = 0; i < n; i++) {
    await p.evaluate((t) => window.dessiner(t), i / IPS);
    await p.screenshot({ path: path.join(IMAGES, `${String(i).padStart(4, "0")}.png`) });
  }
  await browser.close(); srv.close();
  if (erreurs.length) throw new Error(erreurs.join(" | "));
  const entree = ["-framerate", String(IPS), "-i", path.join(IMAGES, "%04d.png")];
  execFileSync("ffmpeg", ["-v", "error", "-y", ...entree, "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", `${SORTIE}.mp4`]);
  execFileSync("ffmpeg", ["-v", "error", "-y", ...entree, "-filter_complex",
    "fps=15,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a",
    "-loop", "0", `${SORTIE}.gif`]);
  fs.rmSync(IMAGES, { recursive: true, force: true });
  for (const ext of ["mp4", "gif"]) console.log(`${SORTIE}.${ext} : ${(fs.statSync(`${SORTIE}.${ext}`).size / 1e6).toFixed(2)} Mo`);
})();
