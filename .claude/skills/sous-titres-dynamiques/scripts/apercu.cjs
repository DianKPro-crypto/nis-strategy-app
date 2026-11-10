#!/usr/bin/env node
// Aperçu hors HyperFrames — assemble index.html et ses sous-compositions dans Chromium (Playwright),
// avance image par image avec GSAP et encode en MP4 (ffmpeg). Sert à vérifier les sous-titres quand
// le CLI HyperFrames n'est pas disponible. Ce n'est PAS le rendu de livraison : pas de fitTextFontSize,
// pas de traitement média, un seul <audio> pris en compte. Livrer avec « npx hyperframes render ».
//
//   NODE_PATH=$(npm root -g) node apercu.cjs <projet> <sortie.mp4> --gsap <gsap.min.js> [--fps 30]
//   NODE_PATH=$(npm root -g) node apercu.cjs <projet> <prefixe.png> --gsap <gsap.min.js> --at 0,4.5,12
//
// GSAP sans rien installer : npm pack gsap@3.12.5 && tar -xzf gsap-3.12.5.tgz  →  package/dist/gsap.min.js
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path"), { spawn } = require("child_process");

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf("--" + k); return i > -1 ? args[i + 1] : d; };
const [projArg, outArg] = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));
if (!projArg || !outArg || !opt("gsap")) {
  console.error("Usage : node apercu.cjs <projet> <sortie.mp4|prefixe.png> --gsap <gsap.min.js> [--at t1,t2] [--fps 30]");
  process.exit(1);
}
const proj = path.resolve(projArg), out = path.resolve(outArg), gsapFile = path.resolve(opt("gsap"));
const fps = Number(opt("fps", 30));
const at = opt("at") ? opt("at").split(",").map(Number) : null;
if (!fs.existsSync(gsapFile)) { console.error("GSAP introuvable : " + gsapFile); process.exit(1); }

const idx = fs.readFileSync(path.join(proj, "index.html"), "utf8");
const attr = (tag, a) => (tag.match(new RegExp(a + '="([^"]*)"')) || [])[1];
const rootTag = idx.match(/<div[^>]*id="root"[^>]*>/)[0];
const W = +attr(rootTag, "data-width"), H = +attr(rootTag, "data-height"), D = +attr(rootTag, "data-duration");
const hosts = [...idx.matchAll(/<div[^>]*data-composition-src="[^"]+"[^>]*>/g)].map((m) => ({
  id: attr(m[0], "id"), src: attr(m[0], "data-composition-src"), start: +attr(m[0], "data-start"),
  dur: +attr(m[0], "data-duration"), z: (m[0].match(/z-index:\s*(\d+)/) || [])[1] || 0,
}));
const audioTag = (idx.match(/<audio[^>]*>/) || [])[0];
const audio = audioTag ? { src: path.join(proj, attr(audioTag, "src")), start: +(attr(audioTag, "data-start") || 0) } : null;

let body = "";
for (const h of hosts) {
  const inner = fs.readFileSync(path.join(proj, h.src), "utf8").match(/<template>([\s\S]*)<\/template>/)[1];
  const scripts = [...inner.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]).join("\n");
  body += `<div class="host" id="host-${h.id}" data-start="${h.start}" data-dur="${h.dur}" style="position:absolute;inset:0;z-index:${h.z};display:none">${inner.replace(/<script>[\s\S]*?<\/script>/g, "")}</div>\n<script>${scripts}<\/script>\n`;
}
const page = `<!doctype html><html><head><meta charset="utf-8"><base href="file://${proj}/">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=Playfair+Display:ital,wght@0,700;1,700&display=block" rel="stylesheet">
<style>html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:#000;position:relative}</style>
<script src="file://${gsapFile}"></script><script>window.__timelines={};</script></head><body>${body}<script>
window.__warns=[];var ow=console.warn;console.warn=function(){window.__warns.push([].join.call(arguments," "));ow.apply(console,arguments);};
window.__seek=function(t){document.querySelectorAll(".host").forEach(function(h){var s=+h.dataset.start,d=+h.dataset.dur,on=t>=s&&t<s+d;h.style.display=on?"block":"none";if(!on)return;var lt=t-s,tl=window.__timelines[h.id.slice(5)];if(tl)tl.seek(lt);h.querySelectorAll(".clip").forEach(function(c){var cs=+c.dataset.start,cd=+c.dataset.duration;c.style.visibility=(lt>=cs&&lt<cs+cd)?"":"hidden";});});};
</script></body></html>`;
const pageFile = path.join(proj, ".apercu.html");
fs.writeFileSync(pageFile, page);

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  await p.goto("file://" + pageFile, { waitUntil: "networkidle" });
  await p.evaluate(() => document.fonts.ready);
  const info = await p.evaluate(() => ({ timelines: Object.keys(window.__timelines), alertes: window.__warns }));
  const missing = hosts.filter((h) => !info.timelines.includes(h.id)).map((h) => h.id);
  console.log(`Timelines : ${info.timelines.join(", ")}${missing.length ? ` — MANQUANTES : ${missing.join(", ")}` : ""}`);
  if (info.alertes.length) console.log("⚠ " + info.alertes.join("\n⚠ "));
  if (errors.length) console.log("✖ " + errors.join("\n✖ "));
  if (at) {
    for (const t of at) {
      await p.evaluate((t) => window.__seek(t), t);
      const f = out.replace(/\.\w+$/, "") + `-${t}s.png`;
      await p.screenshot({ path: f });
      console.log("✔ " + f);
    }
    await b.close();
    return;
  }
  const ffArgs = ["-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-"];
  if (audio && fs.existsSync(audio.src)) ffArgs.push("-itsoffset", String(audio.start), "-i", audio.src);
  else ffArgs.push("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo");
  ffArgs.push("-t", String(D), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out);
  const ff = spawn("ffmpeg", ffArgs, { stdio: ["pipe", "inherit", "inherit"] });
  const n = Math.round(D * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate((t) => window.__seek(t), i / fps);
    const buf = await p.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  await b.close();
  console.log(`✔ ${out} — ${n} images, ${D} s${audio ? ", audio : " + path.basename(audio.src) : ", sans audio"}`);
})();
