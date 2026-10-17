const MODULE_M4 = {
  id: "m4", num: 4,
  titre: "Évaluation critique",
  sousTitre: "Repérer les hallucinations, les erreurs de calcul et les biais avant qu'ils n'atteignent un décideur.",
  competence: "critique",
  lecons: [
    {
      id: "m4-hallucinations", titre: "Hallucinations : pourquoi l'IA invente", duree: 4,
      contenu: `<p>On appelle <strong>hallucination</strong> une affirmation fausse présentée avec assurance. Elle n'est ni un mensonge ni un bug rare : c'est la conséquence directe du fonctionnement de l'IA, qui produit le texte le plus plausible, pas le plus vrai.</p>
<h4>Où elles se cachent</h4>
<ul>
<li>Les chiffres précis : couvertures, effectifs, budgets, taux.</li>
<li>Les références : auteurs, titres, revues, années, identifiants DOI.</li>
<li>Les noms propres, les dates, les intitulés et numéros de lois.</li>
<li>Les citations entre guillemets attribuées à une personne ou à une institution.</li>
</ul>
<h4>Les signaux d'alerte</h4>
<ul>
<li>Une précision excessive (un taux à la décimale près, sans source).</li>
<li>Une référence parfaitement formatée que vous ne retrouvez nulle part.</li>
<li>Une réponse qui confirme exactement ce que vous espériez.</li>
</ul>
<h4>Ce qui protège vraiment</h4>
<ul>
<li>Fournir vos sources et exiger que l'IA s'y limite.</li>
<li>Demander de distinguer ce qui vient de vos documents, de ses connaissances générales, ou d'une hypothèse.</li>
<li>Vérifier dans une source primaire. Demander à l'IA « es-tu sûr ? » ne suffit pas : elle peut confirmer une erreur avec la même assurance.</li>
</ul>
<div class="encadre"><strong>La grille VÉRIF</strong>, appliquée à chaque mission : <strong>V</strong>éracité des faits et références, <strong>É</strong>quité, <strong>R</strong>aisonnement, <strong>I</strong>ntégrité des données, <strong>F</strong>aisabilité des recommandations.</div>`,
      retenir: [
        "L'hallucination découle du fonctionnement de l'IA : elle reste possible même avec un bon prompt.",
        "Chiffres, références, lois et citations sont les zones à vérifier en priorité.",
        "Seule une source primaire confirme un fait ; l'IA ne peut pas s'auto-certifier."
      ]
    },
    {
      id: "m4-references", titre: "Références fantômes et synthèse de littérature", duree: 4,
      contenu: `<p>Demandez à un assistant « cinq études sur l'hésitation vaccinale en Afrique de l'Ouest » : vous obtiendrez une liste élégante. Une partie peut ne pas exister, ou exister sans dire ce qui lui est attribué.</p>
<h4>Le rituel de vérification</h4>
<ol>
<li>Recherchez chaque référence dans PubMed, Google Scholar, ou la bibliothèque institutionnelle de l'OMS (IRIS).</li>
<li>Si un DOI est fourni, ouvrez-le : il doit mener au bon article.</li>
<li>Lisez au minimum le résumé : l'article dit-il vraiment ce que l'IA affirme ?</li>
<li>Vérifiez le pays, l'année et la population étudiés avant toute généralisation.</li>
</ol>
<h4>Une méthode plus sûre pour synthétiser</h4>
<ul>
<li>Constituez vous-même le corpus (articles, rapports) et fournissez-le à l'IA.</li>
<li>Demandez un tableau d'extraction : référence, pays, population, méthode, résultat principal, limites.</li>
<li>Exigez que chaque affirmation de la synthèse renvoie à une ligne du tableau.</li>
<li>Refusez toute « méta-analyse » produite de mémoire.</li>
</ul>
<p>Les outils ancrés dans des sources (NotebookLM, Elicit, Consensus, Perplexity) réduisent nettement le risque de références inventées. Ils ne l'éliminent pas : un article réel peut être mal résumé, ou une phrase attribuée à la mauvaise source.</p>
<div class="encadre"><strong>Règle de diffusion.</strong> Aucune référence produite par l'IA ne figure dans un document diffusé sans avoir été ouverte et lue par un humain.</div>`,
      retenir: [
        "Une référence bien formatée n'est pas une preuve d'existence.",
        "Synthétisez à partir d'un corpus que vous avez constitué, via un tableau d'extraction.",
        "Les outils ancrés réduisent le risque mais n'exemptent pas de la lecture des sources."
      ]
    },
    {
      id: "m4-chiffres", titre: "Chiffres, dénominateurs et calculs", duree: 5,
      contenu: `<p>En vaccination, la plupart des erreurs graves ne viennent pas d'un chiffre inventé mais d'un <strong>mauvais dénominateur</strong> ou d'une <strong>formule mal appliquée</strong>. L'IA reproduit ces erreurs avec aplomb.</p>
<h4>Les formules à connaître</h4>
<table>
<thead><tr><th>Indicateur</th><th>Formule</th></tr></thead>
<tbody>
<tr><td>Couverture vaccinale</td><td>Doses administrées / population cible × 100</td></tr>
<tr><td>Taux d'abandon Penta1–Penta3</td><td>(Penta1 − Penta3) / Penta1 × 100</td></tr>
<tr><td>Enfants zéro-dose (estimation administrative)</td><td>Population cible − enfants ayant reçu Penta1</td></tr>
<tr><td>Complétude des rapports</td><td>Rapports reçus / rapports attendus × 100</td></tr>
</tbody>
</table>
<h4>Les pièges classiques</h4>
<ul>
<li><strong>Couverture supérieure à 100 %</strong> : le plus souvent un dénominateur sous-estimé (projections de recensement anciennes) ou des enfants venus d'autres zones.</li>
<li><strong>Abandon négatif</strong> : rattrapage, erreurs de saisie ou problème de rapportage.</li>
<li><strong>Périodes mélangées</strong> : numérateur annuel, dénominateur semestriel.</li>
<li><strong>Pourcentages de pourcentages</strong> : une baisse de 80 % à 70 % est une baisse de 10 points, soit 12,5 % en relatif.</li>
</ul>
<h4>Avec l'IA</h4>
<ul>
<li>Demandez l'outil d'analyse de données et l'affichage des formules utilisées.</li>
<li>Refaites vous-même le calcul pour deux ou trois lignes.</li>
<li>Triangulez : données administratives, enquêtes (EDS, MICS) et estimations OMS/UNICEF (WUENIC) racontent souvent des histoires différentes. L'écart est en soi une information.</li>
</ul>
<div class="encadre"><strong>Réflexe.</strong> Devant un chiffre surprenant, cherchez d'abord une explication liée à la donnée (dénominateur, saisie, période) avant une explication programmatique.</div>`,
      retenir: [
        "Le dénominateur est la première source d'erreur en analyse de couverture.",
        "Faites afficher les formules et refaites deux ou trois calculs à la main.",
        "Un écart entre sources administratives et enquêtes est une information à analyser, pas un bruit."
      ]
    },
    {
      id: "m4-biais", titre: "Biais, complaisance et équité", duree: 5,
      contenu: `<p>Une réponse peut être exacte dans le détail et biaisée dans son ensemble. Trois mécanismes sont à surveiller.</p>
<h4>1. Le biais des données d'entraînement</h4>
<p>Les modèles ont surtout lu des textes produits dans des pays à revenu élevé, majoritairement en anglais. Sans contexte, ils proposent des solutions pensées pour d'autres systèmes de santé : rappels par SMS là où la couverture réseau est faible, prise de rendez-vous en ligne, ressources humaines supposées disponibles.</p>
<h4>2. La complaisance</h4>
<p>L'IA tend à aller dans le sens de la question. Si vous écrivez « montre que la stratégie avancée est la plus efficace », elle construira cet argumentaire, même si les données ne le soutiennent pas.</p>
<div class="exemple">Formulation neutre : « Compare l'efficacité et le coût des stratégies fixe, avancée et mobile dans ce contexte, avec les arguments pour et contre chacune et le niveau de preuve disponible. »</div>
<h4>3. Les angles morts d'équité</h4>
<p>Ce qui n'est pas dans les données n'existe pas pour l'IA. Les enfants zéro-dose, les populations nomades, les déplacés internes, les zones d'insécurité, les quartiers urbains pauvres ou les adolescentes non scolarisées disparaissent facilement d'une analyse.</p>
<h4>Quatre questions avant de valider</h4>
<ul>
<li><strong>Qui manque ?</strong> Quels groupes sont absents des données ou des recommandations ?</li>
<li><strong>Qui supporte le coût ?</strong> Les recommandations reportent-elles la charge sur les ménages ou les agents de santé communautaires ?</li>
<li><strong>Qui décide ?</strong> Les communautés concernées ont-elles une voix ?</li>
<li><strong>Qui est désigné ?</strong> Le texte stigmatise-t-il un groupe (« populations réfractaires ») ?</li>
</ul>
<div class="encadre"><strong>Relance utile.</strong> « Quels groupes de population ton analyse risque-t-elle d'oublier, et comment le vérifier dans les données disponibles ? »</div>`,
      retenir: [
        "Sans contexte, l'IA importe des solutions conçues pour d'autres systèmes de santé.",
        "Une question orientée produit une réponse orientée : formulez de façon neutre.",
        "Ce qui est absent des données est absent de l'analyse : cherchez activement qui manque."
      ]
    }
  ],
  exercices: [
    { type: "erreurs", ref: "err-abandon" },
    { type: "erreurs", ref: "err-note-politique" },
    { type: "erreurs", ref: "err-reglementaire" }
  ],
  quiz: [
    { q: "Lequel de ces éléments est un signal d'alerte d'hallucination ?",
      options: ["Une réponse qui indique « je ne sais pas ».", "Une référence parfaitement formatée, avec DOI, introuvable dans PubMed.", "Une réponse courte.", "Une réponse présentée en tableau."],
      bonne: 1, explication: "Une référence introuvable est le signe typique d'une hallucination. Reconnaître une incertitude est au contraire un bon signe." },
    { q: "Un district affiche une couverture Penta3 de 112 %. Quelle est l'interprétation la plus prudente ?",
      options: ["Une performance exceptionnelle à valoriser.", "Une erreur de l'IA, à ignorer.", "Un dénominateur probablement sous-estimé ou des enfants venus d'autres zones : à investiguer.", "Le signe d'une épidémie."],
      bonne: 2, explication: "Une couverture supérieure à 100 % signale presque toujours un problème de dénominateur ou de rapportage." },
    { q: "Quelle est la formule correcte du taux d'abandon Penta1–Penta3 ?",
      options: ["(Penta1 − Penta3) / Penta3 × 100", "(Penta1 − Penta3) / population cible × 100", "Penta3 / Penta1 × 100", "(Penta1 − Penta3) / Penta1 × 100"],
      bonne: 3, explication: "Le dénominateur est Penta1 : on mesure la part des enfants ayant commencé la série qui ne l'ont pas terminée." },
    { q: "Vous écrivez : « Montre que la stratégie avancée est plus efficace que la stratégie fixe. » Quel est le principal risque ?",
      options: ["La complaisance : l'IA construit l'argumentaire demandé, même si les données ne le soutiennent pas.", "Aucun risque particulier.", "L'IA refusera de répondre.", "La réponse sera trop courte."],
      bonne: 0, explication: "Une question orientée produit une réponse orientée. Demandez une comparaison neutre, avec arguments pour et contre." },
    { q: "Que peut-on dire des outils de recherche ancrés dans des sources (NotebookLM, Perplexity, Elicit) ?",
      options: ["Ils éliminent toute erreur de citation.", "Ils réduisent le risque de références inventées, mais une source peut être mal résumée ou mal attribuée.", "Ils sont interdits en santé publique.", "Ils ne citent jamais leurs sources."],
      bonne: 1, explication: "L'ancrage améliore la traçabilité ; la lecture de la source reste nécessaire." },
    { q: "L'IA recommande une stratégie mobile hebdomadaire dans tous les villages d'une région en situation d'insécurité, sans moyens supplémentaires. Quel critère VÉRIF est d'abord en défaut ?",
      options: ["Véracité", "Intégrité des données", "Équité", "Faisabilité"],
      bonne: 3, explication: "La recommandation ignore les contraintes de sécurité et de ressources : elle n'est pas réaliste dans ce contexte." }
  ]
};
