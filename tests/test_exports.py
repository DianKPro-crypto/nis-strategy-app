"""Verify all four exporters produce non-empty files from a populated strategy."""
import pytest
from core.models import (NISStrategy, CountryProfile, CountryVision, SWOTItem,
                         StrategicObjective, Intervention, MEIndicator, Activity)


def _sample() -> NISStrategy:
    s = NISStrategy(profile=CountryProfile(country_name="Djibouti", language="fr",
                                           nis_start_year=2026, nis_duration_years=5))
    s.vision = CountryVision(vision="V", goal="G", overall_objective="O")
    s.swot = [SWOTItem(component_code="1", subcomponent_code="1.1",
                       strengths=["s1"], weaknesses=["w1"], opportunities=["o1"], threats=["t1"])]
    s.objectives = [StrategicObjective(obj_id="OBJ1", subcomponent_code="1.1",
                                       objective_text="Obj SMART", main_obstacle="ob", is_smart=True)]
    s.interventions = [Intervention(intervention_id="INT1", objective_id="OBJ1", title="Interv",
                                    expected_impact="impact", timeline={"Y1": True})]
    s.indicators = [MEIndicator(name="Couverture DTC3", objective_id="OBJ1", subcomponent_code="1.1",
                                baseline="80%", targets={"Y1": "82", "Y2": "85"})]
    s.activities = [Activity(activity="Act 1", intervention_id="INT1", objective_id="OBJ1",
                             subcomponent_code="1.1", implementation_level="National",
                             years={"Y1": True})]
    return s


@pytest.mark.parametrize("builder_path", [
    "exports.excel_exporter:build_excel",
    "exports.word_exporter:build_word",
    "exports.pdf_exporter:build_pdf",
    "exports.ppt_exporter:build_ppt",
])
def test_exporters(builder_path):
    mod, fn = builder_path.split(":")
    builder = getattr(__import__(mod, fromlist=[fn]), fn)
    out = builder(_sample())
    assert isinstance(out, (bytes, bytearray)) and len(out) > 500
