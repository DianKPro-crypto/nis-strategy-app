const ERREURS = [
  {
    id: "err-abandon",
    titre: "Taux d'abandon Penta1–Penta3 : l'analyse de quatre districts",
    domaine: "donnees",
    contexte: "Prompt donné à l'IA : « Calcule les couvertures Penta1 et Penta3 et les taux d'abandon Penta1–Penta3 de ces 4 districts, identifie le district prioritaire et propose des pistes d'action. » Données fournies (fictives, 2025) — population cible 0-11 mois / Penta1 / Penta3 / séances de stratégie avancée : district A 10 000 / 9 200 / 8 280 / 40 ; district B 8 000 / 6 400 / 5 120 / 22 ; district C 12 500 / 11 400 / 10 830 / 65 ; district D 6 000 / 6 600 / 6 336 / 58.",
    segments: [
      { t: "Voici l'analyse des quatre districts à partir des données que vous avez fournies." },
      { t: "\n" },
      { t: "Couverture vaccinale (doses administrées / population cible × 100). Le district A atteint 92,0 % en Penta1 et 82,8 % en Penta3, le district B 80,0 % et 64,0 %, le district C 91,2 % et 86,6 %." },
      { t: "Le district D affiche une performance remarquable, avec 110,0 % en Penta1 et 105,6 % en Penta3 : il dépasse sa cible et ses pratiques pourraient servir de modèle aux autres districts.", err: true, type: "Mauvais dénominateur", explication: "Une couverture supérieure à 100 % signale le plus souvent une population cible sous-estimée ou des enfants venus d'autres districts, pas une performance. Un professionnel la signale comme un problème de qualité des données à investiguer, au lieu d'en faire un modèle." },
      { t: "\n" },
      { t: "Taux d'abandon Penta1–Penta3, calculé selon la formule (Penta1 − Penta3) / Penta1 × 100. Les districts C (5,0 %) et D (4,0 %) restent nettement sous le seuil d'alerte de 10 %." },
      { t: "Le district A perd 920 enfants entre la première et la troisième dose, soit un taux d'abandon de 8,2 % : il reste lui aussi sous le seuil.", err: true, type: "Calcul erroné", explication: "920 / 9 200 = 10,0 %, et non 8,2 %. Le district A atteint donc le seuil de 10 % et relève d'un problème d'utilisation : refaire la division à la main suffit à le voir." },
      { t: "Le district B est le plus préoccupant : son taux d'abandon atteint 25,0 % ((6 400 − 5 120) / 5 120), soit plus du double du seuil.", err: true, type: "Mauvais dénominateur", explication: "L'abandon se rapporte à Penta1 : 1 280 / 6 400 = 20,0 %. Le calcul divise ici par Penta3, ce qui gonfle le taux et contredit la formule annoncée juste avant." },
      { t: "Sa couverture Penta1 se situe exactement au seuil de 80 % et, selon l'estimation de population, environ 1 600 enfants de la cohorte n'auraient reçu aucune dose de Penta1 : il cumule donc une fragilité d'accès et un problème d'utilisation." },
      { t: "\n" },
      { t: "Les données montrent clairement que la stratégie avancée réduit l'abandon : les districts C et D, qui ont réalisé le plus de séances (65 et 58), ont les taux d'abandon les plus faibles. Doubler les séances dans le district B suffira donc à ramener son abandon sous 10 %.", err: true, type: "Causalité abusive", explication: "Une association observée sur quatre districts ne prouve pas un lien de cause à effet : accessibilité, ruptures de stock, effectifs de personnel ou insécurité peuvent expliquer les écarts. Un professionnel exige une hypothèse à vérifier, pas une solution présentée comme garantie." },
      { t: "Avant toute décision, confrontez ces constats aux rapports de supervision, aux données de gestion des stocks et, si possible, aux résultats d'une enquête de couverture." }
    ],
    bilan: "Refaites au moins deux calculs à la main, vérifiez que l'abandon est rapporté à Penta1, traitez toute couverture supérieure à 100 % comme une alerte sur le dénominateur et exigez que les explications soient formulées comme des hypothèses à vérifier."
  },
  {
    id: "err-note-politique",
    titre: "Note d'orientation : introduction du vaccin HPV",
    domaine: "decision",
    contexte: "Prompt donné à l'IA : « Rédige l'argumentaire et les recommandations d'une note d'orientation au ministre de la Santé du Mabandé (pays fictif) sur l'introduction du vaccin contre le HPV. » Éléments joints : profil du pays, données de scolarisation des filles, carte des zones d'insécurité, budget du PEV.",
    segments: [
      { t: "1. Justification. Le cancer du col de l'utérus figure parmi les cancers les plus fréquents chez les femmes en Afrique subsaharienne, et la quasi-totalité des cas est liée à une infection persistante par des types à haut risque de papillomavirus humain (HPV)." },
      { t: "La vaccination est la plus efficace lorsqu'elle intervient avant toute exposition au virus : c'est pourquoi l'OMS recommande de cibler en priorité les filles de 9 à 14 ans, avec un schéma à une ou deux doses." },
      { t: "Une étude multicentrique conduite dans cinq pays d'Afrique de l'Ouest a d'ailleurs montré qu'une dose unique réduisait de 89 % les infections persistantes à quatre ans (Kouassi, Mensah et Abdou, African Journal of Immunisation Policy, 2022, 14(3), p. 211-224, doi:10.4102/ajip.v14i3.1187).", err: true, type: "Référence inventée", explication: "Référence fabriquée : la combinaison auteurs, revue, volume et DOI ne correspond à aucun article vérifiable, même si l'efficacité d'une dose unique est par ailleurs étayée par de vraies études. Un professionnel recherche le titre ou le DOI (PubMed, Google Scholar) et ouvre l'article avant de le citer." },
      { t: "\n" },
      { t: "2. Acceptabilité. Au Mabandé, 78,4 % des parents se déclarent prêts à faire vacciner leur fille, ce qui offre une base solide pour une introduction rapide.", err: true, type: "Chiffre invérifiable", explication: "Ce chiffre ne figure dans aucun des éléments fournis et aucune source n'est indiquée ; la décimale donne une fausse impression de rigueur. Un professionnel exige la source (enquête, année, échantillon) ou retire le chiffre." },
      { t: "L'adhésion des leaders communautaires, religieux et traditionnels, ainsi qu'un plan de réponse aux rumeurs, notamment celles qui portent sur la fertilité, restent néanmoins déterminants." },
      { t: "\n" },
      { t: "3. Stratégie. La vaccination sera conduite exclusivement en milieu scolaire, auprès des filles de 9 à 14 ans inscrites dans les établissements publics et privés : cette approche permet d'atteindre l'ensemble de la cohorte au moindre coût.", err: true, type: "Angle mort d'équité", explication: "Une stratégie exclusivement scolaire laisse de côté les filles non scolarisées ou déscolarisées, souvent les plus vulnérables, ainsi que celles des zones d'insécurité où les écoles sont fermées et les populations nomades ou déplacées. Les données de scolarisation et la carte d'insécurité jointes imposaient un volet communautaire et en formation sanitaire." },
      { t: "4. Calendrier et financement. Le lancement pourra intervenir simultanément dans toutes les régions dans un délai de trois mois, sur le budget de fonctionnement actuel du PEV, sans formation ni recrutement supplémentaires.", err: true, type: "Recommandation irréaliste", explication: "Une introduction nationale demande habituellement de nombreux mois de préparation (financement, microplanification, chaîne du froid, formation des vaccinateurs, communication) et des ressources dédiées. Un professionnel confronte le calendrier et le budget aux étapes réelles d'une introduction." },
      { t: "Un dispositif de surveillance des manifestations postvaccinales indésirables (MAPI) et un plan de communication de crise devront être opérationnels avant le lancement." },
      { t: "\n" },
      { t: "5. Décision attendue. Il est proposé au Ministre de valider le principe de l'introduction, après avis du groupe technique consultatif national pour la vaccination (GTCV), et de mandater le PEV pour élaborer le plan d'introduction détaillé." }
    ],
    bilan: "Une note fluide peut mêler faits solides, références fabriquées et chiffres sans source : vérifiez chaque référence et chaque chiffre, demandez qui la stratégie laisse de côté, et confrontez calendrier et budget aux étapes réelles d'une introduction."
  },
  {
    id: "err-reglementaire",
    titre: "Liste de cas de rougeole et ChatGPT : la réponse rassurante",
    domaine: "communication",
    contexte: "Une coordinatrice de la surveillance demande : « Puis-je utiliser ChatGPT pour analyser la base de données des cas de rougeole avec noms et villages ? » L'IA a été chargée de rédiger une réponse claire pour l'équipe pays.",
    segments: [
      { t: "Avant tout : une base de cas de rougeole contenant les noms et les villages est une liste nominative de données de santé, c'est-à-dire des données personnelles particulièrement sensibles." },
      { t: "Elle ne doit donc pas être importée telle quelle dans un assistant IA grand public, quel que soit l'objectif de l'analyse." },
      { t: "Rassurez-vous cependant : il suffit de supprimer la colonne des noms. Les données deviennent alors anonymes et ne relèvent plus de la réglementation sur les données personnelles, ce qui vous permet de les analyser sans autre formalité.", err: true, type: "Affirmation réglementaire fausse", explication: "Supprimer le nom ne rend pas les données anonymes : village, âge et date d'éruption suffisent souvent à reconnaître un cas, surtout dans une petite localité, et les données restent personnelles au sens du RGPD comme des lois nationales, qui visent généralement toute personne identifiable directement ou indirectement. Le réflexe professionnel : se demander si un cas peut être reconnu par recoupement." },
      { t: "Appliquez aussi le principe de minimisation : ne conservez que les variables strictement nécessaires à la question posée. Pour décrire la dynamique de l'épidémie, la semaine d'éruption, la tranche d'âge, le statut vaccinal et le district suffisent le plus souvent." },
      { t: "Pour l'outil lui-même, privilégiez un compte payant : contrairement aux versions gratuites, les abonnements payants garantissent que vos données ne sont ni conservées ni réutilisées par le fournisseur.", err: true, type: "Généralisation hors contexte", explication: "Les conditions de conservation et de réutilisation dépendent de l'offre, du contrat et des paramètres choisis, pas du seul fait de payer ; un compte individuel, même payant, n'est pas un outil approuvé par l'institution. Un professionnel vérifie les conditions effectives et la liste des outils autorisés." },
      { t: "\n" },
      { t: "Chaque fois que possible, travaillez sur des données agrégées, par exemple le nombre de cas par semaine, par tranche d'âge et par district, et masquez les effectifs très faibles qui permettraient de reconnaître un enfant ou une famille." },
      { t: "Si une analyse au niveau individuel est indispensable, elle doit se faire dans un environnement approuvé par votre institution, comme le système national d'information sanitaire ou un logiciel statistique installé sur un poste sécurisé, et non dans un assistant IA grand public." },
      { t: "Consultez le délégué à la protection des données (DPO) ou le service juridique de votre organisation, et vérifiez la loi de protection des données du pays concerné : de nombreux pays africains disposent d'une loi spécifique et d'une autorité de contrôle." },
      { t: "\n" },
      { t: "Enfin, une fois les données préparées, vous pourrez vous fier aux résultats : l'IA vérifie automatiquement ses calculs avant de les afficher, ce qui écarte tout risque d'erreur sur les taux d'attaque ou la létalité.", err: true, type: "Généralisation hors contexte", explication: "Un modèle de langage ne vérifie pas spontanément ses calculs ; même une fonction d'analyse qui exécute du code peut appliquer une mauvaise formule, un mauvais filtre ou un mauvais dénominateur. Un professionnel refait les calculs clés et contrôle les effectifs." },
      { t: "Gardez néanmoins une trace écrite de la démarche suivie et faites relire l'analyse par un épidémiologiste de l'équipe avant diffusion." }
    ],
    bilan: "Sur la protection des données, une réponse d'IA rassurante n'a aucune valeur juridique : supprimer les noms n'anonymise pas, un abonnement payant ne garantit rien en soi, et ce sont la politique de votre institution, le DPO et la loi nationale qui font foi."
  }
];
