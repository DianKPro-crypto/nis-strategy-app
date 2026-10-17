const MODULE_M0 = {
  id: "m0", num: 0,
  titre: "Démarrage express",
  sousTitre: "Quinze minutes pour adopter les bons réflexes avant votre prochaine mission.",
  competence: "fondamentaux",
  lecons: [
    {
      id: "m0-quoi", titre: "Ce que l'IA générative est, et n'est pas", duree: 3, competence: "fondamentaux",
      contenu: `<p>Claude, ChatGPT ou Copilot reposent sur des <strong>modèles de langage</strong>. Ils produisent, mot après mot, la suite de texte la plus plausible compte tenu de votre demande et de tout ce qu'ils ont lu pendant leur entraînement. Ils ne consultent pas une base de faits vérifiés : ils rédigent.</p>
<p>Cette nature explique à la fois leur puissance et leurs limites.</p>
<h4>Ce qu'ils font très bien</h4>
<ul>
<li>Structurer une réflexion : plan de note, storyline de présentation, théorie du changement.</li>
<li>Rédiger, reformuler, adapter un texte à un public (ministre, bailleur, relais communautaire).</li>
<li>Résumer et comparer des documents que <em>vous</em> leur fournissez.</li>
<li>Proposer des options, des risques, des contre-arguments.</li>
<li>Exécuter des calculs lorsqu'ils disposent d'un outil d'analyse de données.</li>
</ul>
<h4>Ce qu'ils font mal ou de façon non fiable</h4>
<ul>
<li>Restituer de mémoire des chiffres précis : couvertures, populations, budgets.</li>
<li>Citer des références exactes : ils peuvent inventer un article parfaitement crédible.</li>
<li>Connaître votre contexte : votre district, votre programme, vos contraintes politiques.</li>
<li>Calculer « de tête » sur un long tableau.</li>
<li>Savoir ce qui s'est passé après leur date de fin d'entraînement, sauf recherche web.</li>
</ul>
<div class="encadre"><strong>Le bon modèle mental.</strong> Un collaborateur très rapide et très cultivé, qui n'a jamais travaillé dans votre pays et qui dit rarement « je ne sais pas ». Vous lui donnez le contexte, vous vérifiez son travail, vous signez.</div>`,
      retenir: [
        "L'IA génère un texte plausible ; rien ne garantit qu'il soit vrai.",
        "Elle excelle pour structurer, rédiger et reformuler ; elle est fragile sur les chiffres et les références.",
        "Votre valeur ajoutée tient au contexte que vous fournissez et à la vérification que vous faites."
      ]
    },
    {
      id: "m0-regles", titre: "Les 5 règles d'or", duree: 4, competence: "ethique",
      contenu: `<p>Ces cinq règles couvrent l'essentiel des risques rencontrés en santé publique. Elles structurent chaque mission dans Boussole.</p>
<ol>
<li><strong>Protéger.</strong> Aucune donnée personnelle ou confidentielle dans un outil non approuvé. Anonymisez, agrégez, ou abstenez-vous. Une liste d'enfants perdus de vue avec noms et villages n'a rien à faire dans un assistant grand public.</li>
<li><strong>Contextualiser.</strong> L'IA ne connaît ni votre pays, ni votre programme, ni votre public. Donnez-lui le contexte, les données, le destinataire et les contraintes : c'est la méthode CADRE.</li>
<li><strong>Vérifier.</strong> Tout chiffre, toute référence et toute affirmation réglementaire se vérifient dans une source primaire avant usage : c'est la grille VÉRIF.</li>
<li><strong>Itérer.</strong> La première réponse est un brouillon. Précisez, demandez les hypothèses, faites critiquer, raccourcissez.</li>
<li><strong>Assumer.</strong> L'IA propose, vous décidez. Vous restez responsable du livrable et vous êtes transparent sur l'usage de l'IA auprès de votre commanditaire.</li>
</ol>
<div class="encadre"><strong>Dans le Mode Mission.</strong> L'étape Protéger applique la règle 1. L'étape Produire applique les règles 2 et 4. L'étape Vérifier applique la règle 3. Le journal de mission documente la règle 5.</div>`,
      retenir: [
        "Protéger les données passe avant tout gain de temps.",
        "Contexte fourni et vérification systématique font la différence entre un usage amateur et un usage professionnel.",
        "La responsabilité du livrable ne se délègue pas à l'outil."
      ]
    },
    {
      id: "m0-premier", titre: "Votre premier prompt CADRE", duree: 5, competence: "prompt",
      contenu: `<p>Comparez ces deux demandes adressées au même assistant.</p>
<div class="exemple"><strong>Version spontanée</strong><br>Fais-moi une note sur la vaccination au Niger.</div>
<p>L'IA ne sait ni pour qui, ni pourquoi, ni à partir de quelles données. Elle produira un texte générique, avec des chiffres de mémoire, possiblement dépassés.</p>
<div class="exemple"><strong>Version CADRE</strong><br>
<strong>C</strong> : Tu es conseiller en politiques de santé. Je prépare un entretien de 15 minutes avec le ministre de la Santé.<br>
<strong>A</strong> : Rédige une note d'une page présentant les 3 priorités pour réduire le nombre d'enfants zéro-dose.<br>
<strong>D</strong> : Appuie-toi uniquement sur les éléments suivants : [coller les constats du dernier rapport annuel du programme].<br>
<strong>R</strong> : N'invente aucun chiffre. Si une information manque, écris [À COMPLÉTER]. Ton factuel, sans jargon.<br>
<strong>E</strong> : Titre, 3 messages clés en gras, 3 recommandations numérotées, la décision attendue en une phrase. 300 mots maximum.</div>
<h4>Ce que chaque lettre apporte</h4>
<ul>
<li><strong>Contexte</strong> : le rôle et la situation fixent le niveau de langage et l'angle.</li>
<li><strong>Action</strong> : un verbe précis et un livrable défini.</li>
<li><strong>Données</strong> : l'IA travaille sur vos éléments, pas sur ses souvenirs.</li>
<li><strong>Règles</strong> : la consigne « n'invente aucun chiffre » est votre première protection.</li>
<li><strong>Exemple de sortie</strong> : le format attendu évite trois allers-retours.</li>
</ul>
<div class="encadre"><strong>Le bon calcul.</strong> Trente secondes de plus pour écrire le prompt font gagner une demi-heure de corrections.</div>`,
      retenir: [
        "Un prompt professionnel précise le contexte, l'action, les données, les règles et le format attendu.",
        "La consigne « n'invente aucun chiffre, signale ce qui manque » réduit fortement les erreurs.",
        "Plus le livrable est précis dans le prompt, moins il faut de corrections ensuite."
      ]
    }
  ],
  exercices: [
    {
      type: "reecriture", id: "ex-m0-reecriture", competence: "prompt",
      titre: "Transformer un prompt spontané en prompt CADRE",
      consigne: "Réécrivez la demande ci-dessous en appliquant les 5 lettres de la méthode CADRE. Inventez les éléments de contexte nécessaires : l'objectif est la structure.",
      faible: "Résume ce rapport sur la rougeole.",
      modele: `Tu es épidémiologiste et tu conseilles la direction de la prévention. (C)
Je dois présenter en 5 minutes, au comité de coordination inter-agences, les principaux enseignements du rapport d'investigation ci-dessous sur la flambée de rougeole de 2025 dans la région Nord.

Rédige une synthèse des constats, des causes identifiées par les auteurs et des recommandations. (A)

Appuie-toi uniquement sur le rapport collé entre les balises <rapport> et </rapport>. (D)

Règles : n'ajoute aucune information extérieure au rapport ; si un point important n'est pas documenté, écris « non documenté dans le rapport » ; distingue clairement les constats des recommandations ; ton factuel. (R)

Format : 3 constats clés, 3 recommandations prioritaires avec leur responsable, 1 phrase sur la décision attendue du comité ; 250 mots maximum. (E)

<rapport>
[coller le rapport]
</rapport>`
    }
  ],
  quiz: [
    { q: "Vous demandez à un assistant IA la couverture Penta3 de votre pays en 2024, sans lui fournir de document. Que vaut sa réponse ?",
      options: ["Elle est fiable : l'IA a été entraînée sur les données de l'OMS.", "C'est une estimation plausible, à vérifier dans une source primaire (WUENIC, rapport du programme).", "Elle est fiable si le chiffre est donné avec une décimale.", "Elle est forcément fausse : l'IA ne connaît aucun chiffre."],
      bonne: 1, explication: "L'IA restitue des chiffres plausibles, parfois justes, parfois approximatifs ou dépassés. Une précision apparente ne garantit pas l'exactitude." },
    { q: "Laquelle de ces tâches convient le mieux à un assistant IA ?",
      options: ["Retrouver la référence exacte d'un article sur l'hésitation vaccinale.", "Donner la population cible exacte d'un district.", "Confirmer la date d'entrée en vigueur d'une loi nationale.", "Proposer trois plans possibles pour une note au ministre à partir de vos éléments."],
      bonne: 3, explication: "Structurer et proposer des options à partir de vos éléments est un point fort de l'IA. Références exactes, chiffres précis et textes de loi exigent une vérification à la source." },
    { q: "Quelle est la première règle d'or avant d'utiliser l'IA ?",
      options: ["Protéger : aucune donnée personnelle ou confidentielle dans un outil non approuvé.", "Choisir l'outil le plus récent.", "Écrire le prompt le plus long possible.", "Demander à l'IA si les données peuvent être partagées."],
      bonne: 0, explication: "La protection des données passe en premier. L'IA n'est pas la bonne instance pour décider si un partage de données est autorisé." },
    { q: "Dans la méthode CADRE, à quoi correspond la lettre R ?",
      options: ["Le rôle donné à l'IA.", "Le résumé final.", "Les règles : contraintes, interdits, ton, longueur.", "Les références bibliographiques."],
      bonne: 2, explication: "Le rôle relève du Contexte (C). Les Règles fixent les limites : n'invente aucun chiffre, 300 mots maximum, ton factuel." },
    { q: "L'IA vous livre une note bien rédigée qui sera transmise au ministre. Qui en est responsable ?",
      options: ["L'éditeur de l'outil d'IA.", "Personne : c'est un brouillon automatique.", "L'IA, puisqu'elle l'a rédigée.", "Vous, qui la vérifiez, la signez et la transmettez."],
      bonne: 3, explication: "La responsabilité professionnelle reste entière. L'IA est un outil, comme un tableur ou un correcteur orthographique." }
  ]
};
