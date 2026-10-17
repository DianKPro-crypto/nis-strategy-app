// Boussole IA · Santé publique — bibliothèque de prompts (Schéma 1 de la SPEC)
// Toutes les données d'exemple sont fictives.

const PROMPTS = [

// ============================================================
// Domaine : donnees — Données épidémiologiques & PEV
// ============================================================

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
},

{
  id: "pev-zero-dose",
  domaine: "donnees",
  titre: "Estimer et caractériser les enfants zéro-dose d'une région",
  resume: "Chiffrer les zéro-dose par district, repérer les communautés probablement concernées et formuler des hypothèses d'équité.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "4 h", avec: "1 h 15" },
  champs: [
    { id: "zone", label: "Zone d'analyse", exemple: "Région Est d'un pays sahélien (fictive), 5 districts sanitaires", type: "texte" },
    { id: "periode", label: "Période couverte", exemple: "janvier–décembre 2025", type: "texte" },
    { id: "donnees", label: "Tableau agrégé par district (copier-coller)", exemple: "District | Pop. cible 0-11 mois | Penta1 | Penta3 | Contexte connu\nDistrict A | 14 200 | 13 100 | 11 900 | chef-lieu, quartiers périphériques informels en forte croissance\nDistrict B | 8 600 | 5 900 | 5 100 | zone frontalière, incidents sécuritaires, 2 centres de santé fermés depuis mars\nDistrict C | 11 300 | 10 950 | 9 800 | rural, bon accès routier\nDistrict D | 6 900 | 4 300 | 3 700 | éleveurs transhumants, accès difficile en saison des pluies\nDistrict E | 9 700 | 9 900 | 8 800 | site de déplacés internes ouvert en 2025, hôpital régional", type: "zone", aide: "Données agrégées par district uniquement. Jamais de liste nominative ni de données par village de très petite taille." },
    { id: "enquetes", label: "Résultats d'enquêtes disponibles (EDS, MICS, enquête de couverture)", exemple: "Enquête de couverture vaccinale fictive 2024, représentative au niveau régional uniquement : 17 % des enfants de 12-23 mois sans aucune dose de vaccin contenant la valence DTC (carte ou déclaration de la mère) ; écart marqué entre le quintile le plus pauvre et le plus riche. Aucune donnée par district.", type: "zone", aide: "Précisez l'année, le niveau de représentativité et la définition utilisée. Écrivez « aucune » s'il n'y en a pas." },
    { id: "public", label: "Destinataire de l'analyse", exemple: "Équipe régionale de santé et partenaires (UNICEF, OMS, ONG) en préparation d'un plan zéro-dose", type: "texte" }
  ],
  modele: `Tu es épidémiologiste spécialiste de la vaccination et de l'équité, expérimenté(e) dans l'analyse des enfants zéro-dose en Afrique, y compris en contexte d'insécurité, de mobilité des populations et d'urbanisation rapide.

CONTEXTE
Je prépare une analyse des enfants zéro-dose pour : {{zone}}, période {{periode}}. Elle est destinée à : {{public}}.
Définitions à utiliser : un enfant zéro-dose est un enfant qui n'a reçu aucune dose de vaccin contenant la valence DTC ; on l'approche par l'absence de Penta1. Un enfant ayant reçu Penta1 mais pas Penta3 est incomplètement vacciné.

TÂCHE
1. Pour chaque district, calcule : couverture Penta1 (Penta1 / population cible × 100) ; nombre estimé de zéro-dose (population cible − Penta1) ; proportion de zéro-dose (zéro-dose / population cible × 100) ; part du total des zéro-dose de la zone ; nombre d'enfants incomplètement vaccinés (Penta1 − Penta3).
2. Établis deux classements : par nombre absolu de zéro-dose (où se trouve le volume) et par proportion (où le risque est le plus concentré). Commente les différences entre les deux.
3. Triangule avec les enquêtes fournies : compare l'estimation administrative et l'estimation d'enquête, puis explique les écarts possibles (dénominateur, doses administrées à des enfants venus d'autres zones, période et niveau de représentativité de l'enquête, mode de recueil) sans trancher à la place des données.
4. Pour les 3 districts prioritaires, propose des hypothèses sur les communautés probablement concernées (insécurité, populations nomades ou transhumantes, déplacés internes ou réfugiés, quartiers urbains pauvres, obstacles liés au genre comme l'autonomie de décision ou le temps disponible des mères), en t'appuyant uniquement sur le contexte fourni. Pour chaque hypothèse, indique la donnée ou la méthode qui permettrait de la vérifier (microplanification, cartographie des campements, enquête rapide, données des acteurs humanitaires).
5. Propose 3 à 5 pistes d'action différenciées selon les communautés, présentées comme des options à discuter.

DONNÉES ADMINISTRATIVES
{{donnees}}

DONNÉES D'ENQUÊTE
{{enquetes}}

RÈGLES
- Montre tes calculs et utilise un outil de calcul si tu en disposes.
- N'invente aucun chiffre : ni estimation nationale, régionale ou mondiale, ni résultat d'enquête que je n'ai pas fourni. Tu peux rappeler que la réduction du nombre d'enfants zéro-dose est une priorité de l'IA2030 et de Gavi, sans citer de chiffre.
- Si une couverture dépasse 100 % ou si un nombre de zéro-dose est négatif, signale-le comme un problème de dénominateur ou de qualité des données ; ne le remplace pas par zéro sans le dire.
- Sépare clairement les FAITS (issus des données), les HYPOTHÈSES (à vérifier) et les PISTES D'ACTION.
- Ne stigmatise aucune communauté : décris des obstacles d'accès et des besoins, pas des comportements.
- Si une information manque pour conclure, écris « information manquante » et précise laquelle.

FORMAT ATTENDU
- Tableau 1 : District | Pop. cible | Penta1 | Couverture Penta1 | Zéro-dose estimés | % zéro-dose | Part du total | Incomplètement vaccinés.
- Un paragraphe « Triangulation » (8 lignes maximum).
- Tableau 2 : District | Communautés possiblement concernées | Hypothèse | Donnée ou méthode pour vérifier.
- Pistes d'action : 3 à 5 puces.
- Une section « Limites » : dénominateurs, qualité des données, représentativité des enquêtes.
- Longueur totale : 2 pages maximum, rédigées pour : {{public}}.`,
  cadre: {
    C: "Le rôle d'épidémiologiste de l'équité et la définition opérationnelle du zéro-dose évitent de confondre zéro-dose et enfants incomplètement vaccinés.",
    A: "Les 5 étapes vont du calcul au ciblage : volume et proportion, triangulation, hypothèses sur les communautés, puis pistes d'action.",
    D: "Données administratives et données d'enquête sont fournies séparément, ce qui oblige l'IA à confronter deux sources plutôt qu'à en choisir une.",
    R: "Les règles interdisent les chiffres mondiaux inventés, imposent de signaler les dénominateurs défaillants et protègent contre la stigmatisation des communautés.",
    E: "Les deux tableaux et la section « Limites » fournissent une base directement réutilisable dans un plan zéro-dose ou une demande de financement."
  },
  adapter: [
    "Remplacez Penta1 par RR1 pour estimer les enfants non protégés contre la rougeole, en gardant la même logique de calcul.",
    "Ajoutez une colonne « déplacés ou transhumants estimés » si les acteurs humanitaires vous la fournissent, pour mieux lire les dénominateurs.",
    "Au niveau national, demandez d'abord le classement des régions, puis appliquez le prompt aux districts des 2 ou 3 régions qui concentrent le plus de zéro-dose."
  ],
  pieges: [
    "Classer uniquement par proportion masque les districts urbains très peuplés, où le nombre absolu de zéro-dose est souvent le plus élevé.",
    "Un nombre négatif de zéro-dose (District E dans l'exemple) traduit un dénominateur sous-estimé ou des enfants venus d'ailleurs, pas l'absence de zéro-dose.",
    "L'IA plaque volontiers des explications toutes faites (« réticence religieuse », « nomadisme ») sans lien avec vos données : exigez pour chaque hypothèse un élément de contexte et un moyen de vérification."
  ],
  verif: [
    "Recalculez à la main les zéro-dose et la part du total pour 2 districts.",
    "Comparez l'ordre de grandeur obtenu avec l'enquête fournie et, au niveau national, avec les estimations OMS/UNICEF (WUENIC), en tenant compte des différences de méthode.",
    "Soumettez les hypothèses sur les communautés aux équipes de district et confrontez-les à la microplanification avant toute communication."
  ],
  outils: "Un assistant doté d'une fonction d'analyse de données (ChatGPT, Claude, Copilot dans Excel) fiabilise les calculs. Pour croiser avec des rapports d'enquête en PDF, NotebookLM limite les réponses aux documents chargés.",
  lecon: "m5-equite"
},

{
  id: "pev-qualite-donnees",
  domaine: "donnees",
  titre: "Diagnostiquer la qualité d'un extrait DHIS2 de vaccination",
  resume: "Contrôler complétude, promptitude, cohérence interne et valeurs aberrantes, puis établir un plan d'action qualité.",
  niveau: "Avancé",
  donnees: "N1",
  gain: { sans: "5 h", avec: "1 h 30" },
  champs: [
    { id: "zone", label: "Unité d'analyse", exemple: "District sanitaire fictif de Nkolbé, 24 formations sanitaires notifiantes", type: "texte" },
    { id: "periode", label: "Période couverte", exemple: "janvier–juin 2026", type: "texte" },
    { id: "donnees", label: "Extrait DHIS2 (copier-coller)", exemple: "Mois | Rapports attendus | Rapports reçus | Reçus à temps | Cible naissances | Cible 0-11 mois | BCG | Penta1 | Penta3 | RR1\nJanv. | 24 | 24 | 20 | 640 | 610 | 615 | 575 | 498 | 452\nFévr. | 24 | 22 | 14 | 640 | 610 | 560 | 548 | 503 | 431\nMars | 24 | 24 | 21 | 640 | 610 | 1 520 | 590 | 512 | 466\nAvril | 24 | 18 | 8 | 640 | 610 | 420 | 395 | 447 | 301\nMai | 24 | 23 | 19 | 640 | 610 | 630 | 588 | 530 | 480\nJuin | 24 | 24 | 22 | 640 | 610 | 0 | 601 | 527 | 492", type: "zone", aide: "Données agrégées (district ou formation sanitaire). Jamais d'export du registre électronique individuel." },
    { id: "normes", label: "Normes du programme", exemple: "Complétude attendue ≥ 90 % ; promptitude ≥ 80 % ; saisie dans DHIS2 au plus tard le 5 du mois suivant ; doses de campagne à saisir dans un formulaire distinct de la routine", type: "texte", aide: "Reprenez les seuils de votre guide national ; à défaut, l'IA doit signaler qu'elle n'en a pas." },
    { id: "contexte", label: "Événements connus sur la période", exemple: "Campagne de rattrapage dans 6 aires de santé en mars ; grève partielle des agents de santé pendant 2 semaines en avril ; nouveau gestionnaire de données au district depuis mai", type: "zone" }
  ],
  modele: `Tu es spécialiste de la qualité des données de vaccination et des systèmes d'information sanitaire (DHIS2), habitué(e) aux revues de qualité des données (complétude, promptitude, cohérence, exactitude) en Afrique.

CONTEXTE
J'examine un extrait DHIS2 pour : {{zone}}, période {{periode}}.
Normes du programme : {{normes}}
Événements connus sur la période : {{contexte}}

TÂCHE
1. Complétude et promptitude : calcule pour chaque mois la complétude (rapports reçus / rapports attendus × 100) et la promptitude (rapports reçus à temps / rapports attendus × 100), puis compare-les aux normes.
2. Cohérence interne : vérifie mois par mois et sur la période cumulée que Penta3 ≤ Penta1 et que RR1 reste cohérent avec Penta1 ; compare BCG à la cible naissances et à Penta1. Rappelle qu'un léger décalage mensuel peut s'expliquer par le calendrier vaccinal, alors qu'une incohérence sur la période cumulée est une anomalie.
3. Valeurs aberrantes et zéros : repère les valeurs qui s'écartent fortement de la médiane de la période, en indiquant la méthode et le seuil retenus ; distingue un zéro plausible d'une donnée manquante saisie à zéro.
4. Ruptures de série : signale les changements brusques de niveau et ce qui pourrait les expliquer (doses de campagne saisies en routine, changement de dénominateur ou de personnel, rupture de stock).
5. Pour chaque anomalie, propose les causes possibles, présentées comme des hypothèses, et la vérification à faire (registre de vaccination, fiche de pointage, rapport de gestion des vaccins, entretien avec le gestionnaire de données).
6. Propose un plan d'action qualité réaliste pour un district : 5 à 8 actions.
7. Conclus sur l'utilisabilité des données : pour quels usages sont-elles suffisamment fiables, et pour lesquels faut-il attendre des corrections ?

DONNÉES
{{donnees}}

RÈGLES
- Montre tous tes calculs ; utilise un outil de calcul si tu en disposes.
- Ne corrige, ne complète et n'impute aucune valeur : décris l'anomalie et propose la vérification.
- Distingue toujours le CONSTAT (chiffré, issu des données) de la CAUSE POSSIBLE (hypothèse).
- Si une norme n'est pas fournie, dis-le et propose un seuil à faire valider, sans le présenter comme une norme officielle.
- Ne cite aucun guide ni aucune norme que je n'ai pas fournis.

FORMAT ATTENDU
- Tableau 1 : Mois | Complétude | Promptitude | Conforme aux normes (oui / non).
- Tableau 2 : N° | Mois | Indicateur | Constat chiffré | Type d'anomalie (complétude, cohérence, valeur aberrante, rupture) | Causes possibles | Vérification à faire | Gravité (élevée, moyenne, faible).
- Tableau 3 (plan d'action) : Action | Responsable (fonction) | Échéance | Indicateur de suivi.
- Conclusion de 5 lignes maximum sur l'utilisabilité des données.`,
  cadre: {
    C: "Le rôle de spécialiste de la qualité des données et les événements connus (campagne, grève) permettent de relier les anomalies à des explications plausibles sans les inventer.",
    A: "Les 7 étapes suivent la logique d'une revue de qualité : complétude, cohérence, valeurs aberrantes, ruptures, causes, plan d'action, utilisabilité.",
    D: "L'extrait mensuel brut, avec rapports attendus et reçus, permet de calculer les indicateurs plutôt que de les supposer.",
    R: "L'interdiction de corriger ou d'imputer préserve la traçabilité : seule une vérification à la source peut modifier une donnée.",
    E: "Les trois tableaux (indicateurs, anomalies, plan d'action) se transposent directement dans un rapport de supervision ou une réunion de validation des données."
  },
  adapter: [
    "Remplacez les mois par les formations sanitaires d'un même trimestre pour repérer les structures qui concentrent les anomalies.",
    "Ajoutez les données de gestion des vaccins (doses reçues, utilisées, taux de perte) pour confronter doses administrées et doses consommées.",
    "Si l'outil de revue de la qualité des données est installé sur votre DHIS2, collez ses résultats et demandez à l'IA de les interpréter plutôt que de tout recalculer."
  ],
  pieges: [
    "L'IA attribue spontanément le pic de BCG de mars à la campagne, alors qu'une erreur de saisie est aussi possible : exigez une vérification au registre.",
    "Un zéro saisi alors que tous les rapports sont reçus (BCG en juin dans l'exemple) peut être une rupture de stock réelle ou une omission de saisie ; l'IA tranche souvent trop vite.",
    "Les seuils de valeur aberrante varient selon la méthode (médiane, écart-type) : une IA qui ne précise pas sa méthode produit une liste invérifiable."
  ],
  verif: [
    "Recalculez la complétude et la promptitude de 2 mois, dont le plus mauvais.",
    "Vérifiez que chaque anomalie listée existe bien dans l'extrait (ligne et valeur), puis parcourez vous-même les colonnes pour repérer celles que l'IA aurait omises.",
    "Faites valider le plan d'action par le gestionnaire de données du district : responsables et échéances doivent être réalistes."
  ],
  outils: "Préférez un assistant capable d'exécuter des calculs (analyse de données dans ChatGPT ou Claude, Copilot dans Excel) et fournissez l'extrait sous forme de tableau. N'exportez que des agrégats, jamais de données individuelles.",
  lecon: "m4-chiffres"
},

{
  id: "pev-commentaire-tdb",
  domaine: "donnees",
  titre: "Rédiger le commentaire analytique d'un tableau de bord trimestriel",
  resume: "Transformer les indicateurs du trimestre en un commentaire clair qui sépare constats, interprétations et alertes.",
  niveau: "Essentiel",
  donnees: "N1",
  gain: { sans: "2 h", avec: "40 min" },
  champs: [
    { id: "zone", label: "Niveau et zone du tableau de bord", exemple: "Tableau de bord national du PEV (pays fictif), 4 régions", type: "texte" },
    { id: "periode", label: "Trimestre analysé et points de comparaison", exemple: "T3 2026 (juillet–septembre), comparé au T2 2026 et au T3 2025", type: "texte" },
    { id: "indicateurs", label: "Indicateurs et cibles (copier-coller)", exemple: "Indicateur | Cible | T3 2025 | T2 2026 | T3 2026\nCouverture Penta3 du trimestre | 90 % | 81 % | 84 % | 83 %\nCouverture RR1 du trimestre | 90 % | 76 % | 79 % | 80 %\nCouverture RR2 du trimestre | 75 % | 51 % | 58 % | 60 %\nTaux d'abandon Penta1–Penta3 | < 10 % | 9 % | 7 % | 11 %\nComplétude des rapports | ≥ 90 % | 88 % | 93 % | 85 %\nDistricts ayant connu une rupture de stock (au moins 1 antigène) | 0 | 6 | 3 | 9\nCas suspects de rougeole notifiés | — | 120 | 95 | 210", type: "zone", aide: "Indicateurs agrégés uniquement." },
    { id: "contexte", label: "Éléments de contexte connus", exemple: "Mise en service d'un nouveau logiciel de gestion des stocks en juillet ; épidémie de choléra dans la région Nord ayant mobilisé les équipes en août ; retard de livraison du vaccin RR au niveau central", type: "zone" },
    { id: "public", label: "Destinataire du commentaire", exemple: "Comité de coordination inter-agences (CCIA) du PEV", type: "texte" }
  ],
  modele: `Tu es chargé(e) du suivi-évaluation d'un programme de vaccination, rompu(e) à la rédaction de commentaires analytiques pour des instances de coordination.

CONTEXTE
Je dois commenter le tableau de bord suivant : {{zone}}, {{periode}}. Le commentaire sera lu par : {{public}}.
Éléments de contexte connus : {{contexte}}

TÂCHE
1. Pour chaque indicateur, décris l'évolution par rapport au trimestre précédent et au même trimestre de l'année précédente, ainsi que l'écart à la cible, en points de pourcentage.
2. Repère les 3 alertes principales (dégradation, écart important à la cible, signal épidémiologique) et classe-les par ordre de gravité.
3. Relève aussi 1 ou 2 progrès réels, sans les exagérer.
4. Pour chaque alerte, propose des interprétations possibles, en t'appuyant uniquement sur le contexte fourni, et la question à poser ou la donnée à examiner pour les confirmer.
5. Termine par 3 recommandations ou décisions à soumettre à l'instance.

DONNÉES
{{indicateurs}}

RÈGLES
- Sépare strictement deux registres : « Constat » (ce que disent les chiffres) et « Interprétation » (ce qui pourrait l'expliquer, au conditionnel).
- N'invente aucun chiffre, aucune cause, aucun événement absent du contexte fourni.
- Exprime les écarts en points de pourcentage, pas en pourcentage d'évolution, et vérifie chaque soustraction.
- Si une variation est faible, précise qu'elle peut relever des fluctuations ou de la qualité des données plutôt que d'une vraie tendance.
- Signale tout indicateur dont l'interprétation dépend de la qualité des données (par exemple une complétude en baisse).

FORMAT ATTENDU
- En tête, un paragraphe de synthèse de 4 phrases maximum (message principal du trimestre).
- Un tableau : Indicateur | Constat (évolution et écart à la cible) | Interprétation possible | Niveau d'alerte (rouge, orange, vert).
- Les 3 recommandations, sous forme de puces commençant par un verbe d'action.
- Longueur totale : une page maximum, ton factuel, adapté à : {{public}}.`,
  cadre: {
    C: "Le rôle de chargé de suivi-évaluation et le destinataire (CCIA) fixent un registre factuel et institutionnel.",
    A: "Les 5 étapes imposent l'équilibre : évolutions, alertes, progrès, interprétations, puis décisions à soumettre.",
    D: "Les indicateurs sont fournis avec leur cible et deux points de comparaison, ce qui rend chaque évolution calculable et vérifiable.",
    R: "La séparation constat / interprétation empêche l'IA de transformer une hypothèse en fait, défaut classique des commentaires de tableaux de bord.",
    E: "La synthèse en tête, le tableau à code couleur et les recommandations correspondent aux attentes d'une instance de coordination."
  },
  adapter: [
    "Pour un tableau de bord régional, ajoutez une colonne par district et demandez les 3 districts qui contribuent le plus à chaque alerte.",
    "Fournissez le commentaire du trimestre précédent pour que l'IA vérifie le suivi des recommandations déjà formulées.",
    "Pour une présentation orale, demandez en plus 3 phrases d'ouverture à prononcer en 1 minute en début de réunion."
  ],
  pieges: [
    "L'IA mélange points de pourcentage et variation relative : passer de 7 % à 11 % d'abandon, c'est + 4 points, soit une hausse relative d'environ 57 % ; les deux ne se confondent pas.",
    "Une baisse de complétude des rapports peut suffire à expliquer une baisse apparente de couverture : l'IA l'oublie si on ne le lui rappelle pas.",
    "Le contexte fourni devient vite une explication automatique : une épidémie de choléra n'explique pas forcément toutes les dégradations du trimestre."
  ],
  verif: [
    "Recalculez 3 écarts à la cible et 2 évolutions, en points de pourcentage.",
    "Surlignez chaque phrase d'interprétation et vérifiez qu'elle est au conditionnel et rattachée à un élément du contexte fourni.",
    "Vérifiez que les alertes retenues sont bien les plus graves pour votre programme : un signal épidémiologique, comme une hausse des cas suspects de rougeole, doit apparaître en bonne place."
  ],
  outils: "Tout assistant convient si le tableau est court ; pour un tableau de bord sous Excel, Copilot dans Excel peut lire les données directement. Relisez toujours les chiffres recopiés dans le texte.",
  lecon: "m4-hallucinations"
},

{
  id: "epi-surveillance-alerte",
  domaine: "donnees",
  titre: "Analyser des données de surveillance hebdomadaires et repérer les alertes",
  resume: "Lire les cas suspects par district et par semaine, appliquer les seuils du guide national et préparer l'investigation.",
  niveau: "Avancé",
  donnees: "N1",
  gain: { sans: "2 h", avec: "45 min" },
  champs: [
    { id: "maladie", label: "Maladie sous surveillance", exemple: "Rougeole (cas suspects)", type: "texte" },
    { id: "zone", label: "Zone et période", exemple: "Région Centre (pays fictif), 5 districts, semaines épidémiologiques 30 à 37 de 2026", type: "texte" },
    { id: "donnees", label: "Cas par district et par semaine (copier-coller)", exemple: "District | Pop. totale | S30 | S31 | S32 | S33 | S34 | S35 | S36 | S37\nDistrict A | 310 000 | 1 | 0 | 2 | 1 | 1 | 0 | 2 | 1\nDistrict B | 185 000 | 0 | 1 | 1 | 3 | 5 | 8 | 12 | 15\nDistrict C | 240 000 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 3\nDistrict D | 95 000 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0\nDistrict E | 150 000 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0", type: "zone", aide: "Comptes agrégés par district et par semaine. Jamais de liste linéaire de cas (nom, village, âge exact)." },
    { id: "labo", label: "Laboratoire et informations complémentaires", exemple: "District B : 6 prélèvements testés (S33–S35), 4 IgM rougeole positifs, 3 résultats en attente. District D : 3 prélèvements testés, aucun positif. Complétude des rapports hebdomadaires : 100 % sauf District E (60 % sur S34–S37, zone d'insécurité). Couverture RR1 administrative 2025 : District B 68 %, autres districts entre 82 % et 95 %.", type: "zone" },
    { id: "seuils", label: "Seuils et définitions du guide national", exemple: "Seuil d'alerte : 1 cas suspect, qui déclenche investigation et prélèvement. Seuil épidémique : 3 cas confirmés (IgM positifs ou liés épidémiologiquement) dans un district en un mois. (Seuils fictifs à remplacer par ceux de votre guide national.)", type: "zone", aide: "Collez le texte exact de votre guide national (SIMR ou équivalent). L'IA ne doit pas utiliser de seuils de mémoire." },
    { id: "public", label: "Destinataire de l'analyse", exemple: "Équipe régionale d'intervention rapide et point focal surveillance", type: "texte" }
  ],
  modele: `Tu es épidémiologiste de terrain, spécialisé(e) dans la surveillance des maladies évitables par la vaccination et dans la Surveillance intégrée de la maladie et riposte (SIMR) en Afrique.

CONTEXTE
J'analyse les données de surveillance hebdomadaires suivantes : {{maladie}}, {{zone}}. L'analyse est destinée à : {{public}}.
Seuils et définitions de mon guide national, à appliquer strictement : {{seuils}}

TÂCHE
1. Décris l'évolution des cas par district et par semaine épidémiologique ; calcule le total sur la période, compare les 4 dernières semaines aux 4 précédentes et, si les populations sont fournies, calcule l'incidence pour 100 000 habitants sur la période.
2. Applique les seuils fournis à chaque district et indique, pour chacun, si le seuil d'alerte ou le seuil épidémique est atteint, en citant la règle utilisée et les chiffres qui la déclenchent.
3. Intègre les résultats de laboratoire et la qualité de la notification : distingue cas suspects, cas confirmés et résultats en attente ; signale les districts où un silence épidémiologique peut traduire une sous-notification.
4. Formule les questions prioritaires pour l'investigation (statut vaccinal et âge des cas, lieux, liens épidémiologiques, couverture vaccinale locale, populations mobiles ou déplacées) et les données complémentaires à demander.
5. Propose les actions immédiates généralement prévues dans ce type de situation, formulées comme des points à confirmer avec le guide national et l'équipe de riposte.

DONNÉES DE SURVEILLANCE
{{donnees}}

LABORATOIRE ET INFORMATIONS COMPLÉMENTAIRES
{{labo}}

RÈGLES
- Utilise uniquement les seuils fournis ci-dessus, jamais des seuils de mémoire ; s'ils sont incomplets, dis-le.
- Montre tes calculs. N'invente aucun cas, aucun résultat de laboratoire, aucune information de terrain.
- Ne déclare pas d'épidémie : indique seulement si un seuil est franchi selon les règles fournies ; la déclaration relève des autorités sanitaires.
- Rappelle explicitement que ton analyse ne remplace ni l'investigation de terrain ni la confirmation biologique.
- Distingue les FAITS (chiffres), les HYPOTHÈSES (explications possibles) et les ACTIONS PROPOSÉES.
- Si les données sont insuffisantes pour conclure sur un district, écris-le.

FORMAT ATTENDU
- Tableau : District | Cas sur la période | Tendance (4 dernières semaines / 4 précédentes) | Incidence pour 100 000 | Laboratoire (confirmés / testés / en attente) | Seuil franchi (aucun, alerte, épidémique) | Règle appliquée.
- 5 à 8 questions d'investigation, classées par priorité.
- Actions immédiates à confirmer : 5 puces au maximum.
- Une phrase finale rappelant les limites de l'analyse.
- Une page maximum.`,
  cadre: {
    C: "Le rôle d'épidémiologiste SIMR et le guide national collé dans le prompt ancrent l'analyse dans vos règles, pas dans la mémoire approximative du modèle.",
    A: "Les 5 étapes suivent la logique de la surveillance : description, application des seuils, laboratoire et qualité de la notification, investigation, riposte.",
    D: "Cas hebdomadaires, résultats de laboratoire et complétude sont fournis séparément, ce qui permet de distinguer une vraie hausse d'un artefact de notification.",
    R: "Les règles interdisent de déclarer une épidémie et rappellent que l'IA ne remplace ni l'investigation ni la confirmation biologique.",
    E: "Le tableau avec la colonne « Règle appliquée » rend chaque conclusion traçable et vérifiable par l'équipe de riposte."
  },
  adapter: [
    "Remplacez la rougeole par la méningite, la fièvre jaune ou la paralysie flasque aiguë (PFA), en collant les définitions de cas et les seuils correspondants de votre guide.",
    "Ajoutez la répartition agrégée des cas par tranche d'âge et statut vaccinal pour orienter la riposte vaccinale.",
    "Pour un suivi hebdomadaire, gardez la même conversation et collez chaque semaine la nouvelle colonne en demandant uniquement ce qui a changé."
  ],
  pieges: [
    "L'IA applique parfois des seuils génériques mémorisés au lieu de ceux de votre guide : vérifiez la règle citée pour chaque district.",
    "Un district silencieux (District E dans l'exemple) peut être un district qui notifie mal, pas un district sans cas.",
    "Un pic isolé (4 cas en une semaine dans le District D) peut être un regroupement de notifications tardives ou un foyer non confirmé : l'IA tend soit à le surinterpréter, soit à l'ignorer."
  ],
  verif: [
    "Recalculez les totaux et la tendance sur 4 semaines pour chaque district signalé en alerte.",
    "Confrontez chaque seuil déclaré franchi au texte exact de votre guide national et aux résultats officiels du laboratoire de référence.",
    "Faites valider conclusions et actions par le point focal surveillance avant toute diffusion."
  ],
  outils: "Un assistant doté d'une fonction d'analyse de données est préférable pour les calculs. Ne collez que des agrégats par district et par semaine : une liste linéaire de cas relève du niveau N3 et n'a pas sa place dans un assistant généraliste.",
  lecon: "m1-contexte"
},

// ============================================================
// Domaine : decision — Aide à la décision stratégique
// ============================================================

{
  id: "dec-note-options",
  domaine: "decision",
  titre: "Rédiger une note d'options pour un décideur",
  resume: "Comparer 3 options (avantages, coûts relatifs, risques, faisabilité) et proposer une recommandation argumentée.",
  niveau: "Intermédiaire",
  donnees: "N2",
  gain: { sans: "6 h", avec: "2 h" },
  champs: [
    { id: "decision", label: "Décision à prendre", exemple: "Choisir la stratégie de rattrapage des enfants de 12 à 59 mois non vaccinés ou incomplètement vaccinés dans 3 districts prioritaires", type: "texte" },
    { id: "decideur", label: "Décideur et contexte institutionnel", exemple: "Secrétaire général du ministère de la Santé ; arbitrage attendu avant la soumission du plan annuel aux partenaires", type: "texte" },
    { id: "options", label: "Options envisagées (une ligne chacune)", exemple: "Option 1 : intensifier la vaccination de routine (séances avancées et mobiles supplémentaires pendant 6 mois)\nOption 2 : organiser des semaines de rattrapage ciblées, en 2 passages\nOption 3 : intégrer le rattrapage aux distributions de moustiquaires et aux consultations nutritionnelles existantes", type: "zone" },
    { id: "elements", label: "Éléments disponibles (données, coûts, contraintes)", exemple: "Environ 23 000 enfants de 12 à 59 mois à rattraper selon la microplanification (estimation fictive). Enveloppe de rattrapage non encore arbitrée. Coût par enfant vacciné : estimé pour les options 1 et 2 dans le budget du programme, non disponible pour l'option 3. Contraintes : zones d'insécurité dans 2 districts sur 3 ; manque d'agents qualifiés ; saison des pluies de juin à septembre.", type: "zone", aide: "N'indiquez que les montants que vous êtes autorisé à partager. Un budget non publié relève du niveau N2 : outil institutionnel uniquement, ou montants remplacés par des ordres de grandeur." },
    { id: "criteres", label: "Critères qui comptent pour le décideur", exemple: "Nombre d'enfants atteints, coût, rapidité de mise en œuvre, équité (zones d'insécurité), effet sur le renforcement de la routine", type: "texte" }
  ],
  modele: `Tu es conseiller(ère) stratégique senior en santé publique, spécialiste de la vaccination et de la rédaction de notes d'aide à la décision pour des responsables ministériels en Afrique.

CONTEXTE
Décision à prendre : {{decision}}
Décideur et contexte : {{decideur}}
Critères importants pour le décideur : {{criteres}}

TÂCHE
1. Reformule en 2 phrases le problème et l'enjeu de la décision.
2. Pour chacune des options ci-dessous, analyse : description synthétique, avantages, inconvénients, coût relatif (faible, moyen, élevé, avec justification), risques principaux, faisabilité (ressources humaines, logistique, sécurité, calendrier) et effet sur l'équité.
3. Compare les options dans un tableau, selon les critères du décideur.
4. Formule une recommandation argumentée (une option ou une combinaison), en précisant ses conditions de succès et ce qui ferait changer cette recommandation.
5. Liste les informations manquantes qui limitent l'analyse et la façon de les obtenir avant la décision.

OPTIONS ENVISAGÉES
{{options}}

ÉLÉMENTS DISPONIBLES
{{elements}}

RÈGLES
- Présente chaque option avec la même rigueur et la même honnêteté, y compris celle que tu recommandes ; ne caricature aucune option pour mettre une autre en valeur.
- N'invente aucun coût, aucune donnée de couverture, aucune référence. Les coûts sont relatifs et justifiés ; si un coût manque, écris « à chiffrer ».
- Distingue les FAITS (issus des éléments fournis), les HYPOTHÈSES et les JUGEMENTS.
- Ta recommandation est une aide : la décision appartient au décideur. N'emploie aucune formulation qui la présenterait comme acquise.
- Tiens compte des contraintes de terrain fournies (insécurité, saisons, ressources humaines).

FORMAT ATTENDU
- Note de 2 pages maximum, structurée ainsi : Objet | Contexte et enjeu | Options | Tableau comparatif | Recommandation | Informations manquantes et prochaines étapes.
- Tableau comparatif : Critère | Option 1 | Option 2 | Option 3 (appréciation qualitative et justification courte).
- Style administratif sobre, phrases courtes, sigles développés, adapté à : {{decideur}}.`,
  cadre: {
    C: "Le rôle de conseiller stratégique et les critères du décideur orientent l'analyse vers ce qui compte réellement pour l'arbitrage.",
    A: "Les étapes appliquent la même grille d'analyse à chaque option, puis une comparaison et une recommandation conditionnelle.",
    D: "Les éléments disponibles et leurs lacunes sont explicites : l'IA ne peut pas combler un coût manquant par une estimation inventée.",
    R: "L'obligation de traiter chaque option avec la même honnêteté limite la complaisance de l'IA envers l'option qu'elle devine préférée.",
    E: "La structure classique d'une note d'options permet au décideur de lire la recommandation en 2 minutes et le détail s'il le souhaite."
  },
  adapter: [
    "Ajoutez une option « statu quo » pour rendre visible le coût de l'inaction.",
    "Réduisez à 2 options si le décideur a déjà écarté une piste, en demandant à l'IA de rappeler en une phrase pourquoi elle a été écartée.",
    "Pour un arbitrage budgétaire, fournissez des coûts unitaires validés et demandez le coût total de chaque option, avec les hypothèses de calcul affichées."
  ],
  pieges: [
    "L'IA devine souvent l'option que vous préférez à la formulation du prompt et la favorise : vérifiez que les inconvénients de l'option recommandée sont aussi détaillés que ceux des autres.",
    "Les coûts relatifs (« faible », « élevé ») peuvent cacher des hypothèses implicites ou des montants imaginés : exigez la justification de chaque appréciation.",
    "La faisabilité en zone d'insécurité est souvent sous-estimée : une option séduisante sur le papier peut être inapplicable dans 2 districts sur 3."
  ],
  verif: [
    "Contrôlez que chaque fait cité figure dans les éléments fournis ; supprimez ou sourcez le reste.",
    "Faites relire la note par un responsable logistique ou une équipe de district pour tester la faisabilité de chaque option.",
    "Vérifiez que la recommandation reste formulée comme une proposition et que les informations manquantes sont listées."
  ],
  outils: "Un assistant généraliste suffit pour la rédaction. Un budget non publié ou une négociation en cours relève du niveau N2 : utilisez uniquement l'outil institutionnel autorisé par votre organisation, ou anonymisez montants et lieux.",
  lecon: "m4-biais"
},

{
  id: "dec-priorisation",
  domaine: "decision",
  titre: "Prioriser des districts avec une matrice multicritère pondérée",
  resume: "Classer districts ou interventions selon vos critères et pondérations, puis tester la robustesse du classement.",
  niveau: "Avancé",
  donnees: "N1",
  gain: { sans: "4 h", avec: "1 h 30" },
  champs: [
    { id: "objet", label: "Objet de la priorisation", exemple: "Sélection de 4 districts sur 8 pour un appui renforcé à la vaccination de routine (financement de 18 mois)", type: "texte" },
    { id: "criteres", label: "Critères, pondérations et sens de lecture", exemple: "Nombre d'enfants zéro-dose estimés : 35 % (plus élevé = plus prioritaire)\nTaux d'abandon Penta1–Penta3 : 20 % (plus élevé = plus prioritaire)\nCouverture RR1 : 20 % (plus faible = plus prioritaire)\nCas suspects de rougeole sur 12 mois : 15 % (plus élevé = plus prioritaire)\nAccessibilité sécuritaire pour les équipes : 10 % (plus accessible = plus prioritaire)", type: "zone", aide: "Les pondérations doivent totaliser 100 %. Précisez pour chaque critère si une valeur élevée augmente ou diminue la priorité." },
    { id: "donnees", label: "Valeurs par district (copier-coller)", exemple: "District | Zéro-dose estimés | Abandon Penta1–Penta3 | Couverture RR1 | Cas suspects rougeole | Accessibilité (1 faible – 3 bonne)\nDistrict A | 1 450 | 8 % | 84 % | 12 | 3\nDistrict B | 2 900 | 14 % | 66 % | 41 | 1\nDistrict C | 600 | 11 % | 79 % | 5 | 3\nDistrict D | 2 100 | 6 % | 71 % | 18 | 2\nDistrict E | 350 | 15 % | 88 % | 2 | 3\nDistrict F | 1 800 | 12 % | 74 % | 25 | 2\nDistrict G | 950 | 9 % | 81 % | 9 | 1\nDistrict H | 2 400 | 10 % | 69 % | 30 | 2", type: "zone", aide: "Valeurs agrégées par district." },
    { id: "contraintes", label: "Contraintes et règles de décision", exemple: "Au moins 1 district de la zone frontalière (B ou G) ; pas plus de 2 districts déjà appuyés par un autre partenaire (A, D et H le sont)", type: "texte" }
  ],
  modele: `Tu es analyste en aide à la décision et en planification sanitaire, maîtrisant les méthodes de priorisation multicritère et les programmes de vaccination.

CONTEXTE
Objet de la priorisation : {{objet}}
Contraintes et règles de décision : {{contraintes}}

TÂCHE
1. Vérifie les critères : les pondérations totalisent-elles 100 % ? Le sens de chaque critère est-il clair ? Signale les critères redondants (fortement liés entre eux) et ceux qui pourraient entrer en tension avec l'équité.
2. Normalise chaque critère sur une échelle de 0 à 1 par la méthode min-max : (valeur − min) / (max − min), ou (max − valeur) / (max − min) lorsque « plus faible = plus prioritaire ». Présente la formule appliquée à chaque critère.
3. Calcule le score pondéré de chaque district (somme des scores normalisés × pondérations) et établis le classement.
4. Analyse de sensibilité : recalcule le classement avec (a) des pondérations égales, (b) le critère le plus lourd réduit de 10 points, redistribués proportionnellement sur les autres, (c) le critère le plus discutable du point de vue de l'équité retiré, en justifiant ce choix. Indique les districts dont le rang est stable et ceux dont le rang dépend des pondérations.
5. Applique ensuite les contraintes et règles de décision, puis propose la sélection finale en expliquant chaque écart par rapport au classement brut.
6. Liste les limites : qualité des données, critères manquants, valeurs à vérifier.

CRITÈRES ET PONDÉRATIONS
{{criteres}}

DONNÉES PAR DISTRICT
{{donnees}}

RÈGLES
- Utilise un outil de calcul si tu en disposes et montre les calculs intermédiaires (au minimum les scores normalisés).
- N'ajoute aucun critère et ne modifie aucune pondération sans le présenter clairement comme une proposition distincte.
- N'invente aucune valeur manquante : si une donnée manque, indique comment tu la traites et l'effet sur le classement.
- Le classement est une aide à la discussion : signale les cas où l'écart de score est trop faible pour départager deux districts.

FORMAT ATTENDU
- Tableau 1 : District | Scores normalisés par critère | Score pondéré | Rang.
- Tableau 2 (sensibilité) : District | Rang de base | Rang (a) | Rang (b) | Rang (c) | Stabilité.
- Sélection finale proposée, justifiée en 5 lignes maximum.
- Section « Limites et points à discuter » (5 puces maximum).`,
  cadre: {
    C: "L'objet et les contraintes rappellent que le classement sert une décision concrète, pas un exercice théorique.",
    A: "Les 6 étapes rendent la méthode transparente : contrôle des critères, normalisation, score, sensibilité, contraintes, limites.",
    D: "Critères, pondérations et valeurs viennent de vous : l'IA calcule, elle ne choisit pas ce qui compte.",
    R: "L'interdiction d'ajouter des critères ou de modifier les pondérations en silence garde la décision entre les mains de l'équipe.",
    E: "Le tableau de sensibilité montre d'un coup d'œil quels choix sont robustes et lesquels méritent un débat."
  },
  adapter: [
    "Remplacez les districts par des interventions (stratégies avancées, campagne de suivi, renforcement de la chaîne du froid) notées sur l'impact attendu, le coût et la faisabilité.",
    "Faites fixer les pondérations en atelier par le comité avant de lancer le prompt, puis collez le résultat retenu.",
    "Ajoutez des critères éliminatoires (par exemple, district exclu si aucune équipe ne peut y accéder) à appliquer avant le calcul des scores."
  ],
  pieges: [
    "Un critère dont le sens n'est pas inversé (« plus faible = plus prioritaire ») renverse le classement sans que rien ne paraisse anormal.",
    "Des critères corrélés (zéro-dose et couverture RR1) comptent deux fois le même phénomène : l'IA le signale rarement d'elle-même.",
    "Un critère d'accessibilité qui favorise les districts accessibles pénalise les populations les plus difficiles à atteindre : c'est un choix d'équité à assumer explicitement."
  ],
  verif: [
    "Recalculez à la main le score normalisé d'un critère et le score pondéré de 2 districts.",
    "Vérifiez que les pondérations de chaque scénario de sensibilité totalisent bien 100 %.",
    "Présentez les districts au rang instable comme des choix à débattre en comité, et non comme le verdict de l'IA."
  ],
  outils: "Un assistant capable d'exécuter des calculs (analyse de données dans ChatGPT ou Claude) ou Copilot dans Excel est fortement recommandé ; demandez le fichier ou le code produit pour pouvoir refaire le calcul.",
  lecon: "m2-iterer"
},

{
  id: "dec-theorie-changement",
  domaine: "decision",
  titre: "Construire une théorie du changement et un cadre de résultats SMART",
  resume: "Relier activités, produits, effets et impact d'un programme, avec indicateurs SMART, hypothèses et risques.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "6 h", avec: "2 h 30" },
  champs: [
    { id: "programme", label: "Programme et objectif", exemple: "Programme de réduction du nombre d'enfants zéro-dose dans 3 régions prioritaires d'un pays d'Afrique centrale (fictif), sur 3 ans", type: "texte" },
    { id: "probleme", label: "Problème et causes connues", exemple: "Environ 1 enfant sur 5 n'a reçu aucune dose de Penta dans les 3 régions selon les données administratives (estimation fictive, à confirmer). Causes relevées lors de la revue du PEV : formations sanitaires éloignées des campements et des quartiers informels, ruptures de stock fréquentes, horaires de vaccination incompatibles avec les activités des mères, faible implication des leaders communautaires, insécurité dans une partie d'une région.", type: "zone" },
    { id: "interventions", label: "Interventions prévues", exemple: "Stratégies avancées et mobiles adaptées aux déplacements des populations mobiles ; microplanification participative avec les communautés ; renforcement de la gestion des stocks ; horaires de vaccination élargis ; engagement des leaders religieux et des associations de femmes ; partenariats avec les acteurs humanitaires en zone d'insécurité.", type: "zone" },
    { id: "donneesdispo", label: "Données de référence disponibles", exemple: "Couvertures Penta1 et Penta3 administratives 2025 par district (DHIS2) ; enquête de couverture régionale fictive 2024 ; pas de données récentes sur les ruptures de stock au niveau des formations sanitaires.", type: "zone" },
    { id: "bailleur", label: "Destinataire et exigences du bailleur", exemple: "Proposition à un bailleur multilatéral : cadre de résultats limité à 12 indicateurs, désagrégation par sexe et par district exigée", type: "texte" }
  ],
  modele: `Tu es spécialiste de la planification stratégique et du suivi-évaluation des programmes de vaccination, expérimenté(e) dans la conception de théories du changement et de cadres de résultats pour des bailleurs internationaux.

CONTEXTE
Programme : {{programme}}
Destinataire et exigences : {{bailleur}}

TÂCHE
1. Formule l'énoncé de la théorie du changement en une phrase « Si… alors… parce que… ».
2. Construis la chaîne de résultats : activités → produits → effets intermédiaires → effet final → impact, en reliant chaque intervention aux causes du problème qu'elle traite. Signale toute cause sans intervention et toute intervention sans lien clair avec une cause.
3. Explicite les hypothèses de passage entre chaque niveau (ce qui doit être vrai pour que le niveau suivant se réalise) et les risques associés.
4. Propose un cadre de résultats avec des indicateurs SMART pour les niveaux produit, effet et impact : définition précise (numérateur et dénominateur), valeur de référence, cible, source de vérification, fréquence de collecte, désagrégation, responsable.
5. Indique pour chaque indicateur si la valeur de référence existe dans les données disponibles ou doit être établie.

PROBLÈME ET CAUSES
{{probleme}}

INTERVENTIONS PRÉVUES
{{interventions}}

DONNÉES DISPONIBLES
{{donneesdispo}}

RÈGLES
- N'invente aucune valeur de référence ni aucune cible chiffrée : écris « référence à établir » ou « cible à fixer avec le programme » quand l'information manque, et propose la méthode pour la fixer.
- Utilise une terminologie exacte : zéro-dose = enfant n'ayant reçu aucune dose de vaccin contenant la valence DTC, approché par l'absence de Penta1 ; taux d'abandon Penta1–Penta3 ; couverture Penta3.
- Limite le nombre d'indicateurs à ce qu'exige le bailleur et privilégie les indicateurs déjà collectés en routine (DHIS2) ou par enquête (EDS, MICS, enquêtes de couverture).
- Distingue ce qui relève du contrôle du programme (produits) de ce qui relève de son influence (effets, impact).
- Signale les hypothèses fragiles, notamment en zone d'insécurité ou pour les populations mobiles, et les désagrégations que les outils actuels ne permettent pas.

FORMAT ATTENDU
- Énoncé « Si… alors… parce que… » (3 lignes maximum).
- Chaîne de résultats sous forme de liste hiérarchique (impact > effets > produits > activités).
- Tableau des hypothèses et risques : Niveau | Hypothèse | Risque si elle ne se vérifie pas | Mesure de suivi.
- Cadre de résultats : Niveau | Indicateur | Définition (numérateur / dénominateur) | Référence | Cible | Source | Fréquence | Désagrégation | Responsable.`,
  cadre: {
    C: "Le rôle de spécialiste du suivi-évaluation et les exigences du bailleur calibrent le niveau de détail et le nombre d'indicateurs.",
    A: "La tâche va de l'énoncé de la théorie à la chaîne de résultats, puis aux hypothèses et au cadre de résultats : la logique précède les indicateurs.",
    D: "Les causes et interventions fournies obligent l'IA à vérifier la cohérence entre le problème et la réponse, au lieu de dérouler une théorie générique.",
    R: "L'interdiction d'inventer références et cibles est essentielle : un cadre de résultats rempli de chiffres plausibles mais faux engage le programme.",
    E: "Les tableaux reprennent les colonnes habituelles des bailleurs, ce qui facilite la reprise dans une proposition ou un plan de suivi-évaluation."
  },
  adapter: [
    "Remplacez le programme zéro-dose par l'introduction d'un nouveau vaccin ou le renforcement de la chaîne du froid, en adaptant causes et interventions.",
    "Collez le modèle de cadre logique imposé par votre bailleur et demandez à l'IA de s'y conformer exactement.",
    "Demandez en complément un schéma textuel (boîtes et flèches) de la chaîne de résultats, à reproduire dans PowerPoint."
  ],
  pieges: [
    "L'IA propose volontiers des cibles « raisonnables » (par exemple, réduire de moitié les zéro-dose en 3 ans) sans aucune base : toute cible doit venir du programme et de ses données.",
    "Les indicateurs d'effet sont souvent confondus avec des indicateurs de produit : un nombre de séances réalisées n'est pas un résultat pour les enfants.",
    "La désagrégation par sexe est rarement disponible dans les rapports de routine : un indicateur qui l'exige peut être impossible à renseigner sans adapter les outils de collecte."
  ],
  verif: [
    "Pour chaque indicateur, vérifiez que le numérateur, le dénominateur et la source existent réellement dans votre système d'information.",
    "Contrôlez que chaque cause identifiée est traitée par au moins une intervention, et que chaque intervention répond à une cause.",
    "Faites valider références et cibles par l'équipe de suivi-évaluation du PEV avant soumission."
  ],
  outils: "Un assistant généraliste convient ; travaillez en plusieurs tours (théorie, puis indicateurs). Pour vous aligner sur un plan stratégique existant, chargez-le dans un outil qui cite ses sources, comme NotebookLM.",
  lecon: "m2-cadre"
},

{
  id: "dec-premortem",
  domaine: "decision",
  titre: "Conduire un pré-mortem et une matrice des risques pour une campagne",
  resume: "Imaginer l'échec d'une campagne ou d'une introduction de vaccin pour en tirer risques, parades et signaux d'alerte.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "3 h", avec: "1 h" },
  champs: [
    { id: "projet", label: "Projet concerné", exemple: "Introduction du vaccin antipaludique dans la vaccination de routine de 12 districts (pays fictif d'Afrique de l'Ouest), à partir de mars 2027", type: "texte" },
    { id: "calendrier", label: "Calendrier et étapes clés", exemple: "Formation des agents en janvier ; réception des vaccins en février ; lancement officiel en mars ; première revue à 6 mois", type: "texte" },
    { id: "contexte", label: "Contexte et contraintes connus", exemple: "Calendrier à 4 doses, dont certaines à des âges sans autre contact vaccinal prévu dans le calendrier national ; chaîne du froid saturée dans 3 districts ; rumeurs sur les réseaux sociaux à propos des « essais » de vaccins ; changement récent de responsable du PEV ; saison des pluies de juin à octobre ; zones d'insécurité dans 2 districts.", type: "zone" },
    { id: "ressources", label: "Ressources et parties prenantes", exemple: "Équipe centrale du PEV, 12 équipes cadres de district, UNICEF (logistique), OMS (appui technique), ONG partenaires pour la mobilisation communautaire, radios communautaires", type: "texte" }
  ],
  modele: `Tu es expert(e) en gestion de programmes de vaccination et en gestion des risques, expérimenté(e) dans l'introduction de nouveaux vaccins et l'organisation de campagnes en Afrique.

CONTEXTE
Projet : {{projet}}
Calendrier et étapes clés : {{calendrier}}
Ressources et parties prenantes : {{ressources}}

TÂCHE
1. Pré-mortem : nous sommes 12 mois après le lancement et le projet est un échec manifeste. Rédige en 10 lignes le récit plausible de cet échec, en t'appuyant sur le contexte fourni.
2. À partir de ce récit, identifie 10 à 12 causes d'échec possibles, réparties entre les catégories : approvisionnement et chaîne du froid ; ressources humaines et formation ; données et suivi ; demande et confiance communautaire ; gouvernance et coordination ; financement ; sécurité et accès ; équité (populations mobiles, déplacées, urbaines pauvres, obstacles liés au genre).
3. Pour chaque risque, estime la probabilité et l'impact (faible = 1, moyen = 2, élevé = 3) en justifiant brièvement, puis calcule la criticité (probabilité × impact).
4. Pour chaque risque, propose une mesure d'atténuation concrète, un responsable (fonction, pas de nom), une échéance située dans le calendrier et un signal d'alerte observable indiquant que le risque se matérialise.
5. Identifie les 3 risques à traiter en priorité avant le lancement.

CONTEXTE ET CONTRAINTES
{{contexte}}

RÈGLES
- Reste ancré(e) dans le contexte fourni ; distingue les risques tirés du contexte de ceux que tu ajoutes à partir de l'expérience générale.
- N'invente aucune statistique, aucun incident passé, aucune référence ; ne cite aucune donnée sur l'efficacité ou la sécurité du vaccin.
- Les signaux d'alerte doivent être mesurables avec les outils existants (DHIS2, rapports de stock, écoute sociale, supervision).
- Les estimations de probabilité et d'impact sont des jugements à discuter en équipe : présente-les comme tels.

FORMAT ATTENDU
- Le récit du pré-mortem (10 lignes maximum).
- Matrice des risques : N° | Catégorie | Risque | Probabilité | Impact | Criticité | Mesure d'atténuation | Responsable | Échéance | Signal d'alerte | Origine (contexte fourni / expérience générale).
- Les 3 priorités avant le lancement, en 3 puces.`,
  cadre: {
    C: "Le rôle d'expert en gestion des risques et le calendrier situent chaque risque par rapport aux étapes réelles du projet.",
    A: "Le récit d'échec imaginé libère l'analyse de l'optimisme des planificateurs, puis la matrice transforme ce récit en mesures concrètes.",
    D: "Les contraintes connues (chaîne du froid, rumeurs, insécurité) donnent des points d'ancrage et réduisent les risques génériques.",
    R: "Les règles imposent des signaux d'alerte mesurables et la traçabilité de l'origine de chaque risque.",
    E: "La matrice avec responsables et échéances est directement utilisable en atelier de planification ou dans le plan d'introduction."
  },
  adapter: [
    "Appliquez le même prompt à une campagne de suivi rougeole-rubéole ou à l'introduction du vaccin contre le papillomavirus humain (HPV) en milieu scolaire, en adaptant le contexte.",
    "Utilisez le récit d'échec comme support d'atelier : projetez-le, demandez aux participants ce qui manque, puis complétez la matrice avec eux.",
    "Relancez le pré-mortem à mi-parcours avec les données réelles des premiers mois pour actualiser probabilités et signaux d'alerte."
  ],
  pieges: [
    "L'IA produit facilement des risques génériques valables pour n'importe quel projet : exigez que chaque risque soit relié à un élément du contexte ou marqué comme générique.",
    "Les mesures d'atténuation proposées dépassent souvent les ressources disponibles (formations supplémentaires, recrutements) : testez leur coût et leur faisabilité.",
    "Les risques liés à l'équité et au genre (temps et autonomie des mères, accès des populations mobiles) sont souvent oubliés ou relégués en fin de liste."
  ],
  verif: [
    "Vérifiez que chaque signal d'alerte peut être suivi avec vos outils actuels, et à quelle fréquence.",
    "Recalculez 2 ou 3 criticités et vérifiez la cohérence des priorités retenues.",
    "Soumettez la matrice aux équipes logistique, communication et district : les probabilités doivent refléter leur jugement, pas celui de l'IA."
  ],
  outils: "Un assistant généraliste convient. Pour un atelier, préparez le récit et la matrice à l'avance, puis complétez-les avec l'équipe ; la matrice s'exporte facilement vers Excel.",
  lecon: "m2-avance"
},

{
  id: "dec-avocat-diable",
  domaine: "decision",
  titre: "Soumettre un document stratégique à une revue « avocat du diable »",
  resume: "Repérer hypothèses fragiles, incohérences, angles morts d'équité et questions des bailleurs, avec des pistes d'amélioration.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "3 h", avec: "1 h" },
  champs: [
    { id: "document", label: "Document à examiner", exemple: "Projet de stratégie nationale de vaccination 2027–2031 (version 2, 45 pages), pays fictif d'Afrique de l'Est", type: "texte" },
    { id: "extraits", label: "Texte ou extraits clés (copier-coller)", exemple: "Objectif général : atteindre 95 % de couverture Penta3 dans tous les districts d'ici 2031.\nStratégie 1 : renforcer la vaccination de routine par la formation de tous les agents de santé.\nStratégie 2 : réduire de moitié le nombre d'enfants zéro-dose grâce à la sensibilisation communautaire.\nFinancement : la part de l'État dans l'achat des vaccins passera progressivement à 100 %.\nSuivi : revue annuelle par le comité de pilotage.", type: "zone", aide: "Collez le résumé exécutif et les sections clés si l'outil limite la longueur. Retirez les éléments confidentiels non nécessaires à la revue." },
    { id: "contexte", label: "Contexte national connu", exemple: "Couverture Penta3 nationale d'environ 78 % selon les données administratives (fictif) ; fortes disparités entre régions ; zones de conflit dans le nord ; dette publique élevée ; pays en phase de transition accélérée du soutien de Gavi", type: "zone" },
    { id: "lecteurs", label: "Lecteurs qui examineront le document", exemple: "Comité d'examen indépendant de Gavi, Banque mondiale, ministère des Finances, partenaires techniques (OMS, UNICEF)", type: "texte" }
  ],
  modele: `Tu es un(e) relecteur(trice) exigeant(e) et indépendant(e), habitué(e) aux comités d'examen de stratégies de vaccination, spécialiste du financement de la santé et de l'équité. Ton rôle est celui d'avocat du diable : trouver les faiblesses avant que d'autres ne les trouvent.

CONTEXTE
Document examiné : {{document}}
Contexte national connu : {{contexte}}
Lecteurs qui l'examineront : {{lecteurs}}

TÂCHE
1. Hypothèses non étayées : relève les affirmations, objectifs ou cibles qui ne reposent sur aucune donnée, analyse ou justification visible dans le texte.
2. Incohérences : signale les écarts entre problèmes, objectifs, stratégies, ressources et dispositif de suivi (objectif sans stratégie, stratégie sans budget, cible incompatible avec le point de départ).
3. Angles morts d'équité : examine la prise en compte des enfants zéro-dose, des zones de conflit, des populations nomades, déplacées et urbaines pauvres, des obstacles liés au genre et des langues locales.
4. Questions des lecteurs : formule les 8 questions les plus probables et les plus difficiles, réparties entre les lecteurs indiqués.
5. Améliorations : pour chaque faiblesse majeure, propose une amélioration concrète et réaliste (reformulation, analyse à ajouter, donnée à produire).
6. Termine par les 3 forces réelles du document, pour équilibrer la revue.

TEXTE À EXAMINER
{{extraits}}

RÈGLES
- Sois franc(he) et précis(e), sans complaisance ni agressivité ; cite le passage concerné pour chaque critique.
- Critique uniquement ce qui figure dans le texte fourni ; si une section n'est pas fournie, dis que tu ne peux pas la juger au lieu de la supposer absente.
- N'invente aucune exigence de bailleur, aucune règle de financement, aucune statistique : formule les attentes des bailleurs comme des questions probables, pas comme des règles.
- Classe chaque critique par gravité : bloquante, importante, mineure.

FORMAT ATTENDU
- Tableau des critiques : N° | Passage cité | Problème | Type (hypothèse non étayée, incohérence, angle mort d'équité, autre) | Gravité | Amélioration proposée.
- Les 8 questions des lecteurs, regroupées par lecteur, avec pour chacune l'élément de réponse qui manque dans le document.
- Les 3 forces, en 3 puces.
- Longueur : 2 pages maximum.`,
  cadre: {
    C: "Le rôle explicite d'avocat du diable autorise l'IA à critiquer, contre sa tendance naturelle à approuver le texte qu'on lui soumet.",
    A: "Les 6 étapes couvrent les angles d'un comité d'examen : hypothèses, cohérence, équité, questions des lecteurs, améliorations, forces.",
    D: "Les extraits et le contexte national permettent de juger le réalisme des cibles par rapport au point de départ.",
    R: "L'obligation de citer le passage et l'interdiction d'inventer des exigences de bailleurs rendent chaque critique vérifiable.",
    E: "Le tableau classé par gravité se transforme directement en plan de révision du document."
  },
  adapter: [
    "Faites jouer successivement à l'IA le rôle de chaque lecteur (Gavi, ministère des Finances, société civile) dans des messages séparés pour approfondir chaque point de vue.",
    "Appliquez la même revue à une demande de financement, à un plan d'introduction de vaccin ou à une note conceptuelle.",
    "Après révision, soumettez la nouvelle version en demandant uniquement si les critiques bloquantes ont été levées."
  ],
  pieges: [
    "L'IA peut prêter aux bailleurs des exigences précises (seuils, règles d'éligibilité) qu'elle invente : vérifiez-les dans les lignes directrices officielles en vigueur.",
    "La revue peut rester superficielle (« renforcer le suivi-évaluation ») : exigez le passage cité et une amélioration concrète pour chaque critique.",
    "Sans consigne, l'IA critique aussi des sections qu'elle n'a pas lues en les supposant absentes : vérifiez qu'elle ne juge que le texte fourni."
  ],
  verif: [
    "Contrôlez que chaque passage cité figure mot pour mot dans votre document.",
    "Confrontez les questions attribuées aux bailleurs à leurs lignes directrices de candidature et aux retours d'examens antérieurs dont vous disposez.",
    "Faites relire les critiques jugées bloquantes par un collègue qui n'a pas participé à la rédaction."
  ],
  outils: "Préférez un outil qui accepte les longs documents (Claude, NotebookLM, Copilot sur un document Word). Un projet de stratégie non publié reste un document interne : utilisez un outil institutionnel ou retirez les éléments sensibles.",
  lecon: "m2-avance"
},

// ============================================================
// Domaine : communication — Communication stratégique
// ============================================================

{
  id: "com-note-ministre",
  domaine: "communication",
  titre: "Rédiger une note de synthèse d'une page pour un ministre",
  resume: "Produire une note BLUF : conclusion d'abord, décision attendue, 3 arguments, risques de l'inaction, prochaines étapes.",
  niveau: "Essentiel",
  donnees: "N2",
  gain: { sans: "2 h", avec: "45 min" },
  champs: [
    { id: "sujet", label: "Sujet de la note", exemple: "Mobilisation de la contrepartie nationale pour l'achat des vaccins en 2027", type: "texte" },
    { id: "decision", label: "Décision attendue du ministre", exemple: "Saisir le ministre des Finances pour inscrire la ligne d'achat des vaccins dans la loi de finances 2027 et obtenir un premier décaissement avant juin", type: "texte" },
    { id: "elements", label: "Éléments factuels disponibles", exemple: "Le cofinancement dû pour 2026 n'a été versé qu'en partie ([montant] restant dû selon le programme). Risque de rupture de vaccin pentavalent au second semestre 2027 si les commandes ne sont pas lancées d'ici mars. Couverture Penta3 nationale stable autour de 80 % (données administratives 2025, fictives). Deux flambées de rougeole en 2026 ont mobilisé des fonds d'urgence.", type: "zone", aide: "N'incluez des montants non publiés que dans un outil institutionnel autorisé ; sinon, remplacez-les par [montant] et complétez hors de l'outil." },
    { id: "ministre", label: "Destinataire et contexte politique", exemple: "Ministre de la Santé, nommé il y a 3 mois, très attentif à l'équité entre régions ; Conseil des ministres dans 10 jours", type: "texte" },
    { id: "emetteur", label: "Émetteur", exemple: "Direction de la prévention, programme élargi de vaccination", type: "texte" }
  ],
  modele: `Tu es conseiller(ère) technique en cabinet ministériel, spécialiste de la santé publique et de la rédaction de notes de synthèse pour des ministres africains.

CONTEXTE
Sujet : {{sujet}}
Destinataire et contexte politique : {{ministre}}
Émetteur : {{emetteur}}
Décision attendue : {{decision}}

TÂCHE
1. Rédige une note d'une page selon le principe BLUF (conclusion d'abord) : la première phrase dit ce que le ministre doit décider et pourquoi maintenant.
2. Développe 3 arguments, chacun appuyé sur un élément factuel fourni.
3. Expose les risques de l'inaction (sanitaires, financiers, politiques), sans dramatisation.
4. Propose 3 prochaines étapes, chacune avec un responsable (fonction) et une échéance.
5. Ajoute, sous la note, la liste des faits à vérifier avant transmission.

ÉLÉMENTS FACTUELS
{{elements}}

RÈGLES
- Utilise uniquement les éléments fournis ; n'invente aucun chiffre, montant, date ou référence. Si un élément manque pour un argument, écris [à compléter] à l'endroit voulu.
- Reste factuel(le) et respectueux(se) de la décision du ministre ; ne prends pas position sur des questions politiques étrangères au sujet.
- Phrases courtes, vocabulaire administratif sobre ; développe chaque sigle à sa première occurrence.
- Ton direct, respectueux, orienté décision.

FORMAT ATTENDU
- En-tête : Objet | Destinataire | Émetteur | Date [à compléter].
- Bloc « Décision attendue » (2 phrases maximum).
- Trois arguments numérotés (3 lignes maximum chacun).
- Risques de l'inaction (3 puces).
- Prochaines étapes (tableau : Étape | Responsable | Échéance).
- Longueur : 350 mots maximum pour la note elle-même, hors liste de vérification.`,
  cadre: {
    C: "Le rôle de conseiller de cabinet et le contexte politique ajustent le ton et le niveau de détail à un ministre pressé.",
    A: "Le principe BLUF place la décision en première phrase : si le ministre ne lit que celle-ci, l'essentiel est passé.",
    D: "Les éléments factuels fournis sont la seule matière autorisée, ce qui évite les chiffres plausibles mais invérifiables.",
    R: "Les mentions [à compléter] rendent les trous visibles au lieu de les combler par des inventions.",
    E: "La limite de 350 mots et la structure fixe imposent la concision attendue d'une note ministérielle."
  },
  adapter: [
    "Pour un ministre des Finances, remplacez les arguments sanitaires par des arguments de coûts évités, de prévisibilité budgétaire et d'engagements de cofinancement.",
    "Demandez une variante en anglais ou en portugais pour un pays anglophone ou lusophone, en conservant la structure.",
    "Ajoutez une annexe d'une demi-page d'éléments de langage pour l'intervention du ministre en Conseil des ministres."
  ],
  pieges: [
    "L'IA allonge spontanément les notes : au-delà d'une page, la note ne sera pas lue jusqu'au bout.",
    "Elle peut ajouter un chiffre « pour renforcer l'argument » (coût d'une épidémie, nombre d'enfants à risque) absent de vos éléments : supprimez-le ou sourcez-le.",
    "La décision attendue est parfois diluée en fin de note ou formulée de façon vague (« appuyer le programme ») au lieu d'une action précise, datée et attribuée."
  ],
  verif: [
    "Vérifiez que la première phrase énonce une décision précise, datée et attribuée.",
    "Pointez chaque chiffre de la note dans vos éléments factuels ou dans la source du programme.",
    "Faites relire la note par le responsable du programme et, si elle engage un budget, par le service financier."
  ],
  outils: "Une note ministérielle contient souvent des informations politiques ou budgétaires sensibles (niveau N2) : utilisez l'outil institutionnel autorisé par votre organisation, ou remplacez les montants par [montant] et complétez hors de l'outil.",
  lecon: "m5-donnees"
},

{
  id: "com-plaidoyer-publics",
  domaine: "communication",
  titre: "Décliner un message de plaidoyer pour trois publics",
  resume: "Adapter un plaidoyer aux Finances, aux parlementaires et aux leaders religieux et communautaires : arguments, preuves, demande.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "4 h", avec: "1 h 30" },
  champs: [
    { id: "cause", label: "Objet du plaidoyer", exemple: "Augmenter et sécuriser le financement national de la vaccination de routine", type: "texte" },
    { id: "porteur", label: "Porteur du plaidoyer", exemple: "Coalition de la société civile pour la vaccination, avec l'appui technique du PEV", type: "texte" },
    { id: "message", label: "Message central", exemple: "Chaque enfant non vacciné reste exposé à des maladies évitables ; financer la vaccination de façon régulière protège les familles et limite les dépenses d'urgence liées aux épidémies.", type: "texte" },
    { id: "preuves", label: "Données et preuves disponibles", exemple: "Couverture Penta3 nationale administrative 2025 : 79 % (fictif) ; 3 régions sous 65 % (fictif) ; dépenses de riposte à la rougeole en 2026 : montant figurant dans le rapport du programme ; ligne budgétaire vaccins exécutée à 60 % en 2025 (fictif) ; étude nationale des coûts du programme en cours de validation.", type: "zone", aide: "Indiquez la source de chaque donnée. Les chiffres de négociation budgétaire non publiés relèvent du niveau N2." },
    { id: "contexte", label: "Contexte national", exemple: "Préparation de la loi de finances 2027 ; session parlementaire en novembre ; forte influence des leaders religieux dans les régions du nord ; rumeurs récentes sur la vaccination dans deux régions", type: "texte" }
  ],
  modele: `Tu es spécialiste du plaidoyer en santé publique et de la communication stratégique, expérimenté(e) auprès des ministères des Finances, des parlements et des leaders religieux et communautaires en Afrique.

CONTEXTE
Objet du plaidoyer : {{cause}}
Porteur : {{porteur}}
Message central : {{message}}
Contexte national : {{contexte}}

TÂCHE
1. Pour chacun des 3 publics suivants : (a) ministère des Finances et du Budget, (b) parlementaires (commissions santé et finances), (c) leaders religieux et communautaires, analyse ce qui compte pour lui, ses objections probables et le registre qui le convaincra.
2. Rédige pour chaque public : 3 arguments principaux ; les preuves à fournir, en n'utilisant que les données ci-dessous ou en indiquant la preuve à produire ; une demande précise (qui fait quoi, et quand) ; le ton recommandé.
3. Propose pour chaque public un message clé de 2 phrases et une réponse à son objection la plus probable.
4. Vérifie la cohérence : le cœur du message et les chiffres doivent être identiques pour les 3 publics ; seuls l'angle et le registre changent.

DONNÉES ET PREUVES DISPONIBLES
{{preuves}}

RÈGLES
- N'invente aucune statistique, aucune étude, aucun retour sur investissement chiffré, aucune citation religieuse ou juridique. Si une preuve renforcerait un argument mais n'est pas fournie, écris « preuve à produire : … ».
- Signale les données non validées (par exemple une étude en cours de validation) et ne les présente pas comme des faits établis.
- Pour les leaders religieux et communautaires, fonde les arguments sur la protection de l'enfant et de la communauté, sans prêter de position à une religion, et recommande de construire le message avec eux.
- Respecte chaque public : ni condescendance ni culpabilisation.

FORMAT ATTENDU
- Tableau : Public | Ce qui compte pour lui | Objections probables | 3 arguments | Preuves à fournir | Demande précise | Ton.
- Pour chaque public : message clé (2 phrases) et réponse à l'objection principale (3 phrases maximum).
- Liste finale des « preuves à produire » avant toute utilisation.`,
  cadre: {
    C: "Le rôle de spécialiste du plaidoyer et le contexte national (calendrier budgétaire, session parlementaire) relient chaque message à une fenêtre d'opportunité réelle.",
    A: "L'analyse de chaque public précède la rédaction : on part de ses intérêts et de ses objections, pas de ce que l'on veut dire.",
    D: "Les preuves sont limitées à celles que vous fournissez, ce qui empêche l'IA de produire des retours sur investissement ou des études invérifiables.",
    R: "Les règles interdisent citations religieuses et chiffres inventés, et imposent de signaler les données non validées.",
    E: "Le tableau comparatif et la liste des preuves à produire permettent de vérifier la cohérence entre publics avant toute diffusion."
  },
  adapter: [
    "Ajoutez un quatrième public (partenaires techniques et financiers, médias, associations de femmes) en reprenant la même grille.",
    "Demandez une version orale de 2 minutes pour une audition parlementaire, avec 3 chiffres au maximum.",
    "Pour les leaders communautaires, faites ensuite traduire le message clé dans la langue locale par un locuteur natif, avec retraduction de contrôle."
  ],
  pieges: [
    "L'IA cite volontiers un retour sur investissement de la vaccination ou une étude internationale sans source exacte : toute preuve doit être retrouvée dans le document d'origine.",
    "Elle peut attribuer des positions à une religion ou employer des références religieuses inexactes, ce qui risque de braquer les leaders que l'on cherche à convaincre.",
    "Les chiffres peuvent varier d'un public à l'autre (arrondis, années différentes) : une incohérence repérée par un parlementaire affaiblit tout le plaidoyer."
  ],
  verif: [
    "Vérifiez que chaque chiffre apparaît à l'identique dans les 3 déclinaisons et dans votre source.",
    "Faites relire la version destinée aux leaders religieux et communautaires par un relais communautaire ou un responsable religieux de confiance.",
    "Contrôlez que chaque demande est précise, réaliste et adressée au bon acteur : une ligne budgétaire relève des Finances et du Parlement, pas des leaders communautaires."
  ],
  outils: "Un assistant généraliste convient. Pour retrouver les preuves dans vos rapports, chargez-les dans un outil qui cite ses sources (NotebookLM, Copilot sur vos documents) et vérifiez chaque citation.",
  lecon: "m4-references"
},

{
  id: "com-storyline",
  domaine: "communication",
  titre: "Construire la storyline d'une présentation exécutive",
  resume: "Structurer 10 diapositives au plus, chacune avec un titre-affirmation, un message clé, un visuel et les données à vérifier.",
  niveau: "Essentiel",
  donnees: "N1",
  gain: { sans: "3 h", avec: "1 h" },
  champs: [
    { id: "objet", label: "Objet de la présentation", exemple: "Bilan à mi-parcours du plan de relance de la vaccination de routine et demandes pour l'année suivante", type: "texte" },
    { id: "auditoire", label: "Auditoire et durée", exemple: "Comité de pilotage présidé par le Secrétaire général du ministère de la Santé, avec les partenaires ; 15 minutes de présentation, 30 minutes de discussion", type: "texte" },
    { id: "message", label: "Message principal souhaité", exemple: "Les progrès sont réels mais concentrés dans les régions faciles d'accès ; il faut réorienter une partie des moyens vers les 3 régions qui concentrent les zéro-dose.", type: "texte" },
    { id: "contenu", label: "Éléments disponibles (résultats, chiffres, faits)", exemple: "Couverture Penta3 passée de 74 % à 81 % en 18 mois (données administratives, fictives) ; abandon Penta1–Penta3 en baisse dans 7 régions sur 10 ; nombre estimé d'enfants zéro-dose en hausse dans les 3 régions touchées par l'insécurité ; 2 ruptures de stock nationales de vaccin RR ; budget exécuté à 72 % ; enquête de satisfaction des mères réalisée dans 2 régions.", type: "zone" },
    { id: "decision", label: "Décisions attendues de l'auditoire", exemple: "Valider la réallocation des moyens et l'élaboration d'un plan spécifique pour les zones d'insécurité", type: "texte" }
  ],
  modele: `Tu es consultant(e) senior en communication stratégique, spécialiste des présentations exécutives pour des instances de décision en santé publique.

CONTEXTE
Objet : {{objet}}
Auditoire et durée : {{auditoire}}
Message principal souhaité : {{message}}
Décisions attendues : {{decision}}

TÂCHE
1. Propose une ligne narrative en 3 temps (situation, enjeu, réponse proposée) et résume-la en 3 phrases.
2. Construis la storyline de 10 diapositives au maximum. Pour chaque diapositive : un titre-affirmation (une phrase complète qui énonce la conclusion de la diapositive, pas un thème), le message clé à dire à l'oral, le visuel suggéré (type de graphique ou de schéma et données représentées) et les données à vérifier avant de produire la diapositive.
3. Rends les décisions attendues explicites, au début et à la fin.
4. Prévois une diapositive de réserve (annexe) pour les questions difficiles probables, et liste ces questions.
5. Vérifie que la lecture des seuls titres raconte toute l'histoire ; si ce n'est pas le cas, corrige.

ÉLÉMENTS DISPONIBLES
{{contenu}}

RÈGLES
- N'utilise que les éléments fournis ; n'invente aucun chiffre, aucune tendance, aucun résultat. Si un visuel nécessite une donnée absente, écris « donnée à fournir ».
- Un seul message par diapositive ; 3 chiffres clés au maximum par diapositive.
- Si un élément fourni contredit ou nuance le message principal souhaité, signale-le au lieu de l'omettre.
- Adapte le nombre de diapositives à la durée : compte environ 1 à 2 minutes par diapositive.

FORMAT ATTENDU
- La ligne narrative (3 phrases).
- Un tableau : N° | Titre-affirmation | Message clé (oral) | Visuel suggéré | Données à vérifier.
- La liste des questions difficiles probables pour l'annexe.`,
  cadre: {
    C: "L'auditoire, la durée et les décisions attendues déterminent le nombre de diapositives et le niveau de détail.",
    A: "Les titres-affirmations obligent à formuler une conclusion par diapositive : la présentation se comprend en ne lisant que les titres.",
    D: "Les éléments disponibles bornent le contenu : l'IA structure vos résultats au lieu d'en produire de nouveaux.",
    R: "L'obligation de signaler les éléments qui nuancent votre message protège contre une présentation trop belle pour être crédible.",
    E: "Le tableau par diapositive sert à la fois de plan, de script oral et de liste de vérification des données."
  },
  adapter: [
    "Pour une présentation à un bailleur, ajoutez une diapositive sur l'utilisation des fonds et les résultats obtenus par rapport aux engagements.",
    "Demandez ensuite les notes du présentateur (150 mots par diapositive) pour préparer l'oral.",
    "Dans Copilot pour PowerPoint, partez de la storyline validée pour générer les diapositives, puis remplacez chaque graphique par vos données vérifiées."
  ],
  pieges: [
    "Les titres proposés sont souvent des thèmes (« Couverture vaccinale ») plutôt que des affirmations (« La couverture progresse, mais pas là où vivent les enfants zéro-dose »).",
    "L'IA peut omettre les éléments qui contredisent votre message (hausse des zéro-dose dans les zones d'insécurité) pour rendre l'histoire plus fluide.",
    "Les visuels suggérés supposent parfois des données que vous n'avez pas, ou des comparaisons trompeuses (axes tronqués, dénominateurs différents)."
  ],
  verif: [
    "Lisez uniquement les titres à voix haute : l'histoire et la décision attendue doivent être compréhensibles.",
    "Pointez chaque chiffre de la storyline dans vos éléments sources.",
    "Testez la storyline auprès d'un collègue qui ne connaît pas le dossier : il doit pouvoir redire la décision attendue en une phrase."
  ],
  outils: "Tout assistant généraliste convient pour la storyline. Les outils qui génèrent des diapositives (Copilot dans PowerPoint, par exemple) sont utiles ensuite, mais vérifiez chaque graphique : ils peuvent insérer des chiffres d'illustration.",
  lecon: "m2-outils"
},

{
  id: "com-campagne-rumeurs",
  domaine: "communication",
  titre: "Préparer les messages clés et la FAQ d'une campagne face aux rumeurs",
  resume: "Produire des messages simples et empathiques et des réponses aux rumeurs fondées uniquement sur des faits validés.",
  niveau: "Intermédiaire",
  donnees: "N1",
  gain: { sans: "6 h", avec: "2 h" },
  champs: [
    { id: "campagne", label: "Campagne concernée", exemple: "Campagne de suivi contre la rougeole et la rubéole, enfants de 9 à 59 mois, 10 jours en novembre, région fictive de Koubé", type: "texte" },
    { id: "faits", label: "Faits validés par le programme", exemple: "Le vaccin RR est gratuit. Il est administré par injection dans les postes fixes et par des équipes mobiles. Tous les enfants de 9 à 59 mois sont concernés, même s'ils ont déjà été vaccinés. Dates : du 3 au 12 novembre. Effets indésirables possibles et conduite à tenir : [coller la fiche validée par le programme]. Numéro vert : [à compléter].", type: "zone", aide: "Collez uniquement des informations validées par le programme ou les autorités sanitaires ; l'IA ne doit rien y ajouter." },
    { id: "rumeurs", label: "Rumeurs et préoccupations relevées", exemple: "« Le vaccin rend les enfants stériles. »\n« La campagne sert à tester un nouveau produit sur nos enfants. »\n« Mon enfant a déjà eu la rougeole, il n'a pas besoin du vaccin. »\n« On vaccine trop souvent, c'est dangereux. »\nPréoccupation : les mères ne peuvent pas quitter le marché pendant les heures d'ouverture des postes.", type: "zone", aide: "Rumeurs agrégées issues de l'écoute sociale ou des relais, sans nom ni détail permettant d'identifier une personne." },
    { id: "publics", label: "Publics, langues et relais", exemple: "Parents (mères et pères), grands-mères, leaders religieux, enseignants ; langues : français, haoussa, fulfulde ; relais : radios communautaires, agents de santé communautaires, crieurs publics, groupes WhatsApp de quartier", type: "texte" },
    { id: "contexte", label: "Contexte local", exemple: "Campagne précédente perturbée par une rumeur sur la stérilité ; méfiance envers les équipes venues de la capitale ; grand marché hebdomadaire le jeudi", type: "texte" }
  ],
  modele: `Tu es spécialiste de la communication pour le changement social et comportemental appliquée à la vaccination, et de la réponse aux rumeurs et à l'hésitation vaccinale en Afrique.

CONTEXTE
Campagne : {{campagne}}
Publics, langues et relais : {{publics}}
Contexte local : {{contexte}}

TÂCHE
1. Rédige 5 messages clés courts (25 mots maximum chacun) : quoi, pour qui, quand, où, pourquoi, en langage simple.
2. Rédige une FAQ de 10 questions-réponses couvrant les questions pratiques et les préoccupations des parents.
3. Pour chaque rumeur ou préoccupation listée, propose une réponse en 3 temps : reconnaître l'inquiétude avec empathie ; donner l'information exacte tirée des faits validés ; proposer une action concrète (où s'informer, à qui parler). Évite de reprendre la rumeur mot pour mot, pour ne pas l'amplifier.
4. Adapte les messages aux relais : une version de 30 secondes pour la radio communautaire, des points à dire en porte-à-porte pour les agents de santé communautaires, une version de 3 lignes pour WhatsApp.
5. Liste les points à faire valider par le programme avant diffusion, et ceux pour lesquels un fait validé manque.

FAITS VALIDÉS (seule source autorisée)
{{faits}}

RUMEURS ET PRÉOCCUPATIONS RELEVÉES
{{rumeurs}}

RÈGLES
- Utilise uniquement les faits validés ci-dessus. N'ajoute aucune information médicale, aucun chiffre, aucune donnée de sécurité ou d'efficacité qui n'y figure pas. Si une réponse nécessite un fait absent, écris [fait à valider par le programme].
- Langage simple (phrases de 15 mots maximum, aucun terme technique non expliqué), ton respectueux et empathique ; ne ridiculise ni ne culpabilise jamais les parents.
- N'attribue aucune rumeur à une communauté, une religion ou une ethnie.
- Ne propose pas de traduction en langue locale : rédige en français simple, facile à traduire, et signale les expressions délicates à traduire.
- Tout le contenu est un projet soumis à la validation obligatoire du programme de vaccination.

FORMAT ATTENDU
- Messages clés : liste numérotée.
- FAQ : tableau Question | Réponse (40 mots maximum par réponse).
- Réponses aux rumeurs : tableau Rumeur | Reconnaître | Informer | Agir.
- Déclinaisons par relais (radio, agents de santé communautaires, WhatsApp).
- Liste « À valider avant diffusion ».`,
  cadre: {
    C: "Le rôle de spécialiste du changement social et comportemental et le contexte local orientent vers l'écoute plutôt que vers la leçon de morale.",
    A: "Les étapes couvrent toute la chaîne : messages clés, FAQ, réponses aux rumeurs, déclinaisons par relais, points à valider.",
    D: "Les faits validés sont déclarés seule source autorisée : l'IA ne peut pas compléter une réponse médicale de mémoire.",
    R: "La mention [fait à valider par le programme] rend les trous visibles, et l'interdiction de traduire évite de diffuser des traductions approximatives.",
    E: "La réponse en trois temps (reconnaître, informer, agir) donne une structure empathique, courte et facile à utiliser par les relais."
  },
  adapter: [
    "Pour l'introduction d'un vaccin (HPV, antipaludique), ajoutez les questions propres à ce vaccin et faites valider chaque réponse par le programme.",
    "Demandez une version destinée aux agents de santé eux-mêmes, qui peuvent aussi avoir des doutes, sur un ton de pair à pair.",
    "Pendant la campagne, collez chaque jour les nouvelles rumeurs relevées dans la même conversation et demandez uniquement les réponses nouvelles."
  ],
  pieges: [
    "L'IA complète volontiers les réponses par des faits médicaux de mémoire (fréquence des effets indésirables, composition du vaccin) : tout ce qui n'est pas dans vos faits validés doit être retiré ou validé.",
    "Les réponses trop longues ou techniques échouent : une réponse de FAQ doit pouvoir être dite en 20 secondes par un relais communautaire.",
    "Une réponse qui répète la rumeur en titre ou qui se moque de la croyance peut renforcer la rumeur au lieu de la désamorcer."
  ],
  verif: [
    "Surlignez chaque affirmation médicale et retrouvez-la dans vos faits validés.",
    "Faites tester les messages auprès de quelques parents et relais, puis faites-les traduire par des locuteurs natifs, avec retraduction vers le français.",
    "Obtenez la validation écrite du programme de vaccination avant toute diffusion."
  ],
  outils: "Un assistant généraliste convient pour les projets de messages. Les traductions automatiques en langues locales sont souvent peu fiables : faites-les réaliser ou vérifier par des locuteurs natifs.",
  lecon: "m4-hallucinations"
},

{
  id: "com-declinaisons",
  domaine: "communication",
  titre: "Décliner un contenu technique en plusieurs formats de diffusion",
  resume: "Tirer d'un rapport un résumé exécutif, un post LinkedIn, un message WhatsApp et un script radio aux chiffres cohérents.",
  niveau: "Essentiel",
  donnees: "N0",
  gain: { sans: "3 h", avec: "1 h" },
  champs: [
    { id: "source", label: "Contenu source (copier-coller)", exemple: "Résultats de la revue annuelle du PEV 2025 (pays fictif) : couverture Penta3 nationale administrative de 82 %, contre 78 % en 2024. Taux d'abandon Penta1–Penta3 de 8 %. 4 régions sur 12 sous 70 % de couverture Penta3. Nombre estimé d'enfants zéro-dose en baisse dans 8 régions, mais en hausse dans les 2 régions touchées par l'insécurité. Introduction du vaccin contre le HPV chez les filles de 9 à 14 ans dans 3 régions pilotes. Principaux défis : ruptures de stock, départ d'agents formés, données incomplètes dans les zones d'insécurité.", type: "zone", aide: "Contenu publié ou validé pour diffusion (N0). Un rapport encore interne relève du niveau N1 et ne doit pas être diffusé." },
    { id: "emetteur", label: "Émetteur et cadre de diffusion", exemple: "Direction nationale de la vaccination (pays fictif), communication officielle après validation par le ministère", type: "texte" },
    { id: "publics", label: "Publics visés", exemple: "Décideurs et partenaires (résumé exécutif), professionnels de santé publique (LinkedIn), agents de santé et relais communautaires (WhatsApp), grand public rural (radio)", type: "texte" },
    { id: "langue", label: "Langue et contraintes", exemple: "Français simple ; le script radio sera traduit et lu en wolof par l'animateur de la radio communautaire", type: "texte" }
  ],
  modele: `Tu es spécialiste de la communication en santé publique, capable d'adapter un contenu technique à des publics et des canaux très différents sans en altérer l'exactitude.

CONTEXTE
Émetteur et cadre de diffusion : {{emetteur}}
Publics visés : {{publics}}
Langue et contraintes : {{langue}}

TÂCHE
1. Établis d'abord une « fiche de faits » : la liste numérotée des chiffres et affirmations clés du contenu source, chacun dans sa formulation exacte. Ces faits sont les seuls utilisables dans les déclinaisons.
2. Rédige les 4 déclinaisons suivantes à partir de la fiche de faits :
   a. Résumé exécutif (200 mots maximum) : résultats, défis, recommandations, pour décideurs et partenaires.
   b. Post LinkedIn (150 mots maximum) : accroche, 2 ou 3 résultats, un défi assumé, une conclusion ; ton professionnel, sans emoji, 3 mots-clés au maximum en fin de texte.
   c. Message WhatsApp (60 mots maximum) : une information principale et une action pour les agents et les relais.
   d. Script radio de 60 secondes (environ 120 à 140 mots) : phrases courtes, chiffres arrondis et peu nombreux, message principal répété, pauses et ton indiqués.
3. Pour chaque déclinaison, indique les numéros des faits utilisés.
4. Vérifie la cohérence : un même chiffre doit être identique, ou arrondi de façon signalée, dans tous les formats. Liste toute adaptation de chiffre.

CONTENU SOURCE
{{source}}

RÈGLES
- N'ajoute aucun chiffre, aucune cause, aucune citation, aucun résultat absent du contenu source.
- Ne transforme pas une hypothèse ou un défi en succès ; conserve les nuances (données administratives, régions en difficulté).
- Ne simplifie pas au point de fausser : une couverture administrative ne doit pas devenir « X % des enfants sont protégés ».
- Pas d'emoji, pas de superlatifs non justifiés.

FORMAT ATTENDU
- Fiche de faits (liste numérotée).
- Les 4 déclinaisons, chacune avec son titre, son nombre de mots et les numéros des faits utilisés.
- Un tableau de cohérence : Fait | Résumé | LinkedIn | WhatsApp | Radio.`,
  cadre: {
    C: "L'émetteur, les publics et les contraintes de langue fixent le registre de chaque format avant la rédaction.",
    A: "Commencer par une fiche de faits numérotée crée une source unique que toutes les déclinaisons doivent respecter.",
    D: "Le contenu source est collé intégralement : l'IA reformule, elle n'enrichit pas.",
    R: "Les règles protègent contre les dérives classiques de la vulgarisation : chiffres arrondis différemment, nuances perdues, succès exagérés.",
    E: "Les limites de mots et le tableau de cohérence permettent de vérifier en quelques minutes l'exactitude de chaque format."
  },
  adapter: [
    "Ajoutez une déclinaison « communiqué de presse » ou « fil de 5 messages pour un réseau social » en conservant la même fiche de faits.",
    "Pour un public anglophone ou lusophone, demandez les déclinaisons dans la langue cible à partir de la même fiche de faits, puis faites-les relire par un locuteur natif.",
    "Si vous publiez au nom d'une institution, collez sa charte éditoriale (ton, mentions obligatoires, mots-clés) dans le contexte."
  ],
  pieges: [
    "Les chiffres glissent d'un format à l'autre (82 % devient « plus de 80 % », puis « 4 enfants sur 5 ») : chaque arrondi doit être signalé et défendable.",
    "Le post LinkedIn tend vers l'autopromotion et efface les défis ; le message WhatsApp peut devenir alarmiste à force de brièveté.",
    "Le script radio dépasse souvent 60 secondes : au-delà de 140 à 150 mots, il est trop long pour une lecture posée."
  ],
  verif: [
    "Lisez le script radio à voix haute, chronomètre en main.",
    "Vérifiez chaque chiffre de chaque format à l'aide du tableau de cohérence et du contenu source.",
    "Faites valider les 4 formats par la personne responsable de la communication institutionnelle avant publication."
  ],
  outils: "Tout assistant généraliste convient. Si le rapport n'est pas encore publié, utilisez un outil institutionnel et ne diffusez rien avant validation.",
  lecon: "m2-iterer"
}

];
