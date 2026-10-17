const MODULE_M1 = {
  id: "m1", num: 1,
  titre: "Comprendre l'IA sans maths",
  sousTitre: "Ce qui se passe réellement quand vous posez une question à une IA, et ce que cela change pour votre travail.",
  competence: "fondamentaux",
  lecons: [
    {
      id: "m1-prediction",
      titre: "Comment un modèle de langage produit une réponse",
      duree: 4,
      contenu: `<p>Claude, ChatGPT, Gemini ou Copilot reposent sur un <strong>grand modèle de langage</strong>. Son principe est simple : à partir du texte qu'il a sous les yeux, il produit la suite <strong>la plus plausible</strong>, morceau par morceau. Imaginez un collègue qui aurait lu une bibliothèque entière et saurait poursuivre presque n'importe quel texte dans le style attendu, mais qui ne consulte jamais de dossier au moment où il parle.</p>
<h4>Un apprentissage sur d'immenses corpus</h4>
<p>Le modèle a été entraîné sur de très grands volumes de textes (pages web, livres, articles, code), puis ajusté pour suivre des instructions et dialoguer. Il en a retenu des régularités : la structure d'une note ministérielle, le vocabulaire du PEV, la manière de formuler une recommandation. Il ne contient pas une base de faits vérifiés qu'il interrogerait : il a appris des associations entre mots et idées.</p>
<h4>Fluidité n'est pas vérité</h4>
<p>Parce qu'il vise le plausible, le modèle peut écrire une phrase impeccable et fausse : un taux de couverture inventé, une référence inexistante, une recommandation de l'OMS déformée. Le ton assuré ne dit rien de la fiabilité. Plus la question est spécifique (un district, une politique nationale récente, un chiffre précis), plus le risque d'erreur augmente.</p>
<h4>Deux propriétés à connaître</h4>
<ul>
<li><strong>La date de coupure des connaissances</strong> : le modèle ignore ce qui s'est passé après la fin de son entraînement (nouveau plan stratégique, changement de calendrier vaccinal, épidémie en cours), sauf s'il dispose d'une recherche web ou si vous lui fournissez les documents.</li>
<li><strong>La variabilité</strong> : la génération comporte une part d'aléatoire. La même question, posée deux fois, peut donner deux réponses différentes, voire contradictoires. Si deux réponses divergent sur un fait, c'est le signal qu'il faut le vérifier.</li>
</ul>
<h4>Ce que cela implique pour vous</h4>
<p>Confiez à l'IA ce qu'elle fait bien : structurer, reformuler, résumer un document que vous fournissez, proposer des pistes, préparer le premier jet d'une note. Ne lui confiez pas le rôle de source. Dans une analyse de district ou une note au ministre, chaque chiffre, référence ou norme citée doit pouvoir être rattaché à une source que vous savez nommer : DHIS2, WUENIC, document de l'OMS, rapport d'enquête.</p>
<div class="encadre"><strong>Attention</strong> — Demander à l'IA « Es-tu sûr de toi ? » ne vérifie rien : elle produit une réponse plausible à cette nouvelle question, qu'elle confirme ou se rétracte. La vérification se fait toujours contre une source externe.</div>`,
      retenir: [
        "Un modèle de langage produit la suite de texte la plus plausible ; il ne consulte pas une base de faits vérifiés.",
        "Une réponse fluide et assurée peut être fausse : chaque chiffre et chaque référence se vérifie contre une source que vous savez nommer.",
        "Le modèle ignore ce qui est postérieur à sa date de coupure et peut répondre différemment à la même question."
      ]
    },
    {
      id: "m1-contexte",
      titre: "Contexte, mémoire et documents fournis",
      duree: 4,
      contenu: `<p>Au cours d'une conversation, l'IA ne travaille qu'avec ce qui figure dans sa <strong>fenêtre de contexte</strong> : vos messages, ses propres réponses, les documents joints et les éventuelles instructions de l'outil. C'est son plan de travail. Ce qui n'y figure pas, elle ne le voit pas ; elle comble alors les vides avec du plausible.</p>
<h4>Fournir ses documents change tout</h4>
<div class="exemple"><strong>Sans ancrage</strong> : « Analyse la couverture Penta3 dans la région de l'Est. »<br><strong>Avec ancrage</strong> : « Voici le tableau DHIS2 agrégé des 8 districts de la région et le rapport de supervision du trimestre. Analyse-les et indique, pour chaque constat, la ligne ou le passage d'où il provient. »</div>
<p>Dans le premier cas, l'IA improvise à partir de connaissances générales, avec un risque élevé de chiffres inventés. Dans le second, elle est <strong>ancrée</strong> dans vos données : chaque affirmation devient vérifiable. Plan national, rapport de revue, note ministérielle précédente : chaque document pertinent fourni réduit la part d'invention.</p>
<h4>La mémoire entre conversations</h4>
<p>Par défaut, une nouvelle conversation repart de zéro. Certains outils proposent une mémoire persistante ou des <strong>projets</strong>, espaces où l'on dépose documents et consignes réutilisés à chaque échange. Ces fonctions varient selon les outils, les abonnements et les paramètres de votre institution : vérifiez ce qui est activé, ce qui est conservé et qui y a accès.</p>
<h4>Les limites</h4>
<ul>
<li><strong>Documents très longs</strong> : la fenêtre est grande mais finie ; au-delà, une partie du texte peut être tronquée ou résumée sans avertissement.</li>
<li><strong>Le milieu est moins bien exploité</strong> : dans un long dossier, le début et la fin sont souvent mieux pris en compte que le milieu ; une annexe clé peut passer inaperçue.</li>
<li><strong>Longues conversations</strong> : après de nombreux échanges, les consignes initiales sont parfois moins bien respectées.</li>
</ul>
<h4>Bonnes pratiques</h4>
<ul>
<li>Fournissez les documents sources plutôt que de compter sur la culture générale de l'IA.</li>
<li>Pour un rapport volumineux, travaillez section par section et désignez précisément les chapitres à analyser.</li>
<li>Exigez la citation du passage source pour chaque affirmation importante.</li>
<li>Quand la conversation s'allonge, ouvrez-en une nouvelle avec un récapitulatif des consignes et des acquis.</li>
</ul>
<div class="encadre"><strong>Attention</strong> — Tout document joint est transmis à l'outil et à son fournisseur. Vérifiez son niveau de sensibilité avant de le joindre : une liste nominative (niveau N3) n'a jamais sa place dans un assistant généraliste.</div>`,
      retenir: [
        "L'IA ne travaille qu'avec ce qui figure dans sa fenêtre de contexte : ce qui n'y est pas, elle l'improvise.",
        "Fournir vos propres documents ancre la réponse et la rend vérifiable, passage par passage.",
        "Pour les longs dossiers, découpez, ciblez les sections utiles et repartez d'une conversation neuve si nécessaire ; vérifiez les fonctions de mémoire de votre outil."
      ]
    },
    {
      id: "m1-outils",
      titre: "Assistants, outils intégrés et agents : le panorama",
      duree: 5,
      contenu: `<p>« L'IA » recouvre aujourd'hui des outils très différents. Choisir le bon outil pour la tâche est déjà une décision de qualité et de sécurité.</p>
<h4>Les assistants généralistes</h4>
<p>Claude, ChatGPT ou Gemini sont des assistants conversationnels polyvalents : rédaction, reformulation, synthèse de documents fournis, structuration d'une note, préparation d'un atelier. Leur force est la souplesse ; leur piège, la tentation de les traiter comme une source de faits.</p>
<h4>Les assistants intégrés à la suite bureautique</h4>
<p>Microsoft Copilot pour Microsoft 365 fonctionne dans Word, Excel, Outlook ou Teams. Selon la configuration et vos droits d'accès, il peut consulter les fichiers, courriels et réunions de votre organisation. C'est un atout (retrouver la dernière version du plan de riposte, résumer un long fil de courriels) et une responsabilité : il peut faire remonter un document que vous ignoriez avoir à disposition. Dans beaucoup d'institutions, c'est l'outil autorisé pour les documents internes.</p>
<h4>Les outils ancrés dans des sources</h4>
<ul>
<li><strong>NotebookLM</strong> répond à partir des documents que vous y déposez et renvoie aux passages : adapté pour interroger un corpus de rapports de revue du PEV.</li>
<li><strong>Perplexity</strong> effectue une recherche web et cite ses sources : utile pour un premier repérage, à condition d'ouvrir les sources.</li>
<li><strong>Elicit</strong> et <strong>Consensus</strong> interrogent la littérature scientifique : utiles pour démarrer une revue, jamais pour la remplacer.</li>
</ul>
<p>Une source citée n'est pas une source vérifiée : l'outil peut la résumer mal ou lui faire dire plus qu'elle ne dit.</p>
<h4>Fonctions spécialisées et agents</h4>
<p>Beaucoup d'assistants disposent d'une <strong>fonction d'analyse de données</strong> qui exécute du code pour calculer : plus fiable que le calcul « de tête » du modèle, mais à contrôler. La <strong>recherche web</strong> donne accès à des informations postérieures à la date de coupure. Les <strong>agents</strong> enchaînent plusieurs actions (chercher, ouvrir, remplir, envoyer) avec une autonomie croissante : gardez une validation humaine à chaque étape qui engage votre institution.</p>
<h4>Quel outil pour quelle tâche ?</h4>
<table><thead><tr><th>Tâche</th><th>Type d'outil adapté</th></tr></thead><tbody>
<tr><td>Premier jet d'une note ministérielle</td><td>Assistant généraliste, ou Copilot pour les documents internes</td></tr>
<tr><td>Taux d'abandon par district</td><td>Assistant avec analyse de données, sur données agrégées</td></tr>
<tr><td>Questions sur vingt rapports de revue</td><td>Outil ancré dans vos documents</td></tr>
<tr><td>Repérage de littérature</td><td>Outil de recherche documentaire, puis lecture des articles</td></tr>
</tbody></table>
<div class="encadre"><strong>Attention</strong> — Les fonctionnalités évoluent très vite et varient selon les abonnements. Avant tout usage professionnel, vérifiez la politique de votre institution : outils autorisés, types de données admis, conditions de conservation.</div>`,
      retenir: [
        "Assistants généralistes, outils bureautiques intégrés, outils ancrés dans des sources et agents répondent à des besoins différents.",
        "Copilot pour Microsoft 365 peut accéder aux fichiers et courriels de l'organisation selon vos droits : c'est un atout et une responsabilité.",
        "Les fonctionnalités changent vite : vérifiez la politique de votre institution avant tout usage professionnel."
      ]
    }
  ],
  quiz: [
    {
      q: "Un assistant IA vous donne, dans une réponse fluide et assurée, un taux national précis de couverture Penta3. Que pouvez-vous en conclure ?",
      options: [
        "Le chiffre est fiable, car le modèle a été entraîné sur les rapports de l'OMS et de l'UNICEF.",
        "Rien sur sa justesse : le modèle produit un texte plausible, le chiffre doit être vérifié dans une source nommée.",
        "Le chiffre est fiable s'il est donné avec une décimale, signe d'un calcul précis.",
        "Le chiffre est fiable si l'IA le maintient quand on lui demande « Es-tu sûr ? »."
      ],
      bonne: 1,
      explication: "Un modèle de langage génère la suite la plus plausible, pas un fait vérifié. Seule une source comme WUENIC ou DHIS2 permet de confirmer un chiffre."
    },
    {
      q: "Vous posez deux fois la même question sur l'année d'introduction d'un vaccin dans un pays et obtenez deux réponses différentes. Quelle interprétation est la bonne ?",
      options: [
        "L'outil est défectueux et doit être signalé au service informatique.",
        "La seconde réponse est la bonne, car l'IA s'est corrigée entre-temps.",
        "La première réponse est la bonne, car c'est la plus spontanée.",
        "La génération comporte une part d'aléatoire : la divergence signale un fait à vérifier dans une source fiable."
      ],
      bonne: 3,
      explication: "La variabilité des réponses est normale. Quand deux réponses divergent sur un fait, aucune n'est garantie : vérifiez auprès du programme national ou de l'OMS."
    },
    {
      q: "Pour obtenir une analyse fiable de la couverture vaccinale de votre région, quelle approche est la plus efficace ?",
      options: [
        "Fournir le tableau agrégé DHIS2 et le rapport de supervision, puis demander une analyse qui indique la source de chaque constat.",
        "Demander à l'IA de s'appuyer sur ses connaissances de la région, puisqu'elle a lu de nombreux rapports.",
        "Poser une question très courte pour ne pas encombrer la fenêtre de contexte.",
        "Préciser que l'analyse est destinée au ministre, pour que l'IA soit plus rigoureuse."
      ],
      bonne: 0,
      explication: "Fournir vos propres données ancre la réponse : l'IA travaille sur vos chiffres et vous pouvez vérifier chaque affirmation. Sans documents, elle improvise."
    },
    {
      q: "Vous avez joint un rapport de revue du PEV de 180 pages. La synthèse produite ignore les recommandations d'une annexe située au milieu du document. Quelle est l'explication la plus probable ?",
      options: [
        "L'annexe ne contenait rien d'important, sinon l'IA l'aurait relevée.",
        "L'IA a délibérément écarté l'annexe pour rester concise.",
        "Dans les longs documents, le milieu est souvent moins bien pris en compte : il faut désigner explicitement la section à analyser.",
        "Les assistants IA ne lisent jamais les annexes."
      ],
      bonne: 2,
      explication: "La prise en compte d'un long document n'est pas uniforme. Travaillez par sections et désignez les passages à analyser."
    },
    {
      q: "Quelle affirmation sur Microsoft Copilot pour Microsoft 365 est exacte ?",
      options: [
        "Il fonctionne comme un assistant isolé et n'a accès à aucun fichier de l'organisation.",
        "Selon la configuration et vos droits d'accès, il peut consulter les fichiers, courriels et réunions de votre organisation.",
        "Il peut consulter tous les documents de l'organisation, y compris ceux auxquels vous n'avez pas accès.",
        "Fourni par l'institution, il dispense de vérifier quels types de données peuvent lui être confiés."
      ],
      bonne: 1,
      explication: "Copilot pour Microsoft 365 s'appuie sur vos droits existants : il peut faire remonter tout ce à quoi vous avez accès. La politique institutionnelle sur les données continue de s'appliquer."
    },
    {
      q: "Vous devez répondre à des questions précises à partir d'un corpus de vingt rapports de revue du PEV, avec renvoi aux passages. Quel type d'outil convient le mieux ?",
      options: [
        "Un outil ancré dans vos documents, comme NotebookLM, qui répond à partir du corpus déposé et renvoie aux passages.",
        "Un assistant généraliste interrogé sans les documents, puisqu'il connaît déjà les revues du PEV.",
        "Un agent autonome chargé de chercher sur le web et d'envoyer directement la synthèse au comité.",
        "Un moteur de recherche web avec citations, car il trouvera des sources plus récentes que vos rapports."
      ],
      bonne: 0,
      explication: "Un outil ancré dans vos sources limite l'invention et facilite la vérification. Les renvois restent à contrôler : une source citée n'est pas une source vérifiée."
    }
  ]
};
