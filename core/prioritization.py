"""
Prioritization logic — faithful to the workbook sheet "How to prioritize".

Method 1: multi-criteria scoring. Each criterion is scored 3 (best) / 2 (moderate)
/ 1 (worst). With the 8 intervention criteria, max = 24, min = 8. Workbook thresholds:
    High priority:   17 - 24
    Medium priority:  9 - 16
    Low priority:     1 - 8

Method 2: 2x2 IMPACT x FEASIBILITY matrix.
    (1) High impact & highly feasible      -> top priority
    (2) High impact & less feasible
    (3) Low impact & highly feasible
    (4) Low impact & less feasible          -> lowest priority
"""
from __future__ import annotations
from core.models import PrioritizationScore, PriorityLevel

# (key, French label, English label) — order matches the workbook's column C list.
INTERVENTION_CRITERIA = [
    ("expertise", "Expertise pour mettre en œuvre la solution", "Expertise to implement"),
    ("return_on_investment", "Retour sur investissement", "Return on investment"),
    ("effectiveness", "Efficacité de la solution", "Effectiveness of the solution"),
    ("ease_of_implementation", "Facilité de mise en œuvre/maintenance", "Ease of implementation"),
    ("negative_consequences", "Conséquences négatives potentielles", "Potential negative consequences"),
    ("legal_constraints", "Considérations juridiques", "Legal/regulatory constraints"),
    ("health_system_impact", "Impact sur les systèmes ou la santé", "Health system impact"),
    ("feasibility", "Faisabilité de l’intervention", "Operational feasibility"),
]

EXTENDED_CRITERIA = [
    ("cost", "Coût approximatif", "Approximate cost"),
    ("urgency", "Urgence", "Urgency"),
    ("equity_contribution", "Contribution à l’équité", "Contribution to equity"),
    ("zero_dose_contribution", "Contribution à atteindre les zéro dose",
     "Contribution to reaching zero-dose children"),
]

# Score legend per criterion (value 3 / 2 / 1) — used for nice UI dropdowns.
SCORE_LEGEND = {
    "expertise": ("Suffisante dans le pays", "Modérée dans le pays", "Aucune dans le pays"),
    "return_on_investment": ("Élevé", "Modéré", "Faible"),
    "effectiveness": ("Élevé", "Modéré", "Faible"),
    "ease_of_implementation": ("Très facile", "Modérément facile", "Pas facile"),
    "negative_consequences": ("Aucune", "Légères", "Importantes"),
    "legal_constraints": ("Aucune", "Légères", "Importantes"),
    "health_system_impact": ("Élevé", "Modéré", "Faible"),
    "feasibility": ("Très faisable", "Modérément faisable", "Faible faisabilité"),
}


def recompute_level(score: PrioritizationScore, use_extended: bool = False) -> PriorityLevel:
    return score.level(use_extended)


def matrix_quadrant(high_impact: bool, high_feasibility: bool) -> tuple[str, int, str]:
    """Return (key, rank 1..4, French label) for the 2x2 matrix."""
    if high_impact and high_feasibility:
        return "high_impact_high_feas", 1, "Impact élevé et très faisable (1)"
    if high_impact and not high_feasibility:
        return "high_impact_low_feas", 2, "Impact élevé et moins faisable (2)"
    if not high_impact and high_feasibility:
        return "low_impact_high_feas", 3, "Impact faible et très faisable (3)"
    return "low_impact_low_feas", 4, "Impact faible et moins faisable (4)"
