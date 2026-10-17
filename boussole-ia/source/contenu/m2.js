const MODULE_M2 = {
  id: "m2", num: 2,
  titre: "L'art du prompt",
  sousTitre: "Obtenir du premier coup un résultat exploitable, puis l'améliorer en quelques relances.",
  competence: "prompt",
  lecons: [
    {
      id: "m2-cadre", titre: "La méthode CADRE en détail", duree: 5,
      contenu: `<p>Un prompt efficace répond à cinq questions. Les oublier, c'est laisser l'IA deviner, et elle devine avec les références d'autres pays et d'autres publics.</p>
<table>
<thead><tr><th>Lettre</th><th>Question à se poser</th><th>Exemple en santé publique</th></tr></thead>
<tbody>
<tr><td><strong>C</strong>ontexte</td><td>Quel rôle pour l'IA ? Quelle situation ? Pour qui ?</td><td>« Tu es économiste de la santé. Je prépare la revue à mi-parcours du plan pluriannuel, pour le comité de coordination inter-agences. »</td></tr>
<tr><td><strong>A</strong>ction</td><td>Quel livrable précis, avec quel verbe, en combien d'étapes ?</td><td>« 1. Identifie les écarts entre cibles et réalisations. 2. Classe-les par gravité. 3. Propose une mesure corrective par écart. »</td></tr>
<tr><td><strong>D</strong>onnées</td><td>Sur quels documents ou chiffres s'appuyer, et seulement sur ceux-là ?</td><td>« Utilise uniquement le tableau de suivi collé ci-dessous. »</td></tr>
<tr><td><strong>R</strong>ègles</td><td>Quelles limites ? Quels interdits ? Quel ton ?</td><td>« N'invente aucun chiffre. Signale les données manquantes. Ton neutre, sans jugement sur les équipes. »</td></tr>
<tr><td><strong>E</strong>xemple de sortie</td><td>Sous quelle forme, quelle longueur, pour quel lecteur ?</td><td>« Un tableau Écart | Gravité | Mesure | Responsable, puis 5 lignes de synthèse. »</td></tr>
</tbody>
</table>
<h4>Trois erreurs fréquentes</h4>
<ul>
<li><strong>Le rôle sans la situation.</strong> « Tu es un expert » ne suffit pas : précisez pour quoi et pour qui.</li>
<li><strong>Plusieurs tâches mélangées.</strong> Numérotez les étapes ou découpez en plusieurs prompts.</li>
<li><strong>Aucun format.</strong> Sans format, vous recevez une dissertation là où il fallait un tableau.</li>
</ul>
<div class="encadre"><strong>Astuce.</strong> Délimitez clairement vos données, par exemple entre des balises &lt;donnees&gt; et &lt;/donnees&gt;. L'IA distingue alors mieux vos consignes de votre matériau.</div>`,
      retenir: [
        "Chaque lettre de CADRE répond à une question que l'IA ne peut pas deviner.",
        "Numérotez les étapes de la tâche : vous pourrez contrôler chacune.",
        "Le format de sortie est la partie la plus souvent oubliée, et la plus rentable."
      ]
    },
    {
      id: "m2-iterer", titre: "Itérer : la conversation est l'outil", duree: 4,
      contenu: `<p>La première réponse est un brouillon. Les utilisateurs experts obtiennent de meilleurs résultats parce qu'ils relancent avec méthode, pas parce que leur premier prompt est parfait.</p>
<h4>Huit relances à connaître par cœur</h4>
<ol>
<li>« Avant de répondre, pose-moi les questions dont tu as besoin pour bien faire ce travail. »</li>
<li>« Quelles hypothèses as-tu faites ? Lesquelles sont les plus fragiles ? »</li>
<li>« Pour chaque affirmation, indique si elle vient de mes documents, de tes connaissances générales, ou si c'est une hypothèse. »</li>
<li>« Qu'objecterait un bailleur sceptique ? Et un directeur régional de la santé ? »</li>
<li>« Propose 3 options contrastées avec avantages, inconvénients et risques. »</li>
<li>« Raccourcis à 150 mots pour un ministre, conclusion en premier. »</li>
<li>« Réécris en langage simple pour un relais communautaire. »</li>
<li>« Quels groupes de population ton analyse risque-t-elle d'oublier ? »</li>
</ol>
<h4>Quand repartir d'une nouvelle conversation</h4>
<ul>
<li>La conversation dérive et l'IA mélange d'anciennes consignes avec les nouvelles.</li>
<li>Vous changez de sujet ou de pays : l'ancien contexte pollue le nouveau.</li>
<li>La conversation est devenue très longue : les éléments du début sont moins bien pris en compte.</li>
</ul>
<div class="encadre"><strong>Bonne pratique.</strong> Quand une relance a bien fonctionné, intégrez-la directement dans votre prompt de départ la fois suivante. Votre bibliothèque personnelle s'améliore ainsi mission après mission.</div>`,
      retenir: [
        "La qualité vient des relances : hypothèses, sources, objections, options, raccourcissement.",
        "Demander à l'IA de poser ses questions avant de répondre évite les malentendus.",
        "Une conversation trop longue ou qui dérive se recommence, avec un prompt de départ amélioré."
      ]
    },
    {
      id: "m2-avance", titre: "Techniques avancées : découpage, exemples, avocat du diable", duree: 5,
      contenu: `<p>Au-delà de CADRE, quelques techniques changent nettement la qualité des résultats sur les tâches complexes.</p>
<h4>1. Découper la tâche</h4>
<p>Pour une stratégie ou un rapport, demandez d'abord le plan, validez-le, puis faites rédiger section par section. Chaque étape reste contrôlable.</p>
<h4>2. Donner un exemple</h4>
<p>Collez une note réussie de votre organisation et demandez : « Reprends la structure et le ton de cet exemple, avec le contenu suivant. » C'est plus efficace que n'importe quel adjectif.</p>
<h4>3. Ancrer dans vos documents</h4>
<div class="exemple">Réponds uniquement à partir du document fourni. Si une information n'y figure pas, écris « non mentionné dans le document ». Indique la section d'où provient chaque élément.</div>
<h4>4. Faire expliciter le raisonnement</h4>
<p>Demandez les étapes de calcul, les formules utilisées et les hypothèses. Une erreur visible est une erreur que vous pouvez corriger.</p>
<h4>5. L'avocat du diable</h4>
<div class="exemple">Tu es membre du comité d'examen indépendant de Gavi. Relis ce projet de demande de financement avec un regard très critique : relève les hypothèses non étayées, les incohérences budgétaires et les risques non traités, classés par gravité.</div>
<p>Mieux vaut que l'IA trouve les faiblesses avant le comité.</p>
<h4>6. Varier les perspectives</h4>
<p>« Analyse cette décision du point de vue du ministère des Finances, d'un district rural et d'une association de mères. » Les angles morts apparaissent vite.</p>
<div class="encadre"><strong>Attention.</strong> Ces techniques améliorent la qualité ; elles ne suppriment pas les erreurs. La vérification reste indispensable.</div>`,
      retenir: [
        "Plan d'abord, rédaction ensuite : les tâches longues se découpent.",
        "Un exemple concret vaut mieux qu'une longue description du style attendu.",
        "Faire critiquer son propre document par l'IA est l'un des usages les plus rentables."
      ]
    },
    {
      id: "m2-outils", titre: "Adapter son prompt à l'outil", duree: 4,
      contenu: `<p>La méthode CADRE fonctionne avec tous les assistants. Leurs fonctions diffèrent cependant, et changent tous les quelques mois. Retenez les grandes familles plutôt que les détails.</p>
<table>
<thead><tr><th>Outil</th><th>Usages typiques</th><th>Précaution</th></tr></thead>
<tbody>
<tr><td>Claude</td><td>Documents longs, rédaction nuancée, projets qui conservent vos documents de référence, analyse de fichiers.</td><td>Vérifiez les paramètres de confidentialité du compte utilisé.</td></tr>
<tr><td>ChatGPT</td><td>Analyse de données avec exécution de calculs, recherche web, assistants personnalisés.</td><td>Demandez à voir le détail des calculs effectués.</td></tr>
<tr><td>Microsoft 365 Copilot</td><td>Travail dans Word, Excel, PowerPoint, Outlook et Teams ; peut s'appuyer sur les fichiers et courriels de l'organisation, selon vos droits d'accès.</td><td>Vérifiez quels documents il cite ; un document interne peut remonter dans une réponse destinée à un autre public.</td></tr>
<tr><td>Gemini, NotebookLM</td><td>Intégration à Google Workspace ; NotebookLM répond à partir des sources que vous chargez, avec citations.</td><td>Les citations renvoient à vos sources : contrôlez que le passage cité dit bien ce qui est affirmé.</td></tr>
<tr><td>Perplexity, Elicit, Consensus</td><td>Recherche documentaire avec sources.</td><td>Une source réelle peut être mal résumée : lisez au moins le résumé original.</td></tr>
</tbody>
</table>
<h4>Trois réglages qui valent pour tous</h4>
<ul>
<li>Utilisez le compte que votre organisation autorise pour le niveau de sensibilité de vos données.</li>
<li>Désactivez l'utilisation de vos conversations pour l'entraînement lorsque l'option existe.</li>
<li>Pour les calculs, activez ou demandez explicitement l'outil d'analyse de données.</li>
</ul>
<div class="encadre"><strong>À vérifier régulièrement.</strong> Les fonctions et les conditions d'utilisation évoluent vite. La politique d'usage de votre organisation prime sur toute recommandation générale.</div>`,
      retenir: [
        "CADRE est universel ; seules les fonctions annexes changent d'un outil à l'autre.",
        "Copilot institutionnel accède à des documents internes : vérifiez ce qu'il cite.",
        "Le choix de l'outil dépend d'abord de la sensibilité des données et de la politique de votre organisation."
      ]
    }
  ],
  exercices: [
    {
      type: "reecriture", id: "ex-m2-reecriture", competence: "prompt",
      titre: "Réécrire une demande d'analyse de données",
      consigne: "Réécrivez cette demande pour obtenir une analyse exploitable par une équipe cadre de district. Utilisez CADRE et au moins une technique avancée (étapes numérotées, ancrage, demande d'hypothèses).",
      faible: "Analyse ces données de couverture et dis-moi ce que tu en penses.",
      modele: `Tu es épidémiologiste spécialiste du PEV et tu appuies l'équipe cadre du district sanitaire de Kouri (district fictif). (C)
Je prépare la revue trimestrielle des performances avec les 12 responsables d'aires de santé.

1. Calcule pour chaque aire de santé la couverture Penta3 et le taux d'abandon Penta1–Penta3.
2. Identifie les 3 aires les moins performantes et les 3 plus performantes.
3. Propose pour les aires en difficulté 2 hypothèses explicatives chacune, présentées comme des hypothèses à vérifier.
4. Termine par les 3 questions que je devrais poser aux responsables pendant la revue. (A)

Utilise uniquement les données entre les balises <donnees> et </donnees>. (D)

Règles : montre tes calculs ; n'invente aucune valeur ; signale toute donnée manquante ou incohérente (couverture supérieure à 100 %, abandon négatif) ; ne présente aucune corrélation comme une cause ; ton constructif, sans désigner de responsable. (R)

Format : un tableau Aire | Couverture Penta3 | Abandon | Observation, puis les hypothèses et les questions, 400 mots maximum. (E)

<donnees>
[coller le tableau agrégé par aire de santé]
</donnees>`
    }
  ],
  quiz: [
    { q: "Votre prompt est : « Analyse ces données ». Que manque-t-il avant tout ?",
      options: ["Le contexte et le format attendu : pour qui, pourquoi, sous quelle forme.", "Une formule de politesse.", "Le nom de l'outil utilisé.", "Des majuscules pour insister."],
      bonne: 0, explication: "Sans contexte ni format, l'IA produit une analyse générique. La politesse ne change pas la qualité du résultat." },
    { q: "La première réponse de l'IA est trop générique. Quelle est la meilleure réaction ?",
      options: ["Reposer exactement la même question dans une nouvelle conversation.", "Accepter la réponse : l'IA a fait de son mieux.", "Préciser le contexte et demander à l'IA quelles informations lui manquent.", "Changer d'outil immédiatement."],
      bonne: 2, explication: "Une réponse générique révèle un contexte insuffisant. Faire poser les questions par l'IA est la relance la plus efficace." },
    { q: "Vous voulez une note dans le style de votre organisation. Quelle technique est la plus efficace ?",
      options: ["Écrire « fais une belle note professionnelle ».", "Fournir une note réussie comme modèle de structure et de ton.", "Laisser l'IA deviner le style attendu.", "Ajouter de nombreux adjectifs au prompt."],
      bonne: 1, explication: "Un exemple concret transmet la structure, le ton et le niveau de détail mieux que n'importe quelle description." },
    { q: "Vous voulez que l'IA réponde uniquement à partir du rapport fourni. Quelle consigne donner ?",
      options: ["« Sois précis. »", "« Utilise tes connaissances les plus récentes. »", "« Cite au moins dix sources. »", "« Réponds uniquement à partir du document fourni ; si l'information n'y figure pas, écris : non mentionné dans le document. »"],
      bonne: 3, explication: "L'ancrage explicite, avec une consigne pour les informations absentes, réduit fortement les ajouts non sourcés." },
    { q: "À quoi sert la technique de l'avocat du diable ?",
      options: ["Faire critiquer un document pour en révéler les faiblesses avant un bailleur ou un comité.", "Rendre l'IA plus polie.", "Contourner les règles de l'outil.", "Raccourcir la réponse."],
      bonne: 0, explication: "Demander une critique sévère et structurée permet d'anticiper les objections et de renforcer le document." },
    { q: "Microsoft 365 Copilot, avec votre compte professionnel, peut s'appuyer sur vos fichiers et courriels. Quelle précaution prendre ?",
      options: ["Aucune : tout reste confidentiel.", "Vérifier quels documents il cite et ne pas diffuser d'informations internes au-delà de leur public prévu.", "Ne jamais l'utiliser dans Word.", "Lui interdire de répondre en français."],
      bonne: 1, explication: "Copilot peut mobiliser des documents internes auxquels vous avez accès. Le risque est de les diffuser hors de leur cercle prévu." }
  ]
};
