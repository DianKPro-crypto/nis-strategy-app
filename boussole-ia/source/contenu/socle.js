const APP = {
  nom: "Boussole IA",
  sousTitre: "Santé publique",
  version: "0.1.0",
  dateContenu: "octobre 2026"
};

const DOMAINES = [
  { id: "donnees", nom: "Données épidémiologiques et PEV", court: "Données" },
  { id: "decision", nom: "Aide à la décision stratégique", court: "Décision" },
  { id: "communication", nom: "Communication stratégique", court: "Communication" }
];

const COMPETENCES = [
  { id: "fondamentaux", nom: "Fondamentaux", desc: "Comprendre ce que l'IA fait, et ce qu'elle ne fait pas." },
  { id: "prompt", nom: "Art du prompt", desc: "Formuler des demandes précises et itérer avec méthode." },
  { id: "usages", nom: "Cas d'usage", desc: "Appliquer l'IA à des missions réelles de santé publique." },
  { id: "critique", nom: "Évaluation critique", desc: "Détecter hallucinations, erreurs de calcul et biais." },
  { id: "ethique", nom: "Éthique et réglementation", desc: "Protéger les données, respecter le droit, servir l'équité." }
];

// Seuils de niveau (points cumulés par compétence)
const NIVEAUX_COMPETENCE = [
  { nom: "Découverte", min: 0 },
  { nom: "Pratique", min: 5 },
  { nom: "Maîtrise", min: 10 }
];

const REGLES = [
  { titre: "Protéger", texte: "Aucune donnée personnelle ou confidentielle dans un outil non approuvé. Anonymisez, agrégez, ou abstenez-vous." },
  { titre: "Contextualiser", texte: "L'IA ne connaît ni votre pays ni votre programme. Donnez contexte, données, public et contraintes (CADRE)." },
  { titre: "Vérifier", texte: "Tout chiffre, toute référence et toute affirmation réglementaire se vérifient dans une source primaire (VÉRIF)." },
  { titre: "Itérer", texte: "La première réponse est un brouillon. Précisez, demandez les hypothèses, faites critiquer." },
  { titre: "Assumer", texte: "L'IA propose, vous décidez. Vous restez responsable et transparent sur son usage." }
];

const CADRE = [
  { l: "C", nom: "Contexte", texte: "Le rôle de l'IA, la situation, le destinataire." },
  { l: "A", nom: "Action", texte: "Le livrable précis, un verbe d'action, des étapes numérotées." },
  { l: "D", nom: "Données", texte: "Les documents et chiffres à utiliser, et seulement ceux-là." },
  { l: "R", nom: "Règles", texte: "Contraintes et interdits : n'invente rien, ton, longueur, sources." },
  { l: "E", nom: "Exemple de sortie", texte: "Le format attendu : tableau, plan, nombre de mots, public." }
];

const VERIF = [
  { l: "V", nom: "Véracité", q: "Les faits, chiffres et références sont-ils vérifiables dans une source primaire ?", aide: "Vérifiez au minimum les 3 chiffres les plus importants et chaque référence citée." },
  { l: "É", nom: "Équité", q: "Qui est absent, mal représenté ou stigmatisé ?", aide: "Zéro-dose, zones d'insécurité, nomades, déplacés, urbains pauvres, genre, handicap, langues." },
  { l: "R", nom: "Raisonnement", q: "Les hypothèses sont-elles explicites et les conclusions proportionnées aux données ?", aide: "Corrélation présentée comme cause ? Généralisation abusive ? Contre-arguments absents ?" },
  { l: "I", nom: "Intégrité des données", q: "Dénominateurs, formules, unités et périodes sont-ils corrects ?", aide: "Refaites 2 ou 3 calculs. Repérez couvertures supérieures à 100 % et valeurs manquantes." },
  { l: "F", nom: "Faisabilité", q: "Les recommandations sont-elles réalistes dans ce contexte ?", aide: "Ressources humaines et financières, calendrier, sécurité, système de santé, acceptabilité politique." }
];

const RELANCES = [
  "Avant de répondre, pose-moi les questions dont tu as besoin pour bien faire ce travail.",
  "Quelles hypothèses as-tu faites ? Lesquelles sont les plus fragiles ?",
  "Pour chaque affirmation, indique si elle vient de mes documents, de tes connaissances générales, ou si c'est une hypothèse.",
  "Qu'objecterait un bailleur sceptique ? Et un directeur régional de la santé ?",
  "Propose 3 options contrastées avec avantages, inconvénients et risques.",
  "Raccourcis à 150 mots pour un ministre, conclusion en premier.",
  "Réécris en langage simple pour un relais communautaire.",
  "Quels groupes de population ton analyse risque-t-elle d'oublier ?"
];

const NIVEAUX_DONNEES = [
  { id: "N0", nom: "Public", def: "Rapports publiés, articles, estimations WUENIC, communiqués.", ex: "Résumer le rapport annuel publié du programme." },
  { id: "N1", nom: "Interne", def: "Données agrégées non publiées (district ou plus), documents de travail sans élément sensible.", ex: "Analyser les couvertures par district issues du DHIS2." },
  { id: "N2", nom: "Confidentiel", def: "Budgets non publiés, négociations, notes politiques sensibles, données agrégées à très petite échelle.", ex: "Préparer une négociation de cofinancement." },
  { id: "N3", nom: "Personnel", def: "Données individuelles de patients ou d'enfants, listes nominatives, données de santé identifiables.", ex: "Liste des enfants perdus de vue avec noms et villages." }
];

const TYPES_OUTILS = [
  { id: "institutionnel", nom: "Compte institutionnel protégé", def: "Outil fourni par votre organisation avec des garanties contractuelles (par exemple Microsoft 365 Copilot avec votre compte professionnel, offres Entreprise de ChatGPT ou de Claude)." },
  { id: "perso-payant", nom: "Compte personnel payant", def: "Abonnement individuel dont vous réglez vous-même les paramètres de confidentialité." },
  { id: "gratuit", nom: "Compte gratuit", def: "Version gratuite d'un assistant grand public." },
  { id: "inconnu", nom: "Outil non vérifié", def: "Extension de navigateur, application inconnue, site tiers « propulsé par l'IA »." }
];

// Règle de prudence : type d'outil × niveau de sensibilité → [statut, conseil]
const MATRICE = {
  "institutionnel": {
    N0: ["ok", "Usage autorisé."],
    N1: ["ok", "Usage autorisé, dans le respect de la politique de votre organisation."],
    N2: ["attention", "Seulement si la politique de votre organisation l'autorise pour ce type d'information. Retirez tout élément non nécessaire à la tâche."],
    N3: ["bloquant", "Pas dans un assistant généraliste, même institutionnel, sauf outil expressément approuvé pour les données de santé par votre délégué à la protection des données. Anonymisez ou agrégez d'abord : vous repasserez en N1."]
  },
  "perso-payant": {
    N0: ["ok", "Usage autorisé."],
    N1: ["attention", "Possible si l'entraînement sur vos conversations est désactivé et si aucune donnée ne permet d'identifier une personne. Préférez l'outil institutionnel."],
    N2: ["bloquant", "Pas d'information confidentielle dans un compte personnel. Reformulez sans ces éléments ou utilisez l'outil institutionnel."],
    N3: ["bloquant", "Interdit : des données personnelles de santé ne vont jamais dans un compte personnel."]
  },
  "gratuit": {
    N0: ["ok", "Usage autorisé."],
    N1: ["attention", "Préférez un compte institutionnel. À défaut, généralisez les données et désactivez l'entraînement si l'option existe."],
    N2: ["bloquant", "Pas d'information confidentielle dans un compte gratuit."],
    N3: ["bloquant", "Interdit : des données personnelles de santé ne vont jamais dans un compte gratuit."]
  },
  "inconnu": {
    N0: ["attention", "Vérifiez qui édite l'outil et ce qu'il fait de vos données avant de l'utiliser."],
    N1: ["bloquant", "N'utilisez pas un outil dont vous ignorez la politique de données."],
    N2: ["bloquant", "N'utilisez pas un outil dont vous ignorez la politique de données."],
    N3: ["bloquant", "Interdit."]
  }
};

const CHECKLIST = [
  { id: "donnees", titre: "Données", questions: [
    { id: "niveau", type: "niveau", texte: "Quel est le niveau de sensibilité des données que vous allez partager avec l'IA ?" },
    { id: "identifiant", texte: "Les données contiennent-elles un élément permettant d'identifier une personne, même indirectement (nom, téléphone, coordonnées GPS d'un ménage, combinaison village + âge + date) ?", options: [
      { l: "Non, ou données correctement anonymisées et agrégées", r: "ok" },
      { l: "Je ne suis pas certain(e)", r: "attention", c: "Vérifiez colonne par colonne. En cas de doute, supprimez ou agrégez les variables indirectement identifiantes." },
      { l: "Oui", r: "bloquant", c: "N'utilisez pas d'assistant IA généraliste. Anonymisez ou agrégez d'abord, ou travaillez sans ces données." } ] },
    { id: "petits", texte: "Certains chiffres portent-ils sur de très petits effectifs (moins de 5 à 10 cas dans une localité ou un groupe) ?", options: [
      { l: "Non", r: "ok" },
      { l: "Oui", r: "attention", c: "Regroupez les petites unités (aire de santé vers district) ou masquez les cellules inférieures à 5 pour éviter toute ré-identification." } ] },
    { id: "droit", texte: "Avez-vous le droit de partager ces données avec un service extérieur (propriété du ministère, accord de partage, embargo avant publication) ?", options: [
      { l: "Oui, c'est autorisé, ou les données sont publiques", r: "ok" },
      { l: "Je ne sais pas", r: "attention", c: "Renseignez-vous auprès du propriétaire des données, souvent le ministère, avant tout usage." },
      { l: "Non", r: "bloquant", c: "N'utilisez pas ces données. Travaillez sur une version publique ou fictive." } ] }
  ] },
  { id: "outil", titre: "Outil", questions: [
    { id: "outil", type: "outil", texte: "Quel type d'outil allez-vous utiliser ?" },
    { id: "entrainement", texte: "L'utilisation de vos conversations pour entraîner les modèles est-elle désactivée ?", options: [
      { l: "Oui, ou compte institutionnel qui l'exclut contractuellement", r: "ok" },
      { l: "Non, ou je ne sais pas", r: "attention", c: "Ouvrez les paramètres de confidentialité de l'outil et désactivez cette option si elle existe." } ] }
  ] },
  { id: "impact", titre: "Impact et équité", questions: [
    { id: "decision", texte: "Le résultat contribuera-t-il à une décision qui affecte des populations (allocation de ressources, ciblage, priorisation) ?", options: [
      { l: "Non, usage rédactionnel ou exploratoire", r: "ok" },
      { l: "Oui", r: "attention", c: "Renforcez la vérification humaine, documentez la méthode et soumettez les conclusions à l'équipe pays avant décision." } ] },
    { id: "vulnerables", texte: "Les populations les plus vulnérables (zéro-dose, zones d'insécurité, nomades, déplacés, urbains pauvres, filles et femmes) sont-elles visibles dans vos données et dans votre question ?", options: [
      { l: "Oui", r: "ok" },
      { l: "Partiellement, ou je ne sais pas", r: "attention", c: "Demandez explicitement une analyse d'équité et signalez les groupes absents des données." } ] },
    { id: "contexte", texte: "Allez-vous fournir à l'IA le contexte local (système de santé, langues, contraintes) au lieu de la laisser supposer ?", options: [
      { l: "Oui", r: "ok" },
      { l: "Non", r: "attention", c: "Sans contexte, l'IA applique des solutions pensées pour d'autres pays. Utilisez la méthode CADRE." } ] }
  ] },
  { id: "responsabilite", titre: "Responsabilité et transparence", questions: [
    { id: "relecture", texte: "Qui vérifiera le résultat avant usage ?", options: [
      { l: "Moi-même avec la grille VÉRIF, plus un pair ou l'équipe pays pour les livrables importants", r: "ok" },
      { l: "Moi-même uniquement", r: "attention", c: "Acceptable pour un usage interne. Pour un livrable diffusé ou une décision, faites relire par un pair." },
      { l: "Personne : diffusion directe", r: "bloquant", c: "Aucun contenu produit par l'IA ne doit être diffusé sans vérification humaine." } ] },
    { id: "transparence", texte: "L'usage de l'IA sera-t-il mentionné de façon appropriée (note méthodologique, information du commanditaire) ?", options: [
      { l: "Oui", r: "ok" },
      { l: "Pas encore décidé", r: "attention", c: "Prévoyez une mention simple : « Document préparé avec l'appui d'un outil d'IA, vérifié et validé par l'auteur. »" } ] },
    { id: "chiffres", texte: "Le livrable contiendra-t-il des chiffres non encore validés par l'équipe pays ?", options: [
      { l: "Non, chiffres validés ou absents", r: "ok" },
      { l: "Oui", r: "attention", c: "Marquez-les clairement : « Données illustratives, à valider par l'équipe pays »." } ] }
  ] }
];

const LIENS_OUTILS = [
  { nom: "Claude", url: "https://claude.ai/new" },
  { nom: "ChatGPT", url: "https://chatgpt.com/" },
  { nom: "Microsoft 365 Copilot", url: "https://m365.cloud.microsoft/chat" },
  { nom: "Gemini", url: "https://gemini.google.com/" }
];

// Modules dont le contenu est encore en préparation (affichés dans le parcours)
const MODULE_M3 = {
  id: "m3", num: 3,
  titre: "Cas d'usage guidés",
  sousTitre: "S'entraîner sur les trois chaînes de valeur : données, décision, communication.",
  competence: "usages",
  special: "pratique",
  lecons: [],
  quiz: []
};

const MODULE_M6 = {
  id: "m6", num: 6,
  titre: "Déployer l'IA dans une équipe",
  sousTitre: "Règles d'usage, gouvernance et formation d'une équipe pays ou d'un programme.",
  competence: "ethique",
  bientot: "Version 1.0",
  plan: ["Rédiger une politique d'usage de l'IA pour une équipe", "Gouvernance : qui valide quoi", "Former une équipe en trois sessions", "Mesurer les bénéfices et les risques"],
  lecons: [],
  quiz: []
};
