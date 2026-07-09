"""
NIS Strategy Builder — Streamlit MVP.

Guided, step-by-step assistant that turns the WHO "All-in-1 SWOT to Activities"
workbook into an interactive platform: country profile → document upload →
AI generation → human review/edit/validate → Excel/Word/PDF/PowerPoint export.

Run locally:   streamlit run app.py
"""
from __future__ import annotations
import json
from datetime import date
import streamlit as st

APP_VERSION = "2026-07-05 · v20 (codes SPO + GIA visibles dans la prose)"

from config import settings
from config.countries import get_countries, DOCUMENT_CATEGORIES_FR
from core.translations import t
from core.models import (NISStrategy, CountryProfile, SWOTItem, RootCauseAnalysis,
                         StrategicObjective, Intervention, MEIndicator, Activity, UploadedDocument)
from core.epi_components import EPI_COMPONENTS, subcomponent_pairs, find_subcomponent, all_components
from core.document_loader import extract_document
from core import ai_engine
from core.prioritization import INTERVENTION_CRITERIA, SCORE_LEGEND
from core.validators import run_quality_check
from core import storage, cloud_store, branding, ui
from core.seed_djibouti import seed_djibouti
from exports.excel_exporter import build_excel
from exports.word_exporter import build_word
from exports.pdf_exporter import build_pdf
from exports.ppt_exporter import build_ppt
from exports.narrative_exporter import build_narrative_word, build_financial_word, build_qa_word
from core.ai_engine import NARRATIVE_SECTIONS

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


# Widget-key prefixes per section. After AI generation we must clear these from
# session_state, otherwise Streamlit keeps the previously-shown (empty) values and
# the freshly generated content never appears in the fields.
SECTION_WIDGET_PREFIXES = {
    "swot": ("sw_",),
    "root_causes": ("rc_",),
    "objectives": ("o_id_", "o_sc_", "o_ob_", "o_vr_", "o_ot_", "o_sm_"),
    "interventions": ("iv_",),
    "indicators": ("me_",),
    "activities": ("a_",),
}


def _gen_or_warn(section: str):
    s = S()
    if not settings.ai_available():
        st.warning(t("no_api", lang()))
        return
    if section != "vision" and not s.documents:
        st.info("ℹ️ Aucun document importé (étape 1). L’IA produira surtout des « À compléter ». "
                "Importez vos documents pour des résultats fondés sur des preuves.")
    ok = False
    try:
        status = st.empty()
        prog = None
        if section in ("swot", "root_causes", "interventions", "indicators", "activities"):
            def prog(i, n, label):
                status.info(f"IA en cours… {i+1}/{n} : {label}")
        with st.spinner("IA en cours… (analyse des documents)"):
            data = ai_engine.generate_section(section, s.profile, s.documents, lang(),
                                              progress=prog, strategy=s)
            ai_engine.apply_section(s, section, data)
            if section == "swot" and isinstance(data, dict) and data.get("_errors"):
                st.session_state["_swot_errors"] = data["_errors"]
        status.empty()
        # Clear stale widget state so the regenerated values display on the next run.
        prefixes = SECTION_WIDGET_PREFIXES.get(section, ())
        for k in [k for k in list(st.session_state.keys()) if prefixes and k.startswith(prefixes)]:
            del st.session_state[k]
        attr = {"swot": "swot", "root_causes": "root_causes", "objectives": "objectives",
                "interventions": "interventions", "indicators": "indicators",
                "activities": "activities"}.get(section, "")
        st.session_state["_gen_result"] = len(getattr(s, attr, []) or []) if attr else 0
        _autosave(s)   # persist to cloud so the work survives a reboot
        ok = True
    except Exception as e:
        st.error(f"Erreur IA : {e}")
    # st.rerun() raises a control-flow exception — call it OUTSIDE the try/except,
    # otherwise the broad `except Exception` would swallow it.
    if ok:
        st.rerun()


def _fill_empty_swot(s: NISStrategy, empties: list[str]) -> None:
    """Targeted regeneration of only the still-empty FFOM subcomponents."""
    ok = False
    try:
        status = st.empty()
        def prog(i, n, label):
            status.info(f"Complétion… {i+1}/{n} : {label}")
        with st.spinner("Complétion des sous-composantes vides…"):
            data = ai_engine.regenerate_swot_subset(s.profile, s.documents, lang(), s, empties, progress=prog)
            ai_engine.apply_section(s, "swot", data)
        status.empty()
        for k in [k for k in list(st.session_state.keys()) if k.startswith("sw_")]:
            del st.session_state[k]
        _autosave(s)
        ok = True
    except Exception as e:
        st.error(f"Erreur IA : {e}")
    if ok:
        st.rerun()


def _autosave(s: NISStrategy) -> None:
    """Persist to cloud after meaningful changes (no-op if cloud not configured)."""
    if not cloud_store.cloud_available():
        return
    name = st.session_state.get("_project_name") or s.profile.country_name or "projet"
    try:
        cloud_store.save_project(name, s)
    except Exception:
        pass


def _validate_button(section: str):
    s = S()
    key = f"val_{section}"
    # Transparent, toggleable state (reflects the stored value; not auto-set by generation).
    if key not in st.session_state:
        st.session_state[key] = bool(s.validated_sections.get(section))
    val = st.checkbox(t("validate_section", lang()), key=key)
    s.validated_sections[section] = val
    if val:
        st.success(t("validated", lang()))


# --------------------------------------------------------------------------- #
# Sidebar navigation
# --------------------------------------------------------------------------- #
def sidebar():
    s = S()
    # Language FIRST so the logo, title and credit all render in the chosen language.
    cur = lang()
    lg = st.sidebar.radio(t("language", cur), ["fr", "en"],
                          index=0 if cur == "fr" else 1,
                          format_func=lambda x: "Français" if x == "fr" else "English")
    s.profile.language = lg
    # Inline data-URI so the logo shows immediately on first load (no media-server refresh needed).
    who_html = branding.logo_html(lg, 210)
    if who_html:
        st.sidebar.markdown(who_html, unsafe_allow_html=True)
    st.sidebar.title(t("app_title", lg))
    if not settings.ai_available():
        st.sidebar.warning(t("no_api", lg))
    else:
        st.sidebar.caption(f"IA: {settings.ANTHROPIC_MODEL}")
    pages = ["nav_profile", "nav_upload", "nav_vision", "nav_swot", "nav_root",
             "nav_obj", "nav_interv", "nav_me", "nav_act", "nav_qc", "nav_export",
             "nav_writeup", "nav_qa", "nav_help"]
    choice = st.sidebar.radio(t("step", lg), pages, format_func=lambda k: t(k, lg))
    st.sidebar.divider()

    # --- Project storage (cloud if configured, else local SQLite) ---
    use_cloud = cloud_store.cloud_available()
    store = cloud_store if use_cloud else storage
    st.sidebar.caption("☁️ Stockage cloud (durable)" if use_cloud
                       else "💾 Stockage local (temporaire — préférez l’export .json)")
    pname = st.sidebar.text_input("Nom du projet" if lg == "fr" else "Project name",
                                  value=s.profile.country_name or "projet")
    st.session_state["_project_name"] = pname

    # Cloud: dropdown of saved projects — the reliable way to restore all data.
    if use_cloud:
        try:
            saved = [n for n, _, _ in store.list_projects()]
        except Exception as e:
            saved = []
            st.sidebar.warning(f"Cloud injoignable : {e}")
        if saved:
            st.sidebar.caption("↩️ " + ("Reprendre un projet sauvegardé :" if lg == "fr"
                                        else "Reopen a saved project:"))
            pick = st.sidebar.selectbox("Projets enregistrés" if lg == "fr" else "Saved projects",
                                        ["—"] + saved, index=0, label_visibility="collapsed")
            if pick != "—" and st.sidebar.button(
                    "📂 " + ("Ouvrir ce projet" if lg == "fr" else "Open this project"),
                    use_container_width=True,
                    help=("Récupère TOUTES les données du projet sélectionné (recommandé)." if lg == "fr"
                          else "Restores ALL data of the selected project (recommended).")):
                loaded = store.load_project(pick)
                if loaded:
                    st.session_state.strategy = loaded
                    _clear_all_widget_state()
                    st.rerun()

    c1, c2 = st.sidebar.columns(2)
    if c1.button("💾 " + t("save", lg),
                 help=("Sauvegarde le projet en cours dans le cloud, sous le nom ci-dessus." if lg == "fr"
                       else "Save the current project to the cloud, under the name above.")):
        try:
            store.save_project(pname, s)
            st.sidebar.success("Enregistré ✅")
        except Exception as e:
            st.sidebar.error(f"Échec sauvegarde : {e}")
    if c2.button("🔄 " + ("Recharger" if lg == "fr" else "Reload"),
                 help=("Recharge depuis le cloud le projet portant EXACTEMENT le nom saisi ci-dessus. "
                       "Pour reprendre un projet, utilisez plutôt « Ouvrir ce projet »." if lg == "fr"
                       else "Reload from the cloud the project named EXACTLY as above. "
                       "To resume a project, use “Open this project” instead.")):
        try:
            loaded = store.load_project(pname)
        except Exception as e:
            loaded = None
            st.sidebar.error(f"Échec chargement : {e}")
        if loaded:
            st.session_state.strategy = loaded
            _clear_all_widget_state()
            st.rerun()
        else:
            st.sidebar.info("Aucun projet à ce nom." if lg == "fr" else "No project with that name.")
    # --- Design credit (Dian K Pro) — logo + text centered together ---
    st.sidebar.divider()
    line1 = ("Conception : OMS, améliorée par Dian K Pro" if lg == "fr"
             else "Design: WHO, enhanced by Dian K Pro")
    line2 = "Public Health & Digital Strategist"
    st.sidebar.markdown(
        f"{branding.dk_logo_html(140)}"
        f"<div style='font-size:0.75rem;color:#5b6b7b;line-height:1.35;text-align:center;margin-top:6px'>"
        f"{line1}<br><i>{line2}</i></div>", unsafe_allow_html=True)
    st.sidebar.caption(f"🔖 Version : {APP_VERSION}")
    return choice


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
def page_profile():
    s = S(); lg = lang()
    with st.expander("♻️ Reprendre un projet (fichier .json)"):
        st.caption("Importez le fichier .json téléchargé à l’étape « 10 · Exports » lors d’une session "
                   "précédente pour continuer le travail là où vous l’aviez laissé.")
        up = st.file_uploader("Fichier de sauvegarde (.json)", type=["json"], key="resume_json")
        if up is not None and st.button("Charger ce projet", key="load_json"):
            try:
                data = json.loads(up.getvalue())
                st.session_state.strategy = NISStrategy.from_dict(data)
                _clear_all_widget_state()
                st.success("Projet rechargé ✅")
                st.rerun()
            except Exception as e:
                st.error(f"Fichier invalide : {e}")
    countries = get_countries()
    names = [n for _, n in countries]
    placeholder = "— " + ("Sélectionnez votre pays" if lg == "fr" else "Select your country") + " —"
    options = [placeholder] + names
    idx = options.index(s.profile.country_name) if s.profile.country_name in names else 0
    sel = st.selectbox(t("country", lg), options, index=idx)
    s.profile.country_name = "" if sel == placeholder else sel
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
    s.profile.focal_point = c6.text_input("Point focal / Focal point", s.profile.focal_point,
                                          key="prof_focal")
    c7.text_input("Date du rapport / Report date", s.profile.generation_date, disabled=True,
                  help="Mise à jour automatiquement à la date du jour." if lg == "fr"
                  else "Automatically set to today’s date.")
    st.info(f"Période SNV / NIS period: **{s.profile.years[0]}–{s.profile.years[-1]}**")


def page_upload():
    s = S(); lg = lang()
    st.caption("⚠️ Documents confidentiels: ils sont traités localement et temporairement.")
    cat = st.selectbox("Catégorie du document", DOCUMENT_CATEGORIES_FR)
    # No 'type=' filter: some OS file pickers grey out all files when a type list is set
    # (symptom: "only folders selectable"). We accept several files and validate the extension after.
    fmts = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
    files = st.file_uploader(
        "Glissez-déposez vos fichiers (plusieurs à la fois)" if lg == "fr"
        else "Drag & drop your files (several at once)",
        accept_multiple_files=True, key="doc_upl",
        help=(f"Formats acceptés : {fmts}." if lg == "fr" else f"Accepted formats: {fmts}."))
    if files and st.button("📥 " + ("Extraire le contenu" if lg == "fr" else "Extract content")):
        n_ok = 0
        for f in files:
            ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
            if ext not in settings.ALLOWED_EXTENSIONS:
                st.warning(f"{f.name} : format « {ext or '?'} » non pris en charge — ignoré "
                           f"(formats : {fmts}).")
                continue
            data = f.getvalue()
            if len(data) > settings.MAX_FILE_MB * 1024 * 1024:
                st.error(f"{f.name}: fichier trop volumineux (>{settings.MAX_FILE_MB} Mo)")
                continue
            doc = extract_document(data, f.name, cat)
            s.documents = [d for d in s.documents if d.name != f.name] + [doc]
            n_ok += 1
        _autosave(s)   # persist immediately so documents survive a reboot
        st.success(f"{n_ok} document(s) traité(s)."
                   + (" ☁️ Sauvegardé." if cloud_store.cloud_available() else ""))

    # --- Fallback: paste text directly (works on any device, no file picker needed) ---
    with st.expander("✍️ " + ("Ou coller le texte d’un document (si le téléversement ne marche pas)"
                              if lg == "fr" else "Or paste a document's text (if upload doesn't work)")):
        st.caption("Copiez le texte de votre document (Word/PDF) et collez-le ici. Utile sur mobile ou "
                   "si le sélecteur de fichiers ne s’ouvre pas." if lg == "fr"
                   else "Copy your document's text and paste it here — useful on mobile or if the file "
                   "picker won't open.")
        pname = st.text_input("Nom du document" if lg == "fr" else "Document name",
                              value="Document collé" if lg == "fr" else "Pasted document", key="paste_name")
        pasted = st.text_area("Contenu" if lg == "fr" else "Content", height=200, key="paste_doc",
                              label_visibility="collapsed",
                              placeholder="Collez ici le texte…" if lg == "fr" else "Paste text here…")
        if pasted.strip() and st.button("➕ " + ("Ajouter ce texte comme document" if lg == "fr"
                                                 else "Add this text as a document"), key="add_pasted"):
            name = (pname or "Document collé").strip()
            doc = UploadedDocument(name=name, file_type="txt", doc_category=cat,
                                   text=pasted.strip(), n_pages=1)
            s.documents = [d for d in s.documents if d.name != name] + [doc]
            _autosave(s)
            st.session_state.pop("paste_doc", None)
            st.success(f"« {name} » ajouté ({len(pasted.strip())} caractères).")
            st.rerun()
    if s.documents:
        total_chars = sum(len((d.text or "").strip()) for d in s.documents)
        st.subheader(f"Documents ({len(s.documents)}) — {total_chars:,} caractères extraits".replace(",", " "))
        if total_chars < 300:
            st.warning("⚠️ Très peu de texte a été extrait. L’IA ne pourra pas s’appuyer sur ces "
                       "documents. Causes fréquentes : PDF **scanné** (image, sans texte) ou fichier vide. "
                       "Fournissez une version **texte** du document, ou saisissez les éléments manuellement.")
        for d in s.documents:
            chars = len((d.text or "").strip())
            flag = "  ·  ⚠️ peu de texte" if chars < 150 else ""
            with st.expander(f"📄 {d.name} — {d.doc_category} ({d.file_type}, {d.n_pages or '?'} p., "
                             f"{chars} car.){flag}"):
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
    docs_added = st.session_state.pop("_docs_added_msg", None)
    if docs_added:
        st.success(f"📄 {docs_added} document(s) ajouté(s) aux sources (visibles à l’étape « 1 · Documents »).")
    stats = st.session_state.pop("_ads_stats", None)
    total = st.session_state.pop("_ads_total", None)
    if stats:
        if total or stats.get("mapped"):
            n = total or stats.get("mapped", 0)
            st.success(f"Import ADS ✅ : {n} obstacle(s) aligné(s) sur l’outil.")
        else:
            st.error("Aucun obstacle reconnu dans le fichier. Vérifiez qu’il contient bien une colonne "
                     "**Code** (format 3.X.Y) et **Obstacle / faiblesse**.")
            st.caption(f"Séparateur détecté : « {stats.get('delimiter')} » · "
                       f"Colonnes lues : {stats.get('columns')}")
    # --- Import: documents sources (Word/PDF/Excel/…) ET/OU analyse ADS (.csv) — tous types, 1 ou plusieurs ---
    do_import = False
    with st.expander("📥 Importer des fichiers ici (documents Word/PDF/Excel **ou** analyse ADS .csv)"):
        st.caption("Déposez **tous types de fichiers**, un ou plusieurs. Un **.csv ADS** (obstacles 3.X.Y) "
                   "est aligné automatiquement sur les composantes ; un **document** (Word, PDF, Excel…) "
                   "est ajouté comme source pour l’IA. (Vous pouvez aussi utiliser l’étape « 1 · Documents ».)")
        # No 'type=' filter -> nothing is greyed out; we route each file by its extension.
        ups = st.file_uploader("Fichiers (tous types)", key="ads_csv", accept_multiple_files=True)
        if ups and st.button("📥 Importer", key="ads_import_btn"):
            do_import = True
    if do_import:
        from core import ads_import
        ads_total, last_stats, docs_added, skipped = 0, {}, 0, []
        for up in ups:
            name = up.name
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            data = up.getvalue()
            try:
                if ext == "csv":
                    items, last_stats = ads_import.import_ads_csv(data)
                    if items:
                        ads_import.merge_into(s, items)
                        ads_total += len(items)
                    else:  # a CSV that isn't an ADS obstacle file -> keep it as a source document
                        s.documents = [d for d in s.documents if d.name != name] + \
                                      [extract_document(data, name, "Analyse ADS / autre")]
                        docs_added += 1
                elif ext in settings.ALLOWED_EXTENSIONS:
                    s.documents = [d for d in s.documents if d.name != name] + \
                                  [extract_document(data, name, "Document source")]
                    docs_added += 1
                else:
                    skipped.append(f"{name} ({ext or '?'})")
            except Exception as e:
                skipped.append(f"{name} : {e}")
        if ads_total:
            for k in [k for k in list(st.session_state.keys()) if k.startswith("sw_")]:
                del st.session_state[k]
            st.session_state["_ads_stats"] = last_stats
            st.session_state["_ads_total"] = ads_total
        if docs_added:
            st.session_state["_docs_added_msg"] = docs_added
        if skipped:
            st.warning("Ignoré(s) : " + " ; ".join(skipped))
        _autosave(s)
    if do_import and (ads_total or docs_added):
        st.rerun()
    if st.button("✨ " + t("generate", lg), key="gen_swot"):
        _gen_or_warn("swot")
    if not s.swot:
        s.swot = [SWOTItem(component_code=c.code, subcomponent_code=sub.code)
                  for c, sub in subcomponent_pairs()]
    # Key by subcomponent code only (robust if the AI returns a mismatched component code).
    by = {x.subcomponent_code: x for x in s.swot}
    total_subs = sum(len(c.subcomponents) for c in EPI_COMPONENTS)
    filled = [(c, sub) for c in EPI_COMPONENTS for sub in c.subcomponents
              if (it := by.get(sub.code)) and any([it.strengths, it.weaknesses, it.opportunities, it.threats])]
    empties = [f"{sub.code}" for c in EPI_COMPONENTS for sub in c.subcomponents
               if not ((it := by.get(sub.code)) and any([it.strengths, it.weaknesses, it.opportunities, it.threats]))]
    if filled:
        st.caption(f"📊 Couverture FFOM : {len(filled)}/{total_subs} sous-composantes renseignées.")
        if empties:
            st.warning("Sous-composantes encore vides : " + ", ".join(empties))
            if settings.ai_available() and st.button(
                    f"🔁 Compléter les {len(empties)} sous-composantes vides", key="fill_empties"):
                _fill_empty_swot(s, empties)
    errs = st.session_state.pop("_swot_errors", None)
    if errs:
        st.caption("⚠️ Incidents de génération : " + " · ".join(errs[:6]))
    for comp in EPI_COMPONENTS:
        with st.expander(comp.label(lg)):
            for sub in comp.subcomponents:
                item = by.get(sub.code) or SWOTItem(component_code=comp.code, subcomponent_code=sub.code)
                item.component_code, item.subcomponent_code = comp.code, sub.code
                st.markdown(f"**{sub.label(lg)}**")
                c1, c2, c3, c4 = st.columns(4)
                item.strengths = _lines(c1.text_area(t("strengths", lg), "\n".join(item.strengths),
                                                      key=f"sw_s_{sub.code}", height=90))
                item.weaknesses = _lines(c2.text_area(t("weaknesses", lg), "\n".join(item.weaknesses),
                                                       key=f"sw_w_{sub.code}", height=90))
                item.opportunities = _lines(c3.text_area(t("opportunities", lg),
                                                          "\n".join(item.opportunities),
                                                          key=f"sw_o_{sub.code}", height=90))
                item.threats = _lines(c4.text_area(t("threats", lg), "\n".join(item.threats),
                                                    key=f"sw_t_{sub.code}", height=90))
                by[sub.code] = item
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
            iv.rationale = st.text_area("Justification (fondée sur les documents)", iv.rationale,
                                        key=f"iv_r_{i}", height=70)
            iv.expected_impact = st.text_area("Impact attendu", iv.expected_impact, key=f"iv_ei_{i}", height=60)
            iv.feasibility_note = st.text_area("Faisabilité", iv.feasibility_note, key=f"iv_fz_{i}", height=50)
            cc1, cc2, cc3 = st.columns(3)
            iv.prerequisites = _lines(cc1.text_area("Prérequis (1 par ligne)", "\n".join(iv.prerequisites),
                                                    key=f"iv_pr_{i}", height=90))
            iv.risks = _lines(cc2.text_area("Risques (1 par ligne)", "\n".join(iv.risks),
                                            key=f"iv_rk_{i}", height=90))
            iv.partners = _lines(cc3.text_area("Partenaires (1 par ligne)", "\n".join(iv.partners),
                                               key=f"iv_pa_{i}", height=90))
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
            _show_evidence(iv.evidence, lg)
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


def page_help():
    lg = lang()
    fname = "GUIDE_UTILISATEUR_FR.md" if lg == "fr" else "USER_GUIDE_EN.md"
    path = settings.BASE_DIR / fname
    svg_path = settings.BASE_DIR / ("assets/quality_chain_fr.svg" if lg == "fr"
                                    else "assets/quality_chain_en.svg")
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        st.error("Guide indisponible / Guide unavailable.")
        return
    # Drop the leading H1 (the hero banner already shows the title)
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # Render the guide, replacing the markdown image with the inline SVG
    # (Streamlit can't load relative local images, so we inject the SVG directly).
    buffer = []
    for ln in lines:
        if ln.lstrip().startswith("!["):
            st.markdown("\n".join(buffer)); buffer = []
            try:
                st.markdown(svg_path.read_text(encoding="utf-8"), unsafe_allow_html=True)
            except Exception:
                pass
        else:
            buffer.append(ln)
    st.markdown("\n".join(buffer))
    st.divider()
    st.download_button("⬇️ " + ("Télécharger ce guide (.md)" if lg == "fr" else "Download this guide (.md)"),
                       text, fname, "text/markdown")


def page_export():
    s = S(); lg = lang()
    # Stamp the report with today's date (not the day the project was first created/saved).
    s.profile.generation_date = date.today().isoformat()
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
    st.markdown("**💾 Sauvegarde complète du projet (.json)** — conservez ce fichier ! Il permet de "
                "**reprendre tout le travail plus tard** via l’étape « 0 · Profil du pays ».")
    st.download_button("⬇️ Télécharger la sauvegarde (.json)", s.to_json(),
                       f"SNV_{base}.json", "application/json")


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


def page_writeup():
    s = S(); lg = lang()
    ai = settings.ai_available()
    st.subheader("A. " + ("Rédaction complète de la SNV (IA)" if lg == "fr" else "Full NIS write-up (AI)"))
    st.caption("L’IA rédige un document narratif approfondi (toutes les sections), aligné IA2030/Gavi 6.0. "
               "Vous pouvez importer une SNV déjà rédigée : l’IA la prendra comme base pour bâtir la version "
               "complète." if lg == "fr" else
               "The AI writes an in-depth narrative (all sections), aligned to IA2030/Gavi 6.0. You may upload an "
               "existing drafted NIS: the AI will build the complete version on top of it.")
    with st.expander("📄 " + ("Documents de base pour la rédaction (facultatif)" if lg == "fr"
                              else "Base documents for the write-up (optional)"), expanded=True):
        def _loaded_msg(n, label_fr, label_en):
            if n < 200:
                st.warning(("⚠️ Peu de texte extrait (" + str(n) + " car.). PDF scanné ? Fournissez une "
                            "version texte." if lg == "fr" else
                            f"⚠️ Little text extracted ({n} chars). Scanned PDF? Provide a text version."))
            else:
                st.success((f"✅ {label_fr} chargé : {n} caractères — prêt pour la rédaction." if lg == "fr"
                            else f"✅ {label_en} loaded: {n} characters — ready for writing."))
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**1. " + ("Document SNV (Word) — étape 10 ou SNV rédigée" if lg == "fr"
                                   else "NIS document (Word) — from step 10 or a drafted NIS") + "**")
            d_up = st.file_uploader("SNV (.docx / .pdf / .txt)", type=["docx", "pdf", "txt"],
                                    key="snv_draft_up", label_visibility="collapsed")
            if d_up is not None:
                if st.button("📥 " + ("Charger la SNV" if lg == "fr" else "Load NIS"), key="load_draft"):
                    s.snv_draft_text = extract_document(d_up.getvalue(), d_up.name, "SNV").text or ""
                    _autosave(s); st.rerun()
                elif not s.snv_draft_text:
                    st.info("👉 " + ("Cliquez « Charger la SNV » pour confirmer." if lg == "fr"
                                     else "Click “Load NIS” to confirm."))
            if s.snv_draft_text:
                _loaded_msg(len(s.snv_draft_text), "Document SNV", "NIS document")
                if st.button("🗑 " + ("Retirer ce document" if lg == "fr" else "Remove this document"),
                             key="rm_draft"):
                    s.snv_draft_text = ""; _autosave(s); st.rerun()
        with cc2:
            st.markdown("**2. " + ("Rapport financier — issu du NIS.COST (étape B)" if lg == "fr"
                                   else "Financial report — from NIS.COST (part B)") + "**")
            f_up = st.file_uploader("Rapport financier", type=["docx", "pdf", "xlsx", "csv", "txt"],
                                    key="fin_input_up", label_visibility="collapsed")
            if f_up is not None:
                if st.button("📥 " + ("Charger le rapport financier" if lg == "fr"
                                      else "Load financial report"), key="load_fin_input"):
                    s.financial_report = extract_document(f_up.getvalue(), f_up.name, "Rapport financier").text or ""
                    _autosave(s); st.rerun()
                elif not s.financial_report:
                    st.info("👉 " + ("Cliquez « Charger le rapport financier »." if lg == "fr"
                                     else "Click “Load financial report”."))
            if s.financial_report:
                _loaded_msg(len(s.financial_report), "Rapport financier", "Financial report")
                if st.button("🗑 " + ("Retirer ce rapport" if lg == "fr" else "Remove this report"),
                             key="rm_fin"):
                    s.financial_report = ""; _autosave(s); st.rerun()
        st.caption(("L’IA bâtira la SNV complète en s’appuyant sur ces documents + vos analyses (étapes 2→8)."
                    if lg == "fr" else
                    "The AI builds the full NIS on these documents + your analyses (steps 2→8)."))
    ready = []
    if s.snv_draft_text:
        ready.append("SNV de base ✅" if lg == "fr" else "base NIS ✅")
    if s.financial_report:
        ready.append("rapport financier ✅" if lg == "fr" else "financial report ✅")
    if s.objectives or s.swot:
        ready.append("analyses plateforme ✅" if lg == "fr" else "platform analyses ✅")
    st.caption(("L’IA utilisera : " if lg == "fr" else "The AI will use: ")
               + (", ".join(ready) if ready else
                  ("aucune source chargée — chargez au moins un document ou complétez les étapes 2→8."
                   if lg == "fr" else "no source loaded — upload a document or complete steps 2→8.")))
    if st.button("✍️ " + ("Rédiger la SNV complète" if lg == "fr" else "Write the full NIS"), key="gen_narr"):
        if not ai:
            st.warning(t("no_api", lg))
        else:
            status = st.empty()
            try:
                with st.spinner("Rédaction en cours…"):
                    ai_engine.generate_narrative(
                        s, lg, progress=lambda i, n, l: status.info(f"Rédaction… {i+1}/{n} : {l}"))
                status.empty()
                for k in [k for k in list(st.session_state) if k.startswith("nar_")]:
                    del st.session_state[k]
                _autosave(s)
                st.rerun()
            except Exception as e:
                st.error(f"Erreur IA : {e}")
    if s.narrative:
        st.success("Rédaction disponible — relisez et ajustez, puis téléchargez." if lg == "fr"
                   else "Draft ready — review, edit, then download.")
        for key, tfr, ten in NARRATIVE_SECTIONS:
            with st.expander(tfr if lg == "fr" else ten):
                s.narrative[key] = st.text_area("", s.narrative.get(key, ""), key=f"nar_{key}", height=220,
                                                label_visibility="collapsed")
        base = (s.profile.country_name or "SNV").replace(" ", "_")
        st.download_button("⬇️ " + ("Rapport SNV narratif (.docx)" if lg == "fr" else "NIS narrative report (.docx)"),
                           build_narrative_word(s), f"SNV_narratif_{base}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    st.divider()
    st.subheader("B. " + ("Rapport financier (NIS.COST)" if lg == "fr" else "Financial report (NIS.COST)"))
    up = st.file_uploader("Fichier NIS.COST" if lg == "fr" else "NIS.COST file",
                          type=["xlsx", "csv", "pdf", "docx"], key="niscost_up")
    if up is not None and st.button("📥 " + ("Charger le NIS.COST" if lg == "fr" else "Load NIS.COST")):
        doc = extract_document(up.getvalue(), up.name, "NIS.COST")
        s.niscost_text = doc.text or ""
        _autosave(s)
        st.success(f"{len(s.niscost_text)} " + ("caractères chargés." if lg == "fr" else "characters loaded."))
    if s.niscost_text:
        st.caption(f"NIS.COST : {len(s.niscost_text)} " + ("caractères" if lg == "fr" else "characters"))
        if st.button("✨ " + ("Générer le rapport financier (IA)" if lg == "fr" else "Generate financial report (AI)"),
                     key="gen_fin"):
            if not ai:
                st.warning(t("no_api", lg))
            else:
                try:
                    with st.spinner("Analyse financière en cours…"):
                        s.financial_report = ai_engine.generate_financial(s.profile, lg, s.niscost_text)
                    for k in [k for k in list(st.session_state) if k.startswith("fin_")]:
                        del st.session_state[k]
                    _autosave(s)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur IA : {e}")
    if s.financial_report:
        s.financial_report = st.text_area("Rapport financier" if lg == "fr" else "Financial report",
                                          s.financial_report, key="fin_report", height=320)
        base = (s.profile.country_name or "SNV").replace(" ", "_")
        st.download_button("⬇️ " + ("Rapport financier (.docx)" if lg == "fr" else "Financial report (.docx)"),
                           build_financial_word(s), f"Rapport_financier_{base}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def _qa_document_text(s: NISStrategy) -> str:
    if s.narrative:
        parts = [f"## {k}\n{v}" for k, v in s.narrative.items() if v]
        if s.financial_report:
            parts.append("## financial\n" + s.financial_report)
        return "\n\n".join(parts)
    # fallback: structured summary
    lines = [f"Vision: {s.vision.vision}", f"But: {s.vision.goal}", f"Objectif: {s.vision.overall_objective}"]
    lines += [f"Objectif {o.obj_id}: {o.objective_text}" for o in s.objectives]
    lines += [f"Intervention: {iv.title} — {iv.rationale}" for iv in s.interventions]
    lines += [f"Indicateur: {i.name} base={i.baseline} cibles={i.targets}" for i in s.indicators]
    return "\n".join(lines)


def page_qa():
    s = S(); lg = lang()
    st.caption("L’IA relit la stratégie, vérifie cohérence/complétude/normes (OMS, IA2030, Gavi 6.0) et "
               "surligne en rouge ce qui doit être ajouté ou amélioré." if lg == "fr" else
               "The AI reviews the strategy for coherence/completeness/standards and flags in red what to improve.")
    if st.button("🔎 " + ("Analyser la qualité (IA)" if lg == "fr" else "Analyze quality (AI)"), key="gen_qa"):
        if not settings.ai_available():
            st.warning(t("no_api", lg))
        else:
            try:
                with st.spinner("Analyse qualité en cours…"):
                    st.session_state["_qa"] = ai_engine.generate_qa(s.profile, lg, _qa_document_text(s))
            except Exception as e:
                st.error(f"Erreur IA : {e}")
    qa = st.session_state.get("_qa")
    if qa:
        c1, c2 = st.columns([1, 3])
        c1.metric("Score", f"{qa.get('score', '—')}/100")
        c2.info(qa.get("overall", ""))
        st.markdown("#### " + ("Points à ajouter / améliorer" if lg == "fr" else "Items to add / improve"))
        order = {"critique": 0, "critical": 0, "majeur": 1, "major": 1, "mineur": 2, "minor": 2}
        for f in sorted(qa.get("findings", []) or [], key=lambda x: order.get(str(x.get("severity", "")).lower(), 3)):
            sev = str(f.get("severity", "")).lower()
            msg = f"**[{f.get('severity','')}] {f.get('section','')}** — {f.get('issue','')}\n\n→ {f.get('recommendation','')}"
            (st.error if sev in ("critique", "critical", "majeur", "major") else st.warning)(msg)
        base = (s.profile.country_name or "SNV").replace(" ", "_")
        st.download_button("⬇️ " + ("Rapport d’assurance qualité (.docx)" if lg == "fr" else "QA report (.docx)"),
                           build_qa_word(s, qa), f"QA_SNV_{base}.docx",
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


PAGES = {
    "nav_profile": page_profile, "nav_upload": page_upload, "nav_vision": page_vision,
    "nav_swot": page_swot, "nav_root": page_root, "nav_obj": page_obj,
    "nav_interv": page_interv, "nav_me": page_me, "nav_act": page_act,
    "nav_qc": page_qc, "nav_export": page_export, "nav_writeup": page_writeup,
    "nav_qa": page_qa, "nav_help": page_help,
}


ALL_WIDGET_PREFIXES = ("sw_", "rc_", "o_id_", "o_sc_", "o_ob_", "o_vr_", "o_ot_", "o_sm_",
                       "iv_", "me_", "a_", "val_", "nar_", "fin_")


def _clear_all_widget_state():
    """Drop all editable-field widget keys so they re-init from the (new) model."""
    for k in [k for k in list(st.session_state.keys()) if k.startswith(ALL_WIDGET_PREFIXES)]:
        del st.session_state[k]


def _debounced_autosave():
    """Background-style save: persist to cloud whenever the strategy content changed."""
    if not cloud_store.cloud_available():
        return
    name = st.session_state.get("_project_name")
    s = S()
    if not name or not s.profile.country_name:
        return
    import hashlib
    try:
        h = hashlib.md5(s.to_json().encode("utf-8")).hexdigest()
    except Exception:
        return
    if st.session_state.get("_saved_hash") != h:
        try:
            cloud_store.save_project(name, s)
            st.session_state["_saved_hash"] = h
        except Exception:
            pass


def main():
    # Report date always reflects the current day.
    S().profile.generation_date = date.today().isoformat()
    ui.inject_theme()
    choice = sidebar()
    ui.hero(choice, lang())
    res = st.session_state.pop("_gen_result", None)
    if res is not None:
        st.success(f"Généré ✅ ({res} élément(s)) — vérifiez et complétez si besoin.")
    PAGES[choice]()
    _debounced_autosave()   # auto-save any edits (profile, focal point, tables…) to the cloud


if __name__ == "__main__":
    main()
