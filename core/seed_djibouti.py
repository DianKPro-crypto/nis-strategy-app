"""
Pre-filled illustrative example — Djibouti NIS 2027-2030 (bilingual FR/EN).

DEMO content showing the full chain (vision → SWOT → root causes → objectives →
interventions → M&E → activities) end to end. Figures are illustrative and must be
replaced/validated by the country team. Loaded from the UI via a button.
"""
from __future__ import annotations
from core.models import (NISStrategy, CountryProfile, CountryVision, SWOTItem,
                         RootCauseAnalysis, StrategicObjective, Intervention,
                         MEIndicator, Activity, PrioritizationScore, EvidenceReference,
                         Confidence, IndicatorType, PriorityLevel)


def seed_djibouti(language: str = "fr") -> NISStrategy:
    fr = language != "en"

    def L(f: str, e: str) -> str:          # pick FR or EN
        return f if fr else e

    s = NISStrategy()
    s.profile = CountryProfile(
        country_name="Djibouti", iso_code="DJ",
        ministry_name=L("Ministère de la Santé", "Ministry of Health"),
        epi_programme_name=L("Programme Élargi de Vaccination (PEV)",
                             "Expanded Programme on Immunization (EPI)"),
        nis_start_year=2027, nis_duration_years=4, currency="DJF",
        focal_point=L("Coordonnateur national du PEV", "National EPI Coordinator"),
        language=language,
    )

    s.vision = CountryVision(
        vision=L("D’ici 2035, chaque enfant, adolescent et adulte à Djibouti bénéficie de tous les "
                 "vaccins recommandés, tout au long de la vie, sans laisser personne de côté.",
                 "By 2035, every child, adolescent and adult in Djibouti receives all recommended "
                 "vaccines across the life course, leaving no one behind."),
        goal=L("Sur la période 2027-2030, réduire le nombre d’enfants zéro dose et sous-vaccinés et "
               "atteindre une couverture équitable et durable en vaccins essentiels sur tout le territoire.",
               "Over 2027-2030, reduce the number of zero-dose and under-immunized children and achieve "
               "equitable, sustainable coverage with essential vaccines nationwide."),
        overall_objective=L("Renforcer un système de vaccination résilient, intégré aux soins de santé "
                            "primaires et financé de manière durable, conformément à l’IA2030.",
                            "Strengthen a resilient immunization system, integrated with primary health "
                            "care and sustainably financed, in line with IA2030."),
        evidence=[EvidenceReference(document_name=L("Exemple de démonstration", "Demonstration example"),
                                    locator="—",
                                    excerpt=L("Contenu illustratif à valider par l’équipe pays.",
                                              "Illustrative content to be validated by the country team."),
                                    confidence=Confidence.LOW)],
    )

    s.swot = [
        SWOTItem(component_code="1", subcomponent_code="1.5",
                 strengths=[L("Ligne budgétaire nationale dédiée aux vaccins existante",
                              "National budget line dedicated to vaccines exists")],
                 weaknesses=[L("Financement insuffisant pour atteindre les communautés zéro dose",
                               "Insufficient funding to reach zero-dose communities"),
                             L("Dépendance élevée au financement Gavi", "High dependence on Gavi funding")],
                 opportunities=[L("Engagement de cofinancement dans le cadre Gavi 6.0",
                                  "Co-financing commitment under the Gavi 6.0 framework")],
                 threats=[L("Espace budgétaire national contraint", "Constrained national fiscal space")],
                 evidence=[EvidenceReference(document_name=L("Exemple", "Example"), locator="—",
                                             confidence=Confidence.LOW)]),
        SWOTItem(component_code="5", subcomponent_code="5.4",
                 strengths=[L("Système DHIS2 déployé au niveau district", "DHIS2 deployed at district level")],
                 weaknesses=[L("Faible utilisation des données pour identifier les zéro dose",
                               "Weak use of data to identify zero-dose children"),
                             L("Complétude des rapports < 80 % dans certains districts",
                               "Report completeness < 80% in some districts")],
                 opportunities=[L("Appui des partenaires au renforcement du SNIS",
                                  "Partner support to strengthen the HMIS")],
                 threats=[L("Mouvements de population et zones d’accès difficile",
                            "Population movements and hard-to-reach areas")]),
        SWOTItem(component_code="7", subcomponent_code="7.3",
                 strengths=[L("Réseau de relais communautaires actif", "Active community health worker network")],
                 weaknesses=[L("Engagement communautaire insuffisant dans les zones périurbaines",
                               "Insufficient community engagement in peri-urban areas")],
                 opportunities=[L("Plateformes communautaires existantes (santé maternelle)",
                                  "Existing community platforms (maternal health)")],
                 threats=[L("Hésitation vaccinale liée à des rumeurs", "Vaccine hesitancy driven by rumours")]),
    ]

    s.root_causes = [
        RootCauseAnalysis(component_code="5", subcomponent_code="5.4",
                          weakness=L("Faible utilisation des données pour identifier les zéro dose",
                                     "Weak use of data to identify zero-dose children"),
                          whys=[L("Les agents n’analysent pas les données au niveau local",
                                  "Staff do not analyse data at local level"),
                                L("Manque de formation à l’analyse et de temps dédié",
                                  "Lack of analysis training and dedicated time"),
                                L("Pas de supervision formative régulière sur l’usage des données",
                                  "No regular supportive supervision on data use")],
                          final_why=L("Absence d’un mécanisme institutionnalisé de revue des données à microplanification",
                                      "No institutionalized data-review mechanism within microplanning")),
        RootCauseAnalysis(component_code="1", subcomponent_code="1.5",
                          weakness=L("Financement insuffisant pour atteindre les communautés zéro dose",
                                     "Insufficient funding to reach zero-dose communities"),
                          whys=[L("Les coûts d’atteinte des zéro dose ne sont pas budgétisés séparément",
                                  "Zero-dose reach costs are not separately budgeted"),
                                L("Absence de microplanification chiffrée pour ces populations",
                                  "No costed microplanning for these populations")],
                          final_why=L("La planification financière n’intègre pas une approche ciblée zéro dose",
                                      "Financial planning does not integrate a targeted zero-dose approach")),
    ]

    s.objectives = [
        StrategicObjective(obj_id="OBJ1", component_code="5", subcomponent_code="5.4",
                           main_obstacle=L("Les données ne sont pas utilisées pour identifier et atteindre "
                                           "les enfants zéro dose",
                                           "Data are not used to identify and reach zero-dose children"),
                           visionary_result=L("Chaque district identifie et suit ses communautés zéro dose "
                                              "et adapte ses stratégies de vaccination en conséquence.",
                                              "Every district identifies and tracks its zero-dose communities "
                                              "and adapts its immunization strategies accordingly."),
                           objective_text=L("D’ici 2030, 100 % des districts conduisent une revue trimestrielle "
                                            "des données et utilisent une microplanification ciblant les zéro dose.",
                                            "By 2030, 100% of districts conduct quarterly data reviews and use "
                                            "microplanning targeting zero-dose children."),
                           is_smart=True),
        StrategicObjective(obj_id="OBJ2", component_code="1", subcomponent_code="1.5",
                           main_obstacle=L("Le financement national ne cible pas spécifiquement les zéro dose",
                                           "National financing does not specifically target zero-dose children"),
                           visionary_result=L("Les activités d’atteinte des zéro dose sont planifiées et "
                                              "financées de façon durable.",
                                              "Zero-dose reach activities are sustainably planned and financed."),
                           objective_text=L("D’ici 2030, intégrer une ligne budgétaire chiffrée « zéro dose » "
                                            "dans le plan opérationnel annuel financé à au moins 80 %.",
                                            "By 2030, integrate a costed ‘zero-dose’ budget line into the annual "
                                            "operational plan, funded at least 80%."),
                           is_smart=True),
    ]

    s.interventions = [
        Intervention(intervention_id="INT1", objective_id="OBJ1", component_code="5", subcomponent_code="5.4",
                     title=L("Institutionnaliser les revues trimestrielles de données au niveau district",
                             "Institutionalize quarterly district-level data reviews"),
                     rationale=L("Améliore l’identification et le suivi des zéro dose.",
                                 "Improves identification and tracking of zero-dose children."),
                     expected_impact=L("Hausse de l’utilisation des données et de la couverture équitable",
                                       "Higher data use and more equitable coverage"),
                     feasibility_note=L("Réalisable avec l’appui des partenaires SNIS",
                                        "Feasible with HMIS partner support"),
                     score=PrioritizationScore(expertise=3, return_on_investment=3, effectiveness=3,
                                               ease_of_implementation=2, negative_consequences=3,
                                               legal_constraints=3, health_system_impact=3, feasibility=2),
                     priority_level=PriorityLevel.HIGH,
                     timeline={"Y1": True, "Y2": True, "Y3": True, "Y4": True},
                     prerequisites=[L("Outils de revue harmonisés", "Harmonized review tools"),
                                    L("Connectivité DHIS2", "DHIS2 connectivity")],
                     risks=[L("Rotation du personnel formé", "Turnover of trained staff")],
                     partners=["OMS/WHO", "UNICEF"]),
        Intervention(intervention_id="INT2", objective_id="OBJ2", component_code="1", subcomponent_code="1.5",
                     title=L("Élaborer une microplanification chiffrée ciblant les communautés zéro dose",
                             "Develop costed microplanning targeting zero-dose communities"),
                     rationale=L("Permet une budgétisation dédiée et un plaidoyer financier.",
                                 "Enables dedicated budgeting and financial advocacy."),
                     expected_impact=L("Financement sécurisé des activités zéro dose",
                                       "Secured financing of zero-dose activities"),
                     score=PrioritizationScore(expertise=2, return_on_investment=3, effectiveness=3,
                                               ease_of_implementation=2, negative_consequences=3,
                                               legal_constraints=3, health_system_impact=3, feasibility=2),
                     priority_level=PriorityLevel.HIGH,
                     timeline={"Y1": True, "Y2": True},
                     partners=["Gavi", L("Ministère des Finances", "Ministry of Finance")]),
    ]

    s.indicators = [
        MEIndicator(component_code="5", subcomponent_code="5.4", objective_id="OBJ1",
                    name=L("Proportion de districts conduisant une revue trimestrielle des données",
                           "Proportion of districts conducting quarterly data reviews"),
                    indicator_type=IndicatorType.OUTPUT,
                    definition=L("Districts ayant tenu ≥3 revues de données sur l’année / total des districts",
                                 "Districts with ≥3 data reviews in the year / total districts"),
                    formula=L("(Districts avec ≥3 revues / Total districts) × 100",
                              "(Districts with ≥3 reviews / Total districts) × 100"),
                    numerator_source=L("Comptes rendus de revue district", "District review reports"),
                    denominator_source=L("Carte sanitaire", "Health facility master list"),
                    data_source=L("DHIS2 / rapports districts", "DHIS2 / district reports"),
                    frequency=L("Trimestrielle", "Quarterly"),
                    responsible_measure=L("Coordination PEV", "EPI Coordination"),
                    responsible_action=L("Directions régionales de santé", "Regional health directorates"),
                    baseline=L("≈30 % (à confirmer par l’équipe pays)", "≈30% (to be confirmed by country team)"),
                    targets={"Y1": "50", "Y2": "70", "Y3": "90", "Y4": "100"},
                    assumptions=L("Disponibilité des outils et de la connectivité",
                                  "Availability of tools and connectivity"),
                    measurement_risks=L("Sous-rapportage", "Under-reporting"), confidence=Confidence.MEDIUM),
        MEIndicator(component_code="1", subcomponent_code="1.5", objective_id="OBJ2",
                    name=L("Taux de financement des activités zéro dose du POA",
                           "Funding rate of zero-dose activities in the AOP"),
                    indicator_type=IndicatorType.OUTCOME,
                    definition=L("Montant financé / montant chiffré des activités zéro dose",
                                 "Amount funded / costed amount for zero-dose activities"),
                    formula=L("(Financé / Budgété) × 100", "(Funded / Budgeted) × 100"),
                    data_source=L("Rapports financiers PEV", "EPI financial reports"),
                    frequency=L("Annuelle", "Annual"),
                    responsible_measure=L("Gestionnaire financier PEV", "EPI finance officer"),
                    responsible_action=L("Comité de coordination (CCIA)", "Coordination committee (ICC)"),
                    baseline=L("Situation de référence à confirmer par l’équipe pays",
                               "Baseline to be confirmed by the country team"),
                    targets={"Y1": "40", "Y2": "60", "Y3": "70", "Y4": "80"}, confidence=Confidence.LOW),
    ]

    s.activities = [
        Activity(component_code="5", subcomponent_code="5.4", objective_id="OBJ1", intervention_id="INT1",
                 activity=L("Élaborer et diffuser un guide harmonisé de revue trimestrielle des données",
                            "Develop and disseminate a harmonized quarterly data-review guide"),
                 implementation_level=L("National", "National"), years={"Y1": True},
                 lead=L("Coordination PEV", "EPI Coordination"), partners=["OMS/WHO"],
                 deliverables=[L("Guide de revue validé", "Validated review guide")]),
        Activity(component_code="5", subcomponent_code="5.4", objective_id="OBJ1", intervention_id="INT1",
                 activity=L("Former les équipes cadres de district à l’analyse et l’usage des données",
                            "Train district management teams in data analysis and use"),
                 implementation_level=L("District", "District"), years={"Y1": True, "Y2": True},
                 lead=L("Directions régionales", "Regional directorates"), partners=["UNICEF"],
                 prerequisites=[L("Guide disponible", "Guide available")],
                 deliverables=[L("Districts formés", "Districts trained")]),
        Activity(component_code="1", subcomponent_code="1.5", objective_id="OBJ2", intervention_id="INT2",
                 activity=L("Réaliser un atelier national de microplanification chiffrée zéro dose",
                            "Hold a national costed zero-dose microplanning workshop"),
                 implementation_level=L("National", "National"), years={"Y1": True},
                 lead=L("Coordination PEV", "EPI Coordination"), partners=["Gavi"],
                 deliverables=[L("Microplan chiffré", "Costed microplan")]),
    ]

    s.validated_sections = {}
    return s
