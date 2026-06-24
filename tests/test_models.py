"""Smoke tests for models, components and prioritization thresholds."""
from core.models import NISStrategy, PrioritizationScore, PriorityLevel
from core.epi_components import EPI_COMPONENTS, subcomponent_pairs


def test_component_counts():
    assert len(EPI_COMPONENTS) == 7
    assert sum(len(c.subcomponents) for c in EPI_COMPONENTS) == 26
    assert len(subcomponent_pairs()) == 26


def test_strategy_roundtrip():
    s = NISStrategy()
    s.profile.country_name = "Djibouti"
    data = s.to_dict()
    s2 = NISStrategy.from_dict(data)
    assert s2.profile.country_name == "Djibouti"


def test_priority_thresholds():
    # all 3s -> 24 -> High; all 1s -> 8 -> Low; all 2s -> 16 -> Medium
    hi = PrioritizationScore(**{k: 3 for k in PrioritizationScore.CORE_CRITERIA})
    lo = PrioritizationScore(**{k: 1 for k in PrioritizationScore.CORE_CRITERIA})
    mid = PrioritizationScore(**{k: 2 for k in PrioritizationScore.CORE_CRITERIA})
    assert hi.total() == 24 and hi.level() == PriorityLevel.HIGH
    assert lo.total() == 8 and lo.level() == PriorityLevel.LOW
    assert mid.total() == 16 and mid.level() == PriorityLevel.MEDIUM
