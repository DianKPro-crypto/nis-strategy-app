# Boussole IA · Santé publique — spécification du contenu

Application HTML autonome (hors ligne) pour un stratège international de santé publique
(vaccination/PEV, systèmes de santé, gouvernance, communication stratégique), non développeur,
qui travaille dans toute l'Afrique. Utilisation « juste-à-temps » : il part d'une tâche réelle.
Outils IA utilisés : Claude, ChatGPT, Microsoft Copilot (institutionnel), Gemini/NotebookLM/Perplexity.

Le contenu est écrit en JavaScript (objets littéraux) dans `source/contenu/*.js`, puis injecté dans `boussole-ia.html` par `source/construire.py`.

## Règles d'écriture (obligatoires)

- Français impeccable (accents, apostrophes typographiques ’ ou droites ' acceptées, espaces normales avant « : » « ? » tolérées).
- On s'adresse à l'utilisateur en **vous**. Dans les prompts destinés à l'IA, on tutoie l'IA (**tu**).
- Ton : expert, sobre, précis, orienté action. Pas d'emoji, pas d'enthousiasme creux, pas de jargon inutile.
- Exactitude : n'inventez aucun chiffre, aucune référence, aucun nom de loi. Préférez les principes aux statistiques.
  Si un fait chiffré est indispensable, il doit être solidement établi (OMS/UNICEF, Gavi, IA2030). En cas de doute, ne le mettez pas.
- Toute donnée d'exemple est **fictive** et doit pouvoir être présentée comme telle.
- Contexte africain par défaut (francophone et anglophone), sans condescendance ; mentionner les spécificités
  (insécurité, populations nomades, déplacés, urbains pauvres, genre, langues locales) quand c'est pertinent.
- Chaînes multi-lignes : littéraux gabarits (backticks). **Interdits** dans les chaînes : la séquence `${`, la séquence `</script`.
  Échappez les backticks internes (\`).
- HTML autorisé dans les champs `contenu` des leçons : `p, h4, ul, ol, li, strong, em, br, table, thead, tbody, tr, th, td`,
  `<div class="encadre">…</div>` (encadré « à retenir / attention »), `<div class="exemple">…</div>` (bloc d'exemple, ex. un prompt).
  Aucun attribut style, aucun script, aucun lien externe.

## Identifiants communs

### Domaines (`domaine`)
- `donnees` — Données épidémiologiques & PEV
- `decision` — Aide à la décision stratégique
- `communication` — Communication stratégique

### Niveaux de sensibilité des données (`donnees`)
- `N0` Public : rapports publiés, articles, données WUENIC, communiqués.
- `N1` Interne non sensible : données agrégées non publiées (district ou plus), documents de travail.
- `N2` Confidentiel : budgets non publiés, négociations, données agrégées à très petite échelle (risque de ré-identification), notes politiques sensibles.
- `N3` Personnel : données individuelles de patients ou d'enfants, listes nominatives, données de santé identifiables. Jamais dans un assistant IA généraliste.

### Compétences (`competence`)
`fondamentaux`, `prompt`, `usages`, `critique`, `ethique`

### Identifiants des micro-leçons (pour le champ `lecon` des prompts)
- `m0-quoi` Ce que l'IA générative est, et n'est pas
- `m0-regles` Les 5 règles d'or
- `m0-premier` Votre premier prompt CADRE
- `m1-prediction` Comment un modèle de langage produit une réponse
- `m1-contexte` Contexte, mémoire et documents fournis
- `m1-outils` Assistants, outils intégrés et agents : le panorama
- `m2-cadre` La méthode CADRE en détail
- `m2-iterer` Itérer : la conversation est l'outil
- `m2-avance` Techniques avancées (découpage, exemples, avocat du diable)
- `m2-outils` Adapter son prompt à l'outil
- `m4-hallucinations` Hallucinations : pourquoi l'IA invente
- `m4-references` Références fantômes et synthèse de littérature
- `m4-chiffres` Chiffres, dénominateurs et calculs
- `m4-biais` Biais, complaisance et équité
- `m5-donnees` Protection des données de santé (RGPD, lois africaines)
- `m5-aiact` AI Act et cadres internationaux
- `m5-equite` Équité en santé et IA

### Méthodes maison
- **CADRE** (écrire un prompt) : **C**ontexte · **A**ction · **D**onnées · **R**ègles · **E**xemple de sortie attendue.
- **VÉRIF** (contrôler une réponse) : **V**éracité · **É**quité · **R**aisonnement · **I**ntégrité des données · **F**aisabilité.

## Schéma 1 — Prompt (fichier `source/contenu/prompts.js`, `const PROMPTS = [ … ];`)

```js
{
  id: "pev-abandon",            // slug unique, minuscules, tirets
  domaine: "donnees",           // donnees | decision | communication
  titre: "…",                   // libellé de tâche, verbe à l'infinitif, ≤ 75 caractères
  resume: "…",                  // 1 phrase, ≤ 140 caractères
  niveau: "Intermédiaire",      // Essentiel | Intermédiaire | Avancé
  donnees: "N1",                // niveau de sensibilité typique des données utilisées
  gain: { sans: "3 h", avec: "45 min" },   // estimation indicative et prudente
  champs: [                     // 3 à 6 champs à remplir ; chaque id apparaît dans le modèle sous la forme {{id}}
    { id: "zone", label: "…", exemple: "…", type: "texte" },        // type: texte (une ligne) | zone (multi-lignes)
    { id: "donnees", label: "…", exemple: "…", type: "zone", aide: "…" }  // aide : optionnelle
  ],
  modele: `…{{zone}}…`,         // le prompt complet, structuré CONTEXTE / TÂCHE / DONNÉES / RÈGLES / FORMAT ATTENDU
  cadre: { C: "…", A: "…", D: "…", R: "…", E: "…" },  // pourquoi ça marche : rôle de chaque partie (1 phrase chacune)
  adapter: ["…", "…", "…"],     // 3 façons concrètes d'adapter le prompt
  pieges: ["…", "…", "…"],      // 3 pièges fréquents dans la réponse de l'IA
  verif: ["…", "…", "…"],       // 3 contrôles concrets à faire sur la réponse
  outils: "…",                  // 1 à 2 phrases : quel type d'outil convient, précautions
  lecon: "m4-chiffres"          // id d'une micro-leçon (liste ci-dessus)
}
```

Exigences de qualité des prompts :
- Rôle expert pertinent ; contexte avec les variables ; tâche découpée en étapes numérotées ;
  règles anti-hallucination (n'invente aucun chiffre ni référence, signale les données manquantes, distingue faits / hypothèses) ;
  format de sortie précis (tableau, longueur, public).
- Les exemples de champs doivent être réalistes, africains, fictifs, et utilisables tels quels pour un essai.
- Jamais de champ qui inviterait à coller des données nominatives.

### Exemple complet (à reprendre tel quel comme premier élément de PROMPTS)

```js
{
  id: "pev-abandon",
  domaine: "donnees",
  titre: "Analyser les taux d'abandon Penta1–Penta3 par district",
  resume: "Repérer les districts prioritaires et formuler des hypothèses explicatives à partir d'un tableau agrégé.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "3 h", avec: "45 min" },
  champs: [
    { id: "zone", label: "Zone et niveau d'analyse", exemple: "Région de Ségou (Mali), 8 districts sanitaires", type: "texte" },
    { id: "periode", label: "Période couverte", exemple: "janvier–décembre 2025", type: "texte" },
    { id: "source", label: "Source des données", exemple: "DHIS2, rapports mensuels de vaccination agrégés par district", type: "texte" },
    { id: "donnees", label: "Tableau agrégé (copier-coller)", exemple: "District | Pop. cible 0-11 mois | Penta1 | Penta3\nDistrict A | 12 400 | 11 950 | 10 020\nDistrict B | 9 800 | 7 100 | 6 650\nDistrict C | 15 200 | 14 900 | 12 100", type: "zone", aide: "Uniquement des données agrégées. Jamais de liste nominative." },
    { id: "public", label: "Destinataire de l'analyse", exemple: "Comité technique régional du PEV", type: "texte" }
  ],
  modele: `Tu es épidémiologiste spécialiste des programmes élargis de vaccination (PEV), habitué(e) à analyser les données de routine en Afrique subsaharienne.

CONTEXTE
J'analyse les performances du PEV pour : {{zone}}, sur la période {{periode}}. Source : {{source}}. L'analyse sera présentée à : {{public}}.

TÂCHE
1. Calcule pour chaque district la couverture Penta1 et Penta3 (doses administrées / population cible × 100) et le taux d'abandon Penta1–Penta3 : (Penta1 − Penta3) / Penta1 × 100.
2. Classe chaque district selon la grille accès / utilisation : accès faible si couverture Penta1 < 80 % ; problème d'utilisation si abandon ≥ 10 %.
3. Identifie les 3 districts prioritaires et justifie ton choix.
4. Pour chacun, propose 2 ou 3 hypothèses explicatives à vérifier sur le terrain, présentées clairement comme des hypothèses.

DONNÉES
{{donnees}}

RÈGLES
- Utilise un outil d'analyse ou de calcul si tu en disposes, et montre tes calculs.
- N'invente aucune donnée. Si une valeur manque ou paraît incohérente (abandon négatif, couverture > 100 %), signale-la sans la corriger.
- Signale les limites liées au dénominateur (estimations de population).
- Ne présente aucune corrélation comme une cause.

FORMAT ATTENDU
- Un tableau : District | Couverture Penta1 | Couverture Penta3 | Taux d'abandon | Catégorie.
- 5 messages clés au maximum, rédigés pour : {{public}}.
- Une section « Qualité des données et limites ».`,
  cadre: {
    C: "Le rôle d'épidémiologiste PEV et le contexte (zone, période, source, public) fixent le vocabulaire et le niveau d'exigence.",
    A: "La tâche est découpée en 4 étapes numérotées : l'IA n'en saute aucune et vous pouvez contrôler chacune.",
    D: "Les données sont fournies explicitement : l'IA travaille sur vos chiffres, pas sur des souvenirs approximatifs.",
    R: "Les règles interdisent l'invention et imposent de signaler les incohérences : c'est la principale protection contre les erreurs chiffrées.",
    E: "Le format (tableau, messages clés, limites) rend le résultat directement exploitable et facile à vérifier."
  },
  adapter: [
    "Remplacez Penta1–Penta3 par RR1–RR2 (rougeole) ou BCG–RR1 selon votre question.",
    "Ajoutez une colonne « enfants zéro-dose estimés » (population cible − Penta1) pour un éclairage équité.",
    "Au niveau national, demandez d'abord un regroupement par région, puis le détail des districts des régions prioritaires."
  ],
  pieges: [
    "Une couverture supérieure à 100 % signale le plus souvent un dénominateur sous-estimé, pas une performance exceptionnelle.",
    "Un taux d'abandon négatif révèle un problème de qualité des données (rattrapage, erreurs de saisie, doses hors zone).",
    "L'IA propose volontiers des causes génériques (« manque de sensibilisation ») : exigez des hypothèses vérifiables et spécifiques."
  ],
  verif: [
    "Refaites à la main le calcul de couverture et d'abandon pour 2 districts.",
    "Vérifiez que les seuils (80 %, 10 %) correspondent aux normes de votre programme.",
    "Confrontez les districts prioritaires aux données de supervision et aux enquêtes (EDS, MICS)."
  ],
  outils: "Idéal avec un assistant doté d'une fonction d'analyse de données (ChatGPT, Claude, Copilot dans Excel). Sans cette fonction, vérifiez chaque calcul.",
  lecon: "m4-chiffres"
}
```

## Schéma 2 — Module et leçons (ex. `source/contenu/m1.js`, `const MODULE_M1 = { … };`)

```js
{
  id: "m1", num: 1,
  titre: "Comprendre l'IA sans maths",
  sousTitre: "…",                 // 1 phrase
  competence: "fondamentaux",
  lecons: [
    {
      id: "m1-prediction", titre: "…", duree: 4,        // minutes (3 à 5)
      contenu: `<p>…</p><h4>…</h4><ul><li>…</li></ul><div class="encadre">…</div>`,   // 250 à 450 mots
      retenir: ["…", "…", "…"]                          // 3 points à retenir, 1 phrase chacun
    }
  ],
  quiz: [                          // 6 questions
    { q: "…", options: ["…", "…", "…", "…"], bonne: 1, explication: "…" }   // bonne = index (0-3) ; explication 1-2 phrases
  ]
}
```
Varier la position de la bonne réponse. Distracteurs plausibles (idées reçues courantes).

## Schéma 3 — Exercice « Trouvez l'erreur » (`source/contenu/erreurs.js`, `const ERREURS = [ … ];`)

```js
{
  id: "err-abandon",
  titre: "…",
  domaine: "donnees",             // donnees | decision | communication
  contexte: "…",                  // le prompt (résumé) qui a été donné à l'IA, 1-2 phrases
  segments: [                     // 9 à 14 segments (phrases ou groupes de phrases) qui forment la réponse de l'IA
    { t: "Texte exact du passage." },
    { t: "Passage piégé.", err: true, type: "Calcul erroné", explication: "Pourquoi c'est faux et comment le détecter (1-2 phrases)." },
    { t: "\n" }                   // un segment égal à "\n" force un saut de paragraphe
  ],
  bilan: "…"                      // la leçon à retenir (1-2 phrases)
}
```
- 3 ou 4 passages piégés par exercice, de types variés : `Calcul erroné`, `Mauvais dénominateur`, `Référence inventée`, `Chiffre invérifiable`,
  `Causalité abusive`, `Angle mort d'équité`, `Généralisation hors contexte`, `Affirmation réglementaire fausse`, `Recommandation irréaliste`.
- Les passages corrects doivent être vraiment corrects (sinon l'exercice enseigne une erreur).
- La réponse doit ressembler à une vraie réponse d'IA : fluide, assurée, crédible. Les erreurs doivent être subtiles mais détectables par un professionnel attentif.
- Les données sont fictives (districts « A, B, C » ou noms inventés, jamais de vrais districts avec de faux chiffres).

## Validation

`node source/valider.js source/contenu/<fichier>.js`
doit afficher `OK` sans erreur.
