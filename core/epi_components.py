"""
EPI components and subcomponents — the structural backbone of the tool.

Extracted faithfully from the WHO workbook
"2_All in 1 SWOT to Activities_FR.xlsx" (sheet "Country_Sequence of events",
column A = components/subcomponents, column B = examples of content to look for).

7 components, 26 subcomponents. French labels are the exact workbook wording;
English labels follow the prompt specification. The `examples` field carries the
workbook's guidance ("Exemples de contenu à rechercher par sous-composante"),
which we pass to the AI so its SWOT findings stay grounded in WHO methodology.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubComponent:
    code: str            # e.g. "1.1"
    label_fr: str
    label_en: str
    examples_fr: str = ""

    def label(self, lang: str) -> str:
        return self.label_fr if lang == "fr" else self.label_en


@dataclass(frozen=True)
class Component:
    code: str            # e.g. "1"
    label_fr: str
    label_en: str
    subcomponents: list[SubComponent] = field(default_factory=list)

    def label(self, lang: str) -> str:
        return self.label_fr if lang == "fr" else self.label_en


EPI_COMPONENTS: list[Component] = [
    Component(
        "1", "1. Gestion du programme et financement",
        "1. Programme Management and Financing",
        [
            SubComponent("1.1", "1.1 Politiques et orientations", "1.1 Policies and guidance",
                "Politiques nationales de vaccination (ouverture des flacons multidoses, vaccination de rattrapage, "
                "élimination des pertes vaccinales, vaccination obligatoire avant l’entrée à la crèche/école), SOP."),
            SubComponent("1.2", "1.2 Gouvernance et redevabilité", "1.2 Governance and accountability",
                "GTCV/NITAG, autres comités (CCN, NPEC, NTF, NEC MAPI), communication entre les niveaux du système de "
                "santé, termes de référence des fonctions du PEV, mécanismes de redevabilité."),
            SubComponent("1.3", "1.3 Planification et approvisionnement", "1.3 Planning and procurement",
                "Existence de plans stratégiques et opérationnels à jour, lien entre planification et planification financière."),
            SubComponent("1.4", "1.4 Coordination des partenaires", "1.4 Partner coordination",
                "Comité de coordination inter-agences (CCIA/ICC), autres mécanismes de coordination aux niveaux inférieurs."),
            SubComponent("1.5", "1.5 Budgétisation et finances", "1.5 Budgeting and finance",
                "Disponibilité de ressources financières nationales à tous les niveaux, évolution dans le temps, "
                "financement des nouveaux vaccins, financement des communautés zéro dose."),
        ],
    ),
    Component(
        "2", "2. Gestion des ressources humaines", "2. Human Resource Management",
        [
            SubComponent("2.1", "2.1 Planification des ressources humaines", "2.1 Human resource planning",
                "Plan RH du PEV, organigramme, descriptions de poste, adéquation des effectifs à tous les niveaux, "
                "motivation, rotation du personnel, RH affectant les communautés zéro dose."),
            SubComponent("2.2", "2.2 Renforcement des capacités", "2.2 Capacity building",
                "Formation sur le programme et les politiques — occasions manquées, flacons ouverts, chaîne du froid, "
                "planification, formation sur le tas, MLM, nouveaux vaccins."),
            SubComponent("2.3", "2.3 Supervision et suivi de la performance", "2.3 Supervision and performance monitoring",
                "Supervision formative (qualité et quantité) et par niveau."),
        ],
    ),
    Component(
        "3", "3. Approvisionnement, qualité et logistique des vaccins",
        "3. Vaccine Supply, Quality and Logistics",
        [
            SubComponent("3.1", "3.1 Chaîne du froid", "3.1 Cold chain",
                "Quantité, adéquation et fonctionnalité de la chaîne du froid."),
            SubComponent("3.2", "3.2 Gestion des approvisionnements", "3.2 Supply management",
                "Prévision des besoins, achat central des vaccins, distribution et gestion des stocks "
                "(ruptures, dommages, pertes), logistique affectant les communautés zéro dose."),
            SubComponent("3.3", "3.3 Transport", "3.3 Transport",
                "Adéquation et fonctionnalité du système de transport (Push/Pull), carburant, véhicules, maintenance."),
            SubComponent("3.4", "3.4 Gestion des déchets", "3.4 Waste management",
                "Disponibilité de directives et d’infrastructures de gestion des déchets."),
        ],
    ),
    Component(
        "4", "4. Prestation des services", "4. Service Delivery",
        [
            SubComponent("4.1", "4.1 Ressources humaines et stratégies", "4.1 Human resources and strategies",
                "Adéquation entre stratégies (fixe, avancée, mobile) planifiées et mises en œuvre, géographies "
                "(populations marginalisées, déplacés, réfugiés, contextes fragiles) et RH pour la prestation."),
            SubComponent("4.2", "4.2 Qualité des séances", "4.2 Session quality",
                "Temps au point de prestation, sensibilisation avant/pendant/après, taux d’abandon, accueil."),
            SubComponent("4.3", "4.3 Intégration", "4.3 Integration",
                "Niveau d’intégration des stratégies du PEV avec les autres services de soins de santé primaires."),
        ],
    ),
    Component(
        "5", "5. Couverture vaccinale et suivi des MAPI",
        "5. Immunization Coverage and AEFI Monitoring",
        [
            SubComponent("5.1", "5.1 Ressources humaines et systèmes", "5.1 Human resources and systems",
                "Utilisation d’un système d’information sanitaire incluant les données spécifiques au PEV."),
            SubComponent("5.2", "5.2 Enregistrement et notification", "5.2 Recording and reporting",
                "Existence et utilisation des outils de données (pointage, registres, formulaires, cartes), "
                "analyse et utilisation des données d’équité pour la planification."),
            SubComponent("5.3", "5.3 Qualité des données", "5.3 Data quality",
                "Ponctualité et complétude, revues de la qualité des données, qualité des données administratives."),
            SubComponent("5.4", "5.4 Suivi et utilisation de la couverture", "5.4 Coverage monitoring and use",
                "Suivi de la performance et mesures correctives, courbe de suivi, couvertures par antigène, "
                "vaccination dans le privé, données pour identifier les communautés zéro dose."),
            SubComponent("5.5", "5.5 Suivi des MAPI", "5.5 AEFI monitoring",
                "Système fonctionnel de surveillance des MAPI, comité d’évaluation de la causalité, "
                "plan de communication sur les risques."),
        ],
    ),
    Component(
        "6", "6. Surveillance des maladies", "6. Disease Surveillance",
        [
            SubComponent("6.1", "6.1 Surveillance des maladies", "6.1 Disease surveillance",
                "Épidémies récentes de MEV, utilisation des données pour la réponse, ponctualité/complétude/qualité, "
                "rougeole comme traceur des communautés zéro dose."),
            SubComponent("6.2", "6.2 Détection et réponse", "6.2 Detection and response",
                "Disponibilité des fournitures de laboratoire, surveillance de laboratoire, investigation des cas, "
                "rapidité de la réponse."),
            SubComponent("6.3", "6.3 Performance", "6.3 Performance",
                "Atteinte des indicateurs de surveillance des MEV (rougeole, polio, tétanos néonatal, fièvre jaune), "
                "utilisation des données pour l’action."),
        ],
    ),
    Component(
        "7", "7. Génération de la demande", "7. Demand Generation",
        [
            SubComponent("7.1", "7.1 Demande", "7.1 Demand",
                "Hésitation vaccinale, rumeurs, satisfaction des clients, confiance, facteurs influençant la demande "
                "dans les communautés zéro dose."),
            SubComponent("7.2", "7.2 Plaidoyer et communication", "7.2 Advocacy and communication",
                "Communication entre agents de santé et clients, séances de plaidoyer programme/bénéficiaires."),
            SubComponent("7.3", "7.3 Engagement communautaire", "7.3 Community engagement",
                "Agents de santé et communautés/leaders, prise en compte des préoccupations communautaires."),
        ],
    ),
]

# Optional bucket for country-specific priorities outside the 7 standard components.
COUNTRY_SPECIFIC = Component(
    "8", "8. Priorités spécifiques au pays (hors composantes PEV)",
    "8. Country-specific priorities (outside EPI components)",
    [SubComponent("8.1", "8.1 Priorité spécifique au pays", "8.1 Country-specific priority",
                  "Tout autre problème pertinent pour le PEV ne relevant pas directement d’une composante standard.")],
)


def all_components(include_country_specific: bool = True) -> list[Component]:
    return EPI_COMPONENTS + ([COUNTRY_SPECIFIC] if include_country_specific else [])


def subcomponent_pairs(include_country_specific: bool = False) -> list[tuple[Component, SubComponent]]:
    """Flat list of (component, subcomponent) — handy for iterating the 26 (or 27) rows."""
    out: list[tuple[Component, SubComponent]] = []
    for comp in all_components(include_country_specific):
        for sub in comp.subcomponents:
            out.append((comp, sub))
    return out


def find_subcomponent(code: str) -> tuple[Component, SubComponent] | None:
    for comp in all_components(True):
        for sub in comp.subcomponents:
            if sub.code == code:
                return comp, sub
    return None


# Sanity: the workbook defines 7 components / 26 subcomponents.
assert len(EPI_COMPONENTS) == 7
assert sum(len(c.subcomponents) for c in EPI_COMPONENTS) == 26
