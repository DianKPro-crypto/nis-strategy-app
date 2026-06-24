"""
NIS Strategy Builder — Streamlit MVP.

Guided, step-by-step assistant that turns the WHO "All-in-1 SWOT to Activities"
workbook into an interactive platform: country profile → document upload →
AI generation → human review/edit/validate → Excel/Word/PDF/PowerPoint export.

Run locally:   streamlit run app.py
"""
from __future__ import annotations
import streamlit as st

from config import settings
from config.countries import get_countries, DOCUMENT_CATEGORIES_FR
from core.translations import t
from core.models import (NISStrategy, CountryProfile, SWOTItem, RootCauseAnalysis,
                         StrategicObjective, Intervention, MEIndicator, Activity)
from core.epi_components import EPI_COMPONENTS, subcomponent_pairs, find_subcomponent, all_components
from core.document_loader import extract_document
from core import ai_engine
from core.prioritization import INTERVENTION_CRITERIA, SCORE_LEGEND
from core.validators import run_quality_check
from core import storage, branding, ui
from core.seed_djibouti import seed_djibouti
from exports.excel_exporter import build_excel
from exports.word_exporter import build_word
from exports.pdf_exporter import build_pdf
from exports.ppt_exporter import build_ppt

st.set_page_config(page_title="NIS Strategy Builder", page_icon="💉", layout="wide")


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
def S() -> NISStrategy:
    if "strategy" not in st.session_state:
        st.session_state.strategy = NISStrategy()
    return st.session_state.strategy


def lang() -> str:
    return S().profile.language or settings.DEFAULT_LANGUAGE


def _gen_or_warn(section: str):
    s = S()
    if not settings.ai_available():
        st.warning(t("no_api", lang()))
        return
    try:
        with st.spinner("IA en cours…"):
            data = ai_engine.generate_section(section, s.profile, s.documents, lang())
            ai_engine.apply_section(s, section, data)
        st.success("Généré ✅")
    except Exception as e:
        st.error(f"Erreur IA: {e}")


def _validate_button(section: str):
    s = S()
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(t("validate_section", lang()), key=f"val_{section}"):
            s.validated_sections[section] = True
    if s.validated_sections.get(section):
        col2.success(t("validated", lang()))


# --------------------------------------------------------------------------- #
# Sidebar navigation
# --------------------------------------------------------------------------- #
def sidebar():
    s = S()
    lp = branding.logo_path(lang())
    if lp:
        st.sidebar.image(str(lp), use_container_width=True)
    st.sidebar.title("💉 " + t("app_title", lang()))
    lg = st.sidebar.radio(t("language", lang()), ["fr", "en"],
                          index=0 if lang() == "fr" else 1,
                          format_func=lambda x: "Français" if x == "fr" else "English")
    s.profile.language = lg
    if not settings.ai_available():
        st.sidebar.warning(t("no_api", lg))
    else:
        st.sidebar.caption(f"IA: {settings.ANTHROPIC_MODEL}")
    pages = ["nav_profile", "nav_upload", "nav_vision", "nav_swot", "nav_root",
             "nav_obj", "nav_interv", "nav_me", "nav_act", "nav_qc", "nav_export"]
    choice = st.sidebar.radio(t("step", lg), pages, format_func=lambda k: t(k, lg))
    st.sidebar.divider()
    # quick save/load
    pname = st.sidebar.text_input("Projet", value=s.profile.country_name or "projet")
    c1, c2 = st.sidebar.columns(2)
    if c1.button("💾 " + t("save", lg)):
        storage.save_project(pname, s)
        st.sidebar.success("Enregistré")
    if c2.button("📂 Charger"):
        loaded = storage.load_project(pname)
        if loaded:
            st.session_state.strategy = loaded
            st.rerun()
    return choice


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
def page_profile():
    s = S(); lg = lang()
    with st.expander("🇩🇯 Charger l’exemple Djibouti (démonstration)"):
        st.caption("Pré-remplit toute la chaîne (vision → activités) avec un contenu illustratif "
                   "à valider par l’équipe pays.")
        if st.button("Charger l’exemple Djibouti 2027-2030"):
            st.session_state.strategy = seed_djibouti(lg)
            st.rerun()
    countries = get_countries()
    names = [n for _, n in countries]
    idx = names.index(s.profile.country_name) if s.profile.country_name in names else 0
    sel = st.selectbox(t("country", lg), names, index=idx)
    s.profile.country_name = sel
    s.profile.iso_code = dict((n, c) for c, n in countries).get(sel, "")
    c1, c2 = st.columns(2)
    s.profile.ministry_name = c1.text_input("Ministère / Ministry", s.profile.ministry_name)
    s.profile.epi_programme_name = c2.text_input("Programme PEV / EPI", s.profile.epi_programme_name)
    c3, c4, c5 = st.columns(3)
    s.profile.nis_start_year = c3.number_input("Année de début / Start year", 2020, 2040,
                                               s.profile.nis_start_year)
    dur = c4.selectbox("Durée / Duration", [3, 4, 5, 6], index=[3, 4, 5, 6].index(
        s.profile.nis_duration_years) if s.profile.nis_duration_years in [3, 4, 5, 6] else 2)
    s.profile.nis_duration_years = dur
    s.profile.currency = c5.text_input("Devise / Currency", s.profile.currency)
    c6, c7 = st.columns(2)
    s.profile.focal_point = c6.text_input("Point focal / Focal point", s.profile.focal_point)
    s.profile.generation_date = c7.text_input("Date", s.profile.generation_date)
    st.info(f"Période SNV / NIS period: **{s.profile.years[0]}–{s.profile.years[-1]}**")


def page_upload():
    s = S(); lg = lang()
    st.caption("⚠️ Documents confidentiels: ils sont traités localement et temporairement.")
    cat = st.selectbox("Catégorie du document", DOCUMENT_CATEGORIES_FR)
    files = st.file_uploader("Glissez-déposez vos fichiers",
                             type=list(settings.ALLOWED_EXTENSIONS), accept_multiple_files=True)
    if files and st.button("📥 Extraire le contenu"):
        for f in files:
            data = f.getvalue()
            if len(data) > settings.MAX_FILE_MB * 1024 * 1024:
                st.error(f"{f.name}: fichier trop volumineux (>{settings.MAX_FILE_MB} Mo)")
                continue
            doc = extract_document(data, f.name, cat)
            s.documents = [d for d in s.documents if d.name != f.name] + [doc]
        st.success(f"{len(files)} document(s) traité(s).")
    if s.documents:
        st.subheader(f"Documents ({len(s.documents)})")
        for d in s.documents:
            with st.expander(f"📄 {d.name} — {d.doc_category} ({d.file_type}, {d.n_pages or '?'} p.)"):
                st.caption(d.tables_summary)
                st.text((d.text or "")[:1500] + ("…" if len(d.text) > 1500 else ""))
                if st.button("🗑 Supprimer", key=f"del_{d.name}"):
                    s.documents = [x for x in s.documents if x.name != d.name]
                    st.rerun()


def page_vision():
    s = S(); lg = lang()
    if st.button("✨ " + t("generate", lg), key="gen_vision"):
        _gen_or_warn("vision")
    s.vision.vision = st.text_area("Vision (≈10 ans)", s.vision.vision, height=100)
    s.vision.goal = st.text_area("But de la SNV / NIS goal", s.vision.goal, height=80)
    s.vision.overall_objective = st.text_area("Objectif général / Overall objective",
                                              s.vision.overall_objective, height=80)
    _show_evidence(s.vision.evidence, lg)
    _validate_button("vision")


def page_swot():
    s = S(); lg = lang()
    st.caption("Forces/Faiblesses = INTERNES au PEV · Opportunités/Menaces = EXTERNES")
    if st.button("✨ " + t("generate", lg), key="gen_swot"):
        _gen_or_warn("swot")
    if not s.swot:
        s.swot = [SWOTItem(component_code=c.code, subcomponent_code=sub.code)
                  for c, sub in subcomponent_pairs()]
    by = {(x.component_code, x.subcomponent_code): x for x in s.swot}
    for comp in EPI_COMPONENTS:
        with st.expander(comp.label(lg)):
            for sub in comp.subcomponents:
                item = by.get((comp.code, sub.code)) or SWOTItem(
                    component_code=comp.code, subcomponent_code=sub.code)
                st.markdown(f"**{sub.label(lg)}**")
                c1, c2, c3, c4 = st.columns(4)
                item.strengths = _lines(c1.text_area(t("strengths", lg), "\n".join(item.strengths),
                                                      key=f"s_{sub.code}", height=90))
                item.weaknesses = _lines(c2.text_area(t("weaknesses", lg), "\n".join(item.weaknesses),
                                                       key=f"w_{sub.code}", height=90))
                item.opportunities = _lines(c3.text_area(t("opportunities", lg),
                                                          "\n".join(item.opportunities),
                                                          key=f"o_{sub.code}", height=90))
                item.threats = _lines(c4.text_area(t("threats", lg), "\n".join(item.threats),
                                                    key=f"t_{sub.code}", height=90))
                by[(comp.code, sub.code)] = item
    s.swot = list(by.values())
    _validate_button("swot")


def page_root():
    s = S(); lg = lang()
    st.caption("Méthode des POURQUOI : pour chaque faiblesse, remonter jusqu’à la cause profonde.")
    if st.button("✨ " + t("generate", lg), key="gen_root"):
        _gen_or_warn("root_causes")
    if st.button("➕ Ajouter une ligne"):
        s.root_causes.append(RootCauseAnalysis(whys=[""]))
    for i, rc in enumerate(s.root_causes):
        with st.expander(f"#{i+1} {rc.weakness[:60] or '(faiblesse)'}"):
            rc.subcomponent_code = st.text_input("Sous-composante (ex: 1.1)", rc.subcomponent_code,
                                                 key=f"rc_sub_{i}")
            sc = find_subcomponent(rc.subcomponent_code)
            rc.component_code = sc[0].code if sc else rc.component_code
            rc.weakness = st.text_area("Faiblesse", rc.weakness, key=f"rc_w_{i}", height=60)
            rc.whys = _lines(st.text_area("POURQUOI (une ligne par POURQUOI)", "\n".join(rc.whys),
                                          key=f"rc_y_{i}", height=100))
            rc.final_why = st.text_area("Dernier POURQUOI (cause profonde)", rc.final_why,
                                        key=f"rc_f_{i}", height=60)
    _validate_button("root_causes")


def page_obj():
    s = S(); lg = lang()
    s.grouping_option = st.radio(
        "Option de regroupement (Section 3)",
        ["option1", "option2", "option3"],
        format_func=lambda k: {"option1": "1 obstacle par sous-composante (≥26)",
                               "option2": "1 obstacle par composante (≥7)",
                               "option3": "Regroupement contextuel proposé par l’IA"}[k],
        index=["option1", "option2", "option3"].index(s.grouping_option))
    if st.button("✨ " + t("generate", lg), key="gen_obj"):
        _gen_or_warn("objectives")
    if st.button("➕ Ajouter un objectif"):
        s.objectives.append(StrategicObjective(obj_id=f"OBJ{len(s.objectives)+1}"))
    for i, o in enumerate(s.objectives):
        with st.expander(f"{o.obj_id or '#'+str(i+1)} — {o.objective_text[:60] or '(objectif)'}"):
            c1, c2 = st.columns(2)
            o.obj_id = c1.text_input("ID", o.obj_id or f"OBJ{i+1}", key=f"o_id_{i}")
            o.subcomponent_code = c2.text_input("Sous-composante", o.subcomponent_code, key=f"o_sc_{i}")
            sc = find_subcomponent(o.subcomponent_code)
            o.component_code = sc[0].code if sc else o.component_code
            o.main_obstacle = st.text_area("Problème/Obstacle principal", o.main_obstacle, key=f"o_ob_{i}")
            o.visionary_result = st.text_area("Résultat visionnaire du changement", o.visionary_result,
                                              key=f"o_vr_{i}")
            o.objective_text = st.text_area("Objectif stratégique prioritaire (SMART)", o.objective_text,
                                            key=f"o_ot_{i}")
            o.is_smart = st.checkbox("Confirmé SMART", o.is_smart, key=f"o_sm_{i}")
    _validate_button("objectives")


def page_interv():
    s = S(); lg = lang()
    if st.button("✨ " + t("generate", lg), key="gen_iv"):
        _gen_or_warn("interventions")
    obj_ids = [o.obj_id for o in s.objectives] or [""]
    if st.button("➕ Ajouter une intervention"):
        s.interventions.append(Intervention(intervention_id=f"INT{len(s.interventions)+1}"))
    for i, iv in enumerate(s.interventions):
        with st.expander(f"{iv.intervention_id or '#'+str(i+1)} — {iv.title[:60] or '(titre)'} "
                         f"[{getattr(iv.priority_level,'value',iv.priority_level)}]"):
            iv.title = st.text_input("Titre", iv.title, key=f"iv_t_{i}")
            c1, c2 = st.columns(2)
            iv.objective_id = c1.selectbox("Objectif lié", obj_ids,
                                           index=obj_ids.index(iv.objective_id) if iv.objective_id in obj_ids else 0,
                                           key=f"iv_o_{i}")
            iv.subcomponent_code = c2.text_input("Sous-composante", iv.subcomponent_code, key=f"iv_sc_{i}")
            iv.rationale = st.text_area("Justification", iv.rationale, key=f"iv_r_{i}", height=60)
            iv.expected_impact = st.text_area("Impact attendu", iv.expected_impact, key=f"iv_ei_{i}", height=60)
            st.markdown("**Notation multicritère (3=meilleur, 1=faible)**")
            cols = st.columns(4)
            for j, (key, fr, en) in enumerate(INTERVENTION_CRITERIA):
                legend = SCORE_LEGEND.get(key, ("3", "2", "1"))
                val = cols[j % 4].select_slider(
                    fr if lg == "fr" else en, options=[1, 2, 3],
                    value=int(getattr(iv.score, key)), key=f"iv_sc_{i}_{key}",
                    help=f"3={legend[0]} · 2={legend[1]} · 1={legend[2]}")
                setattr(iv.score, key, val)
            iv.priority_level = iv.score.level()
            st.metric("Score total / Priorité",
                      f"{iv.score.total()}/24 · {getattr(iv.priority_level,'value',iv.priority_level)}")
            years = [f"Y{k+1}" for k in range(s.profile.nis_duration_years)]
            sel = st.multiselect("Calendrier (années)", years,
                                 [y for y in years if iv.timeline.get(y)], key=f"iv_tl_{i}")
            iv.timeline = {y: (y in sel) for y in years}
    _validate_button("interventions")


def page_me():
    s = S(); lg = lang()
    if st.button("✨ " + t("generate", lg), key="gen_me"):
        _gen_or_warn("indicators")
    obj_ids = [o.obj_id for o in s.objectives] or [""]
    if st.button("➕ Ajouter un indicateur"):
        s.indicators.append(MEIndicator())
    years = [f"Y{k+1}" for k in range(s.profile.nis_duration_years)]
    for i, ind in enumerate(s.indicators):
        with st.expander(f"#{i+1} {ind.name[:60] or '(indicateur)'}"):
            ind.name = st.text_input("Nom de l’indicateur", ind.name, key=f"me_n_{i}")
            c1, c2, c3 = st.columns(3)
            ind.objective_id = c1.selectbox("Objectif", obj_ids,
                                            index=obj_ids.index(ind.objective_id) if ind.objective_id in obj_ids else 0,
                                            key=f"me_o_{i}")
            ind.indicator_type = c2.selectbox("Type", ["impact", "outcome", "output", "process"],
                                              index=["impact", "outcome", "output", "process"].index(
                                                  str(ind.indicator_type)) if str(ind.indicator_type) in
                                              ["impact", "outcome", "output", "process"] else 1, key=f"me_t_{i}")
            ind.subcomponent_code = c3.text_input("Sous-composante", ind.subcomponent_code, key=f"me_sc_{i}")
            ind.definition = st.text_area("Définition", ind.definition, key=f"me_d_{i}", height=50)
            ind.formula = st.text_input("Calcul / formule", ind.formula, key=f"me_f_{i}")
            cc1, cc2 = st.columns(2)
            ind.numerator_source = cc1.text_input("Source numérateur", ind.numerator_source, key=f"me_num_{i}")
            ind.denominator_source = cc2.text_input("Source dénominateur", ind.denominator_source, key=f"me_den_{i}")
            cc3, cc4 = st.columns(2)
            ind.frequency = cc3.text_input("Fréquence", ind.frequency, key=f"me_fr_{i}")
            ind.baseline = cc4.text_input("Situation de référence", ind.baseline, key=f"me_b_{i}")
            cc5, cc6 = st.columns(2)
            ind.responsible_measure = cc5.text_input("Responsable mesure", ind.responsible_measure, key=f"me_rm_{i}")
            ind.responsible_action = cc6.text_input("Responsable action", ind.responsible_action, key=f"me_ra_{i}")
            tcols = st.columns(len(years))
            for k, y in enumerate(years):
                ind.targets[y] = tcols[k].text_input(f"Cible An {k+1}", ind.targets.get(y, ""), key=f"me_y_{i}_{y}")
    _validate_button("indicators")


def page_act():
    s = S(); lg = lang()
    if st.button("✨ " + t("generate", lg), key="gen_act"):
        _gen_or_warn("activities")
    iv_ids = [iv.intervention_id for iv in s.interventions] or [""]
    levels = ["National", "Région/Gouvernorat", "District", "Formation sanitaire", "Communauté",
              "Tous les niveaux", "Autre"]
    if st.button("➕ Ajouter une activité"):
        s.activities.append(Activity())
    years = [f"Y{k+1}" for k in range(s.profile.nis_duration_years)]
    for i, a in enumerate(s.activities):
        with st.expander(f"#{i+1} {a.activity[:60] or '(activité)'}"):
            a.activity = st.text_area("Activité clé", a.activity, key=f"a_a_{i}", height=50)
            c1, c2 = st.columns(2)
            a.intervention_id = c1.selectbox("Intervention", iv_ids,
                                             index=iv_ids.index(a.intervention_id) if a.intervention_id in iv_ids else 0,
                                             key=f"a_iv_{i}")
            a.implementation_level = c2.selectbox("Niveau de mise en œuvre", levels,
                                                  index=levels.index(a.implementation_level) if a.implementation_level
                                                  in levels else 0, key=f"a_lv_{i}")
            a.lead = st.text_input("Responsable principal", a.lead, key=f"a_l_{i}")
            sel = st.multiselect("Années", years, [y for y in years if a.years.get(y)], key=f"a_y_{i}")
            a.years = {y: (y in sel) for y in years}
    _validate_button("activities")


def page_qc():
    s = S(); lg = lang()
    r = run_quality_check(s)
    st.progress(min(1.0, r.completion_pct / 100), text=f"Complétude: {r.completion_pct}%")
    if r.export_ready:
        st.success("✅ Prêt pour export")
    else:
        st.warning("⛔ Export bloqué tant que les sections clés ne sont pas complètes et validées.")
    cols = st.columns(2)
    blocks = [
        ("Champs manquants", r.missing_fields), ("Composantes non couvertes", r.uncovered_components),
        ("Objectifs sans indicateur", r.objectives_without_indicators),
        ("Interventions sans activité", r.interventions_without_activities),
        ("Indicateurs sans référence", r.indicators_without_baseline),
        ("Cibles non progressives", r.non_progressive_targets),
        ("À valider", r.needs_validation), ("Lacunes critiques", r.critical_gaps),
    ]
    for i, (title, items) in enumerate(blocks):
        with cols[i % 2]:
            st.markdown(f"**{title}** ({len(items)})")
            for it in items[:25]:
                st.write(f"- {it}")


def page_export():
    s = S(); lg = lang()
    r = run_quality_check(s)
    confirm = st.checkbox("Je confirme la validation humaine de la stratégie", value=r.export_ready)
    if not confirm:
        st.warning("Cochez la confirmation pour activer les exports.")
        return
    base = (s.profile.country_name or "NIS").replace(" ", "_")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.download_button("⬇️ Excel (.xlsx)", build_excel(s), f"SNV_{base}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("⬇️ Word (.docx)", build_word(s), f"SNV_{base}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c3:
        st.download_button("⬇️ PDF", build_pdf(s), f"SNV_{base}.pdf", "application/pdf")
    with c4:
        st.download_button("⬇️ PowerPoint (.pptx)", build_ppt(s), f"SNV_{base}.pptx",
                           "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    st.divider()
    st.download_button("⬇️ Données JSON", s.to_json(), f"SNV_{base}.json", "application/json")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _show_evidence(evidence, lg):
    if not evidence:
        return
    with st.expander("🔎 " + t("evidence", lg)):
        for e in evidence:
            conf = getattr(e.confidence, "value", e.confidence)
            st.write(f"- **{e.document_name}** ({e.locator}) — _{conf}_ : {e.excerpt}")


PAGES = {
    "nav_profile": page_profile, "nav_upload": page_upload, "nav_vision": page_vision,
    "nav_swot": page_swot, "nav_root": page_root, "nav_obj": page_obj,
    "nav_interv": page_interv, "nav_me": page_me, "nav_act": page_act,
    "nav_qc": page_qc, "nav_export": page_export,
}


def main():
    ui.inject_theme()
    choice = sidebar()
    ui.hero(choice, lang())
    PAGES[choice]()


if __name__ == "__main__":
    main()
