const MODULE_M5 = {
  id: "m5", num: 5,
  titre: "Éthique et réglementation",
  sousTitre: "Protéger les données de santé, connaître le droit applicable en Afrique et en Europe, servir l'équité.",
  competence: "ethique",
  lecons: [
    {
      id: "m5-donnees", titre: "Protection des données de santé : lois africaines et RGPD", duree: 5,
      contenu: `<p>Coller un tableau dans un assistant d'IA est un <strong>traitement de données</strong>. Si les données concernent des personnes, le droit de la protection des données s'applique, et les données de santé y figurent presque partout parmi les données <strong>sensibles</strong>, protégées par un régime renforcé.</p>
<h4>En Afrique : un socle désormais majoritaire</h4>
<p>La grande majorité des pays africains disposent d'une loi générale de protection des données personnelles et d'une autorité de contrôle : Commission de protection des données personnelles (CDP) au Sénégal, ARTCI en Côte d'Ivoire, APDP au Mali, NDPC au Nigeria, ODPC au Kenya, Information Regulator en Afrique du Sud, par exemple. Ces lois s'inspirent de l'Acte additionnel de la CEDEAO (2010), de la loi type de la SADC (2013) et de la Convention de Malabo de l'Union africaine, entrée en vigueur en 2023. L'onglet « Repères par pays » de la page Éthique résume la situation des 54 pays.</p>
<h4>Les principes communs à retenir</h4>
<ul>
<li><strong>Finalité et minimisation</strong> : ne partager que les données strictement nécessaires à la tâche.</li>
<li><strong>Sécurité et confidentialité</strong> : un outil non approuvé n'offre aucune garantie contractuelle.</li>
<li><strong>Transferts hors du pays</strong> : la plupart des assistants d'IA traitent les données sur des serveurs situés hors d'Afrique. Beaucoup de lois africaines encadrent ces transferts, et certaines exigent une autorisation préalable de l'autorité.</li>
<li><strong>Droits des personnes</strong> : information, accès, opposition.</li>
</ul>
<h4>Quand le RGPD européen s'applique-t-il ?</h4>
<p>Le RGPD classe les données de santé parmi les catégories particulières (article 9). Il s'impose à vous lorsque vous travaillez pour une organisation établie dans l'Union européenne ou en sous-traitance pour elle (bailleur, université, ONG), ou lorsque vous ciblez des personnes situées dans l'Union. Les agences des Nations Unies appliquent leurs propres politiques, fondées sur les Principes des Nations Unies relatifs à la protection des données personnelles et de la vie privée (2018).</p>
<h4>Anonymiser vraiment</h4>
<p>Supprimer le nom ne suffit pas. Une combinaison village + âge + date de vaccination suffit souvent à ré-identifier un enfant dans une petite localité. Agrégez au district, masquez les effectifs inférieurs à 5, retirez les coordonnées GPS des ménages.</p>
<div class="encadre"><strong>Règle pratique.</strong> En cas de doute, posez la question au délégué à la protection des données de votre organisation ou à l'autorité nationale, pas à l'IA.</div>`,
      retenir: [
        "Les données de santé sont des données sensibles dans la quasi-totalité des lois applicables.",
        "Utiliser un assistant d'IA hébergé à l'étranger peut constituer un transfert international de données.",
        "Supprimer le nom n'est pas anonymiser : agrégez et masquez les petits effectifs."
      ]
    },
    {
      id: "m5-aiact", titre: "AI Act et cadres internationaux", duree: 5,
      contenu: `<p>Plusieurs textes encadrent l'usage de l'IA en santé. Aucun ne vous interdit d'utiliser un assistant pour rédiger ou analyser ; tous vous demandent de le faire de façon responsable, transparente et équitable.</p>
<h4>Le règlement européen sur l'IA (AI Act)</h4>
<p>Entré en vigueur le 1er août 2024, il classe les systèmes d'IA selon leur niveau de risque. Les pratiques inacceptables sont interdites depuis février 2025. Les obligations des modèles d'IA à usage général s'appliquent depuis août 2025, celles de transparence depuis août 2026. Les systèmes à haut risque, dont ceux qui conditionnent l'accès aux services de santé et les dispositifs médicaux, relèvent d'un calendrier modifié en juillet 2026 par l'« omnibus numérique » : leurs obligations sont reportées à fin 2027 et 2028. Consultez l'onglet « Cadres de référence » pour le détail des dates, et EUR-Lex pour le texte qui fait foi.</p>
<p>Pour un acteur africain, l'AI Act s'applique directement lorsqu'un système est mis sur le marché ou utilisé dans l'Union. Il compte aussi indirectement : de nombreux partenaires européens l'intègrent dans leurs exigences contractuelles. Son article 4 demande aux organisations de soutenir la <strong>maîtrise de l'IA</strong> de leurs équipes : c'est précisément l'objet de cette application.</p>
<h4>Les repères de l'OMS</h4>
<p>En 2021, l'OMS a posé six principes pour l'IA en santé : protéger l'autonomie humaine ; promouvoir le bien-être, la sécurité et l'intérêt public ; garantir la transparence et l'intelligibilité ; favoriser la responsabilité ; garantir l'inclusion et l'équité ; promouvoir une IA réactive et durable. Ses orientations de 2024 sur les grands modèles multimodaux appliquent ces principes à l'IA générative.</p>
<h4>Les cadres africains</h4>
<ul>
<li><strong>Stratégie continentale de l'Union africaine sur l'IA</strong> (juillet 2024) : approche centrée sur le développement, la santé parmi les secteurs prioritaires.</li>
<li><strong>Convention de Malabo</strong> (en vigueur depuis 2023) et <strong>Cadre de politique des données de l'UA</strong> (2022).</li>
<li>Un nombre croissant de <strong>stratégies nationales d'IA</strong>, à consulter pour chaque pays d'intervention.</li>
</ul>
<p>La <strong>Recommandation de l'UNESCO sur l'éthique de l'IA</strong> (2021), adoptée par ses 193 États membres, complète ce socle.</p>
<div class="encadre"><strong>Pour votre pratique.</strong> Ces textes convergent vers quatre exigences : supervision humaine, transparence sur l'usage de l'IA, protection des données et attention à l'équité. La checklist éthique les rend opérationnelles.</div>`,
      retenir: [
        "L'AI Act suit une logique de risque ; son calendrier a été modifié en 2026, vérifiez toujours les dates en vigueur.",
        "Les six principes de l'OMS (2021) restent la référence éthique pour l'IA en santé.",
        "Supervision humaine, transparence, protection des données et équité : les quatre exigences communes à tous les cadres."
      ]
    },
    {
      id: "m5-equite", titre: "Équité en santé et IA", duree: 5,
      contenu: `<p>L'IA peut aider à atteindre les populations laissées pour compte. Elle peut aussi les rendre encore plus invisibles. La différence tient à la manière dont vous l'utilisez.</p>
<h4>Comment l'IA peut creuser les inégalités</h4>
<ul>
<li><strong>Données lacunaires</strong> : les communautés sans formation sanitaire, les populations nomades ou déplacées et les quartiers informels sont sous-représentés dans les données de routine. Ce qui manque dans les données disparaît de l'analyse.</li>
<li><strong>Critères d'optimisation</strong> : une priorisation fondée sur le seul coût par enfant vacciné défavorise systématiquement les zones éloignées ou en insécurité.</li>
<li><strong>Langues</strong> : les modèles maîtrisent mal de nombreuses langues africaines ; des messages traduits automatiquement peuvent être faux ou maladroits.</li>
<li><strong>Stéréotypes</strong> : des contenus qui ne s'adressent qu'aux mères renforcent l'idée que la vaccination ne concerne pas les pères ni les autres aidants.</li>
</ul>
<h4>Cinq réflexes d'équité</h4>
<ol>
<li>Demandez des analyses désagrégées : sexe, milieu de résidence, quintile de richesse (enquêtes EDS et MICS), zones d'insécurité.</li>
<li>Posez explicitement la question : « Quels groupes cette analyse risque-t-elle d'oublier ? »</li>
<li>Rendez les critères de priorisation explicites et incluez un critère d'équité, par exemple le nombre d'enfants zéro-dose.</li>
<li>Faites valider les messages en langues locales par des locuteurs et des relais communautaires.</li>
<li>Associez les acteurs concernés à la validation des conclusions avant décision.</li>
</ol>
<p>L'Agenda pour la vaccination à l'horizon 2030 (IA2030) place l'équité et les enfants zéro-dose au cœur des priorités. Une analyse assistée par l'IA qui ne dit rien de ces enfants est incomplète, quelle que soit sa qualité technique.</p>
<div class="encadre"><strong>Test simple.</strong> Avant de valider une recommandation, demandez-vous qui en bénéficie, qui en supporte le coût, et qui n'a pas été consulté.</div>`,
      retenir: [
        "Ce qui est absent des données disparaît de l'analyse : cherchez activement les groupes manquants.",
        "Un critère d'efficacité seul pénalise les populations difficiles à atteindre ; ajoutez un critère d'équité explicite.",
        "Les messages en langues locales se valident avec des locuteurs, jamais par la seule traduction automatique."
      ]
    }
  ],
  quiz: [
    { q: "Vous voulez faire analyser par un assistant d'IA grand public une liste d'enfants perdus de vue, avec noms et villages. Que faire ?",
      options: ["L'utiliser, puisque l'objectif est de rattraper ces enfants.", "Supprimer uniquement la colonne des noms, puis l'utiliser.", "Ne pas utiliser de données nominatives : travailler sur des données agrégées par aire de santé, ou dans un outil expressément approuvé.", "Demander à l'IA si c'est autorisé."],
      bonne: 2, explication: "Il s'agit de données personnelles de santé (niveau N3). Supprimer le nom ne suffit pas : le village et l'âge permettent souvent de ré-identifier un enfant." },
    { q: "Pourquoi l'usage d'un assistant d'IA hébergé hors d'Afrique peut-il poser une question juridique ?",
      options: ["Parce que l'IA ne comprend pas le français.", "Parce que partager des données personnelles peut constituer un transfert international, encadré par de nombreuses lois nationales.", "Parce que les assistants d'IA sont interdits en Afrique.", "Il n'y a jamais de question juridique si le compte est payant."],
      bonne: 1, explication: "Beaucoup de lois africaines encadrent les transferts de données hors du pays. Un compte payant ne remplace ni une base légale ni des garanties contractuelles." },
    { q: "Dans quel cas le RGPD européen s'impose-t-il à un consultant travaillant en Afrique de l'Ouest ?",
      options: ["Jamais : le RGPD ne s'applique qu'en Europe.", "Toujours, pour toute donnée de santé dans le monde.", "Uniquement s'il utilise ChatGPT.", "Lorsqu'il traite des données pour une organisation établie dans l'Union européenne, par exemple en sous-traitance pour une ONG ou une université européenne."],
      bonne: 3, explication: "Le RGPD s'applique notamment par la relation contractuelle avec un responsable de traitement établi dans l'Union, et lorsque des personnes situées dans l'Union sont ciblées." },
    { q: "Lequel de ces éléments fait partie des six principes de l'OMS pour l'IA en santé (2021) ?",
      options: ["Garantir l'inclusion et l'équité.", "Maximiser la vitesse de traitement.", "Remplacer la décision clinique par l'algorithme.", "Privilégier les outils gratuits."],
      bonne: 0, explication: "Les six principes : autonomie humaine, bien-être et sécurité, transparence, responsabilité, inclusion et équité, IA réactive et durable." },
    { q: "Une priorisation des districts réalisée avec l'IA repose uniquement sur le coût par enfant vacciné. Quel est le risque principal ?",
      options: ["Aucun : c'est le critère le plus objectif.", "Défavoriser systématiquement les zones éloignées ou en insécurité, où se concentrent souvent les enfants zéro-dose.", "Un calcul trop lent.", "Une violation de l'AI Act."],
      bonne: 1, explication: "Un critère d'efficacité seul pénalise les populations difficiles à atteindre. Ajoutez un critère d'équité explicite." },
    { q: "Comment valider des messages de sensibilisation traduits en langue locale par l'IA ?",
      options: ["Les diffuser tels quels : la traduction automatique est fiable.", "Les retraduire en français avec la même IA pour vérifier.", "Les faire relire par des locuteurs et des relais communautaires avant diffusion.", "Les raccourcir pour limiter les erreurs."],
      bonne: 2, explication: "Les modèles maîtrisent inégalement les langues africaines. Seule une relecture humaine par des locuteurs garantit le sens et le ton." }
  ]
};
