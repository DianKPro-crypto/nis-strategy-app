// Validateur de contenu Boussole IA. Usage : node validate.js src/fichier.js
const fs = require('fs');
const vm = require('vm');
const file = process.argv[2];
const code = fs.readFileSync(file, 'utf8');
const errors = [];
if (code.includes('${')) errors.push('La séquence ${ est interdite.');
if (/<\/script/i.test(code)) errors.push('La séquence </script est interdite.');
let ctx;
try {
  ctx = vm.runInNewContext(code + `
;({
  PROMPTS: typeof PROMPTS !== 'undefined' ? PROMPTS : undefined,
  ERREURS: typeof ERREURS !== 'undefined' ? ERREURS : undefined,
  MODULES: Object.fromEntries(['MODULE_M0','MODULE_M1','MODULE_M2','MODULE_M3','MODULE_M4','MODULE_M5','MODULE_M6']
    .filter(n => { try { return eval('typeof ' + n) !== 'undefined'; } catch (e) { return false; } })
    .map(n => [n, eval(n)]))
})`);
} catch (e) {
  console.error('Erreur de syntaxe ou d\'exécution :', e.message);
  process.exit(1);
}
const LECONS = ['m0-quoi','m0-regles','m0-premier','m1-prediction','m1-contexte','m1-outils','m2-cadre','m2-iterer','m2-avance','m2-outils','m4-hallucinations','m4-references','m4-chiffres','m4-biais','m5-donnees','m5-aiact','m5-equite'];
const need = (o, k, where) => { if (o[k] === undefined || o[k] === null || o[k] === '') errors.push(`${where} : champ manquant « ${k} »`); };
if (ctx.PROMPTS) {
  const ids = new Set();
  ctx.PROMPTS.forEach((p, i) => {
    const w = `PROMPTS[${i}] ${p.id || ''}`;
    ['id','domaine','titre','resume','niveau','donnees','gain','champs','modele','cadre','adapter','pieges','verif','outils','lecon'].forEach(k => need(p, k, w));
    if (ids.has(p.id)) errors.push(`${w} : id dupliqué`); ids.add(p.id);
    if (!['donnees','decision','communication'].includes(p.domaine)) errors.push(`${w} : domaine invalide`);
    if (!['Essentiel','Intermédiaire','Avancé'].includes(p.niveau)) errors.push(`${w} : niveau invalide`);
    if (!['N0','N1','N2','N3'].includes(p.donnees)) errors.push(`${w} : donnees invalide`);
    if (!LECONS.includes(p.lecon)) errors.push(`${w} : lecon inconnue ${p.lecon}`);
    ['C','A','D','R','E'].forEach(k => p.cadre && need(p.cadre, k, w + ' cadre'));
    (p.champs || []).forEach(c => {
      ['id','label','exemple','type'].forEach(k => need(c, k, `${w} champ ${c.id}`));
      if (!['texte','zone'].includes(c.type)) errors.push(`${w} champ ${c.id} : type invalide`);
      if (p.modele && !p.modele.includes('{{' + c.id + '}}')) errors.push(`${w} : {{${c.id}}} absent du modèle`);
    });
    const used = [...(p.modele || '').matchAll(/\{\{(\w+)\}\}/g)].map(m => m[1]);
    used.forEach(u => { if (!(p.champs || []).some(c => c.id === u)) errors.push(`${w} : {{${u}}} sans champ`); });
    ['adapter','pieges','verif'].forEach(k => { if (!Array.isArray(p[k]) || p[k].length < 2) errors.push(`${w} : ${k} doit contenir au moins 2 éléments`); });
  });
  console.log(`${ctx.PROMPTS.length} prompts`);
}
if (ctx.ERREURS) {
  ctx.ERREURS.forEach((e, i) => {
    const w = `ERREURS[${i}] ${e.id || ''}`;
    ['id','titre','domaine','contexte','segments','bilan'].forEach(k => need(e, k, w));
    const errs = (e.segments || []).filter(s => s.err);
    if (errs.length < 3 || errs.length > 4) errors.push(`${w} : ${errs.length} passages piégés (3 à 4 attendus)`);
    errs.forEach(s => { need(s, 'type', w); need(s, 'explication', w); });
  });
  console.log(`${ctx.ERREURS.length} exercices`);
}
Object.entries(ctx.MODULES || {}).forEach(([n, m]) => {
  ['id','num','titre','sousTitre','competence','lecons','quiz'].forEach(k => need(m, k, n));
  (m.lecons || []).forEach(l => {
    ['id','titre','duree','contenu','retenir'].forEach(k => need(l, k, `${n} ${l.id}`));
    if (/style=|<script|href=/i.test(l.contenu || '')) errors.push(`${n} ${l.id} : HTML non autorisé`);
  });
  (m.quiz || []).forEach((q, i) => {
    ['q','options','explication'].forEach(k => need(q, k, `${n} quiz ${i}`));
    if (typeof q.bonne !== 'number' || q.bonne < 0 || q.bonne >= (q.options || []).length) errors.push(`${n} quiz ${i} : index bonne invalide`);
  });
  console.log(`${n} : ${(m.lecons || []).length} leçons, ${(m.quiz || []).length} questions`);
});
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log('OK');
