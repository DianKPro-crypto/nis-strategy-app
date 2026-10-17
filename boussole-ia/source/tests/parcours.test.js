// Test de bout en bout de Boussole IA (fichier autonome) avec Playwright.
// Usage : node source/tests/parcours.test.js [chemin du fichier HTML]
// Les captures d'écran sont enregistrées dans build/captures/.
const path = require('path');
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright')); }
const FICHIER = 'file://' + path.resolve(process.argv[2] || path.join(__dirname, '..', '..', 'boussole-ia.html'));
const SHOTS = path.resolve(__dirname, '..', '..', 'build', 'captures');
fs.mkdirSync(SHOTS, { recursive: true });

const erreurs = [];
const ok = (cond, msg) => { if (!cond) { erreurs.push('ÉCHEC : ' + msg); console.log('✗', msg); } else console.log('✓', msg); };

(async () => {
  const browser = await chromium.launch().catch(() => chromium.launch({ executablePath: process.env.CHROMIUM_PATH }));
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 900 }, colorScheme: 'dark', permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await ctx.newPage();
  page.on('pageerror', e => erreurs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.googleapis|ERR_|net::/.test(m.text())) erreurs.push('console: ' + m.text()); });

  await page.goto(FICHIER);
  await page.waitForSelector('.hero');
  ok(await page.title() === 'Boussole IA', 'titre de la page');
  await page.screenshot({ path: SHOTS + '/01-accueil-desktop.png', fullPage: true });

  // --- Mission complète ---
  await page.click('.porte-principale');
  await page.waitForSelector('.tache');
  ok(await page.locator('.tache').count() === 15, '15 tâches proposées');
  await page.fill('#rech-mission', 'abandon');
  ok(await page.locator('.tache').count() >= 1, 'recherche de tâche');
  await page.fill('#rech-mission', '');
  await page.click('[data-a="choisirTache"][data-id="pev-abandon"]');
  await page.waitForSelector('.ck-grille');
  const rep = { niveau: 'N1', identifiant: 0, petits: 0, droit: 0, outil: 'institutionnel', entrainement: 0, decision: 1, vulnerables: 0, contexte: 0, relecture: 0, transparence: 0, chiffres: 0 };
  for (const [q, v] of Object.entries(rep)) await page.click(`[data-a="ck"][data-q="${q}"][data-v="${v}"]`);
  ok(await page.locator('.verdict.v-attention').count() === 1, 'verdict orange attendu');
  await page.screenshot({ path: SHOTS + '/02-proteger.png', fullPage: true });
  // Feu rouge bloque
  await page.click('[data-a="ck"][data-q="identifiant"][data-v="2"]');
  ok(await page.locator('[data-a="versProduire"]').isDisabled(), 'feu rouge bloque la suite');
  await page.click('[data-a="ck"][data-q="identifiant"][data-v="0"]');
  await page.selectOption('[data-ch="pays"]', 'SN');
  ok((await page.locator('.pays-encart').innerText()).includes('Sénégal'), 'encart pays Sénégal');
  await page.click('[data-a="versProduire"]');
  await page.waitForSelector('#apercu');
  ok(await page.locator('#apercu mark.vide').count() > 0, 'champs vides signalés');
  await page.fill('#champ-zone', 'Région test');
  ok((await page.locator('#apercu').innerText()).includes('Région test'), 'aperçu mis à jour en direct');
  ok(await page.evaluate(() => document.activeElement && document.activeElement.id) === 'champ-zone', 'focus conservé pendant la saisie');
  await page.click('[data-a="toutExemple"]');
  ok(await page.locator('#apercu mark.vide').count() === 0, 'tous les champs remplis');
  await page.click('[data-a="copierPrompt"]');
  await page.waitForTimeout(300);
  const clip = await page.evaluate(() => navigator.clipboard.readText().catch(() => ''));
  ok(clip.includes('Région test') && clip.includes('Penta1'), 'prompt copié dans le presse-papiers');
  await page.screenshot({ path: SHOTS + '/03-produire.png', fullPage: true });
  await page.click('[data-a="versVerifier"]');
  ok(await page.locator('[data-a="enregistrerMission"]').isDisabled(), 'enregistrement bloqué tant que VÉRIF incomplet');
  for (const l of ['V', 'É', 'R', 'I', 'F']) await page.click(`[data-a="verif"][data-l="${l}"][data-v="${l === 'I' ? 'attention' : 'ok'}"]`);
  ok(await page.locator('.bandeau').count() >= 1, 'conseil de correction affiché');
  await page.click('[data-a="controle"][data-i="0"]');
  await page.click('[data-a="utilise"][data-v="corrige"]');
  await page.selectOption('#gain', '120');
  await page.fill('#note', 'Préciser le dénominateur dans le prompt.');
  await page.screenshot({ path: SHOTS + '/04-verifier.png', fullPage: true });
  await page.click('[data-a="enregistrerMission"]');
  await page.waitForSelector('.lecon');
  ok((await page.locator('.suivant').innerText()).toLowerCase().includes('mission enregistrée'), 'mission enregistrée');
  await page.click('[data-a="luMission"]');
  ok(await page.locator('text=Leçon lue').count() === 1, 'leçon liée marquée lue');
  await page.screenshot({ path: SHOTS + '/05-apprendre.png', fullPage: true });

  // --- Parcours : leçons et quiz du module 0 ---
  await page.click('.nav [data-r="parcours"]');
  ok(await page.locator('.module').count() === 7, '7 modules');
  await page.screenshot({ path: SHOTS + '/06-parcours.png', fullPage: true });
  await page.click('[data-a="ouvrirModule"][data-m="m0"]');
  await page.click('[data-a="ouvrirLecon"][data-id="m0-quoi"]');
  for (let i = 0; i < 3; i++) await page.click('[data-a="lu"]');
  ok(await page.locator('.lecons .lue').count() === 3, '3 leçons du module 0 lues');
  await page.click('[data-a="ouvrirQuiz"][data-m="m0"]');
  const bonnes = await page.evaluate(() => MODULE_M0.quiz.map(q => q.bonne));
  for (let i = 0; i < bonnes.length; i++) await page.click(`[data-a="rep"][data-q="${i}"][data-o="${bonnes[i]}"]`);
  ok((await page.locator('.score').innerText()).includes('Réussi'), 'quiz module 0 réussi');
  await page.screenshot({ path: SHOTS + '/07-quiz.png', fullPage: true });

  // --- Exercice « Trouvez l'erreur » ---
  await page.click('.nav [data-r="parcours"]');
  await page.click('[data-a="ouvrirModule"][data-m="m4"]');
  await page.click('[data-a="ouvrirEx"][data-id="err-abandon"]');
  const idx = await page.evaluate(() => ERREURS[0].segments.map((s, i) => s.err ? i : -1).filter(i => i >= 0));
  for (const i of idx) await page.click(`[data-a="seg"][data-i="${i}"]`);
  await page.screenshot({ path: SHOTS + '/08-erreurs-avant.png', fullPage: true });
  await page.click('[data-a="verifierEx"]');
  ok((await page.locator('.score').innerText()).includes(idx.length + ' / ' + idx.length), 'toutes les erreurs trouvées');
  await page.screenshot({ path: SHOTS + '/09-erreurs-apres.png', fullPage: true });

  // --- Réécriture ---
  await page.click('.nav [data-r="parcours"]');
  await page.click('[data-a="ouvrirModule"][data-m="m0"]');
  await page.click('[data-a="ouvrirEx"][data-id="ex-m0-reecriture"]');
  await page.fill('#reec', 'Tu es épidémiologiste. Rédige une synthèse du rapport ci-dessous. N\'invente rien. Format : 3 messages clés.');
  ok(await page.locator('#detection .puce.ok').count() === 5, 'détection CADRE complète');
  await page.click('[data-a="revelerReec"]');
  ok(await page.locator('pre.prompt').count() === 1, 'proposition révélée');

  // --- Bibliothèque ---
  await page.click('.nav [data-r="prompts"]');
  ok(await page.locator('.carte-prompt').count() === 15, '15 fiches');
  await page.click('[data-a="filtrePrompts"][data-f="communication"]');
  ok(await page.locator('.carte-prompt').count() === 5, 'filtre communication');
  await page.click('[data-a="filtrePrompts"][data-f="tous"]');
  await page.click('[data-a="favori"][data-id="dec-premortem"]');
  await page.click('[data-a="ouvrirPrompt"][data-id="dec-premortem"]');
  await page.waitForSelector('.fiche');
  await page.screenshot({ path: SHOTS + '/10-fiche.png', fullPage: true });
  await page.click('[data-a="fermerPrompt"]');
  await page.click('[data-a="filtrePrompts"][data-f="favoris"]');
  ok(await page.locator('.carte-prompt').count() === 1, 'favori enregistré');

  // --- Éthique ---
  await page.click('.nav [data-r="ethique"]');
  for (const [q, v] of Object.entries(Object.assign({}, rep, { niveau: 'N3', outil: 'gratuit' }))) await page.click(`[data-a="ck"][data-q="${q}"][data-v="${v}"]`);
  ok(await page.locator('.verdict.v-bloquant').count() === 1, 'N3 + compte gratuit = feu rouge');
  await page.click('[data-a="enregistrerVerif"]');
  await page.click('[data-a="ongletEthique"][data-o="matrice"]');
  await page.screenshot({ path: SHOTS + '/11-matrice.png', fullPage: true });
  await page.click('[data-a="ongletEthique"][data-o="pays"]');
  ok(await page.locator('#lignes-pays tr').count() === 54, '54 pays');
  await page.fill('[data-in="rechPays"]', 'Nigeria');
  ok(await page.locator('#lignes-pays tr').count() >= 1, 'recherche pays');
  await page.fill('[data-in="rechPays"]', '');
  await page.screenshot({ path: SHOTS + '/12-pays.png' });
  await page.click('[data-a="ongletEthique"][data-o="cadres"]');
  await page.screenshot({ path: SHOTS + '/13-cadres.png', fullPage: true });

  // --- Progression, export, persistance ---
  await page.click('.nav [data-r="progression"]');
  ok((await page.locator('.journal').innerText()).includes('Penta1'), 'mission au journal');
  await page.click('[data-a="exporter"]');
  const exp = await page.locator('#export-texte').inputValue();
  ok(JSON.parse(exp).missions.length === 1, 'export JSON valide');
  await page.screenshot({ path: SHOTS + '/14-progression.png', fullPage: true });
  await page.goto('about:blank');
  await page.goto(FICHIER);
  await page.waitForSelector('.hero');
  ok((await page.locator('.chiffre').first().innerText()).startsWith('1'), 'progression conservée après rechargement');
  // Import dans un contexte neuf
  const ctx2 = await browser.newContext({ viewport: { width: 1360, height: 900 } });
  const p2 = await ctx2.newPage();
  p2.on('pageerror', e => erreurs.push('pageerror(p2): ' + e.message));
  await p2.goto(FICHIER + '#progression');
  await p2.fill('#import-texte', exp);
  await p2.click('[data-a="importer"]');
  await p2.click('[data-a="confirmerImport"]');
  ok((await p2.locator('.journal').innerText()).includes('Penta1'), 'import sur un autre appareil');
  await p2.fill('#import-texte', 'pas du json');
  await p2.click('[data-a="importer"]');
  ok(await p2.locator('.bandeau').count() >= 1, 'import invalide refusé proprement');
  await page.click('.nav [data-r="memo"]');
  await page.screenshot({ path: SHOTS + '/15-memo.png', fullPage: true });

  // --- Mobile, thème clair ---
  const mob = await browser.newContext({ viewport: { width: 390, height: 844 }, colorScheme: 'light', isMobile: true, hasTouch: true });
  const pm = await mob.newPage();
  pm.on('pageerror', e => erreurs.push('pageerror(mobile): ' + e.message));
  await pm.goto(FICHIER);
  await pm.waitForSelector('.hero');
  for (const r of ['accueil', 'mission', 'prompts', 'parcours', 'ethique', 'progression', 'memo']) {
    await pm.evaluate(r => { location.hash = r; }, r);
    await pm.waitForTimeout(150);
    const debord = await pm.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    ok(debord <= 0, 'mobile sans défilement horizontal : ' + r + ' (' + debord + ')');
    await pm.screenshot({ path: SHOTS + `/m-${r}.png`, fullPage: r === 'accueil' });
  }
  await pm.evaluate(() => { location.hash = 'mission'; });
  await pm.click('[data-a="choisirTache"][data-id="com-note-ministre"]');
  await pm.screenshot({ path: SHOTS + '/m-mission-proteger.png' });
  await pm.evaluate(() => { location.hash = 'ethique'; });
  await pm.click('[data-a="ongletEthique"][data-o="pays"]');
  ok(await pm.evaluate(() => document.documentElement.scrollWidth - window.innerWidth) <= 0, 'mobile : tableau pays contenu');

  await browser.close();
  console.log('\n' + (erreurs.length ? erreurs.join('\n') : 'AUCUNE ERREUR'));
  process.exit(erreurs.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
