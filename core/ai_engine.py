"""
Anthropic Claude integration.

- `generate_section()` runs one workflow step and returns validated structured data.
- `generate_nis_strategy()` is the central orchestrator required by the spec (§10):
  it runs all sections in order and returns a fully populated NISStrategy.
- Strict-JSON enforcement with retry on invalid JSON.
- Offline/manual mode: when no API key is set, returns empty scaffolds so the user
  can fill everything by hand (acceptance criterion: offline mode).
"""
from __future__ import annotations
import json
import re

from config import settings
from core.models import (
    NISStrategy, CountryProfile, UploadedDocument, CountryVision, SWOTItem,
    RootCauseAnalysis, StrategicObjective, Intervention, MEIndicator, Activity,
    PrioritizationScore,
)
from core.epi_components import subcomponent_pairs, find_subcomponent
from templates.prompts import (SYSTEM_PROMPT, SYSTEM_PROMPT_NARRATIVE, build_generation_prompt,
                               build_root_cause_prompt, build_intervention_prompt, build_indicator_prompt,
                               build_swot_prompt, build_activity_prompt, build_narrative_prompt,
                               build_financial_prompt, build_qa_prompt)

SECTIONS = ["vision", "swot", "root_causes", "objectives", "interventions", "indicators", "activities"]


class AIError(RuntimeError):
    pass


def _client():
    if not settings.ai_available():
        raise AIError("ANTHROPIC_API_KEY manquante")
    import anthropic
    # Bounded timeout so a stalled request fails fast instead of hanging forever.
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=300.0, max_retries=2)


def _extract_json(raw: str) -> dict:
    """Tolerantly pull the first JSON object out of a model response."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except Exception:
        start, depth = raw.find("{"), 0
        if start == -1:
            raise
        for i in range(start, len(raw)):
            depth += raw[i] == "{"
            depth -= raw[i] == "}"
            if depth == 0:
                return json.loads(raw[start:i + 1])
    raise AIError("Réponse JSON invalide")


def _fix_pct(text: str) -> str:
    """Stick the % sign to the number (80 % -> 80%), including narrow/nbsp spaces."""
    return re.sub(r"(\d)[\s  ]+%", r"\1%", text or "")


def _call_claude_text(prompt: str, system: str = SYSTEM_PROMPT_NARRATIVE) -> str:
    """Prose call (no JSON parsing) — for narrative writing and financial reports.
    STREAMS the response (keeps the connection alive for large max_tokens — avoids the
    non-streaming hang on Streamlit Cloud) and uses a lower effort ('medium') for speed;
    falls back gracefully if the model/SDK doesn't accept the effort parameter."""
    client = _client()
    kw = dict(model=settings.ANTHROPIC_MODEL, max_tokens=settings.AI_MAX_TOKENS,
              system=system, messages=[{"role": "user", "content": prompt}])
    effort = (settings.AI_EFFORT or "").strip().lower()

    def _stream(**extra):
        with client.messages.stream(**kw, **extra) as st:
            return st.get_final_message()

    try:
        msg = _stream(extra_body={"output_config": {"effort": effort}}) if effort in (
            "low", "medium", "high") else _stream()
    except Exception:
        msg = _stream()   # effort not supported -> plain streamed call
    return _fix_pct("".join(getattr(b, "text", "") for b in msg.content).strip())


# ---- Step 11/12: full write-up, financial report, quality assurance ----
NARRATIVE_SECTIONS = [
    ("exec", "Résumé exécutif", "Executive summary"),
    ("positioning", "Positionnement de la SNV (IA2030, stratégie sectorielle de santé, du cMYP à la SNV)",
     "Positioning of the NIS (IA2030, health sector strategy, from cMYP to NIS)"),
    ("situation", "Analyse de la situation — 7 composantes du PEV, FFOM et causes profondes",
     "Situation analysis — 7 EPI components, SWOT and root causes"),
    ("financing", "Éléments de financement (situation macro-économique, budget santé, financement du PEV)",
     "Financing landscape (macro-economy, health budget, EPI financing)"),
    ("vision", "Vision, but et objectif général", "Vision, goal and overall objective"),
    ("objectives", "Priorités et objectifs stratégiques prioritaires (liens avec l’IA2030)",
     "Strategic priorities and priority objectives (links to IA2030)"),
    ("interventions", "Interventions principales par composante", "Main interventions by component"),
    ("special", "Considérations spéciales (COVID-19, campagnes/AVS, nouveaux vaccins, urgences)",
     "Special considerations (COVID-19, campaigns/SIAs, new vaccines, emergencies)"),
    ("me", "Suivi et évaluation — théorie du changement et cadre de S&E",
     "Monitoring & evaluation — theory of change and M&E framework"),
    ("resources", "Besoins en ressources et financement de la SNV", "Resource needs and NIS financing"),
    ("implementation", "Mise en œuvre : hypothèses, risques, mesures d’atténuation et lien avec le POA",
     "Implementation: assumptions, risks, mitigation and link to the AOP"),
    ("conclusion", "Conclusion et prochaines étapes", "Conclusion and next steps"),
]


def _narrative_context(key, s, lang) -> str:
    def comp_label(code):
        from core.epi_components import EPI_COMPONENTS
        return next((c.label(lang) for c in EPI_COMPONENTS if c.code == code), code)
    if key == "exec":
        return (f"Vision: {s.vision.vision}\nBut: {s.vision.goal}\nObjectif: {s.vision.overall_objective}\n"
                f"{len(s.objectives)} objectifs, {len(s.interventions)} interventions, "
                f"{len(s.indicators)} indicateurs, {len(s.activities)} activités.")
    if key == "situation":
        lines = []
        for x in s.swot:
            if any([x.strengths, x.weaknesses, x.opportunities, x.threats]):
                lines.append(f"[{x.subcomponent_code}] F:{'; '.join(x.strengths)} | "
                             f"Fa:{'; '.join(x.weaknesses)} | O:{'; '.join(x.opportunities)} | "
                             f"M:{'; '.join(x.threats)}")
        for rc in s.root_causes:
            lines.append(f"Cause profonde [{rc.subcomponent_code}]: {rc.weakness} ⇒ {rc.final_why}")
        return "\n".join(lines) or "(pas de données FFOM)"
    if key == "vision":
        return f"Vision: {s.vision.vision}\nBut: {s.vision.goal}\nObjectif général: {s.vision.overall_objective}"
    if key == "objectives":
        return "\n".join(f"[{o.obj_id} | {comp_label(o.component_code)}] {o.objective_text} "
                         f"(obstacle: {o.main_obstacle})" for o in s.objectives) or "(aucun objectif)"
    if key == "interventions":
        return "\n".join(f"[{iv.objective_id}] {iv.title} — {iv.rationale} "
                         f"(priorité {getattr(iv.priority_level,'value',iv.priority_level)}; "
                         f"partenaires: {', '.join(iv.partners)})" for iv in s.interventions) or "(aucune)"
    if key == "me":
        return "\n".join(f"{i.name} ({i.indicator_type}) base={i.baseline} "
                         f"cibles={i.targets}" for i in s.indicators) or "(aucun indicateur)"
    if key == "activities":
        return "\n".join(f"[{a.implementation_level}] {a.activity} (resp: {a.lead})"
                         for a in s.activities) or "(aucune activité)"
    if key == "positioning":
        return (f"Pays: {s.profile.country_name}. Période: {s.profile.nis_start_year}-"
                f"{s.profile.nis_start_year + s.profile.nis_duration_years - 1}. Programme: {s.profile.epi_programme_name}. "
                f"Alignement attendu: IA2030 (7 domaines), Gavi 6.0 (2026-2030), stratégie sectorielle santé, "
                f"passage du cMYP/PPAC à la SNV. (Détails à tirer de la SNV rédigée et des documents.)")
    if key == "financing":
        fin = (f"\n\nRAPPORT FINANCIER DISPONIBLE (base-toi dessus):\n{s.financial_report[:12000]}"
               if getattr(s, "financial_report", "") else "")
        return (f"Devise: {s.profile.currency}. Éléments à couvrir: situation macro-économique, budget national "
                f"de santé, financement public et non-étatique (Gavi, UNICEF, partenaires), financement du PEV, "
                f"trajectoire de cofinancement Gavi 6.0. (Chiffres à confirmer par l'équipe pays / NIS.COST.){fin}")
    if key == "special":
        return ("Considérations spéciales à traiter: riposte/déploiement COVID-19, activités de vaccination "
                "supplémentaires (AVS/campagnes), introduction de nouveaux vaccins, vaccination en situations "
                "d'urgence/conflit et populations déplacées, vaccination tout au long de la vie.")
    if key == "resources":
        fin = (f"\n\nRAPPORT FINANCIER DISPONIBLE (base-toi dessus):\n{s.financial_report[:12000]}"
               if getattr(s, "financial_report", "") else "")
        return (f"Base: {len(s.interventions)} interventions et {len(s.activities)} activités à chiffrer. "
                f"Couvrir: besoins en ressources par composante, sources de financement, écart de financement, "
                f"durabilité (cofinancement Gavi 6.0). Chiffres via NIS.COST.{fin}")
    if key == "implementation":
        risks = "; ".join({r for iv in s.interventions for r in iv.risks} | {r for a in s.activities for r in a.risks})
        return (f"Interventions: {len(s.interventions)}; activités: {len(s.activities)}. "
                f"Risques identifiés: {risks[:800] or 'à préciser'}. Couvrir hypothèses, risques et mesures "
                f"d'atténuation, gouvernance de la mise en œuvre, et lien SNV → Plan Opérationnel Annuel (POA).")
    if key == "conclusion":
        return (f"Objectif général: {s.vision.overall_objective}. {len(s.objectives)} objectifs prioritaires, "
                f"{len(s.interventions)} interventions. Prochaines étapes: validation MoH, chiffrage NIS.COST, POA.")
    return ""


def _situation_context(comp, strategy, language):
    """Per-component FFOM + root causes context for the situation analysis."""
    sw = {x.subcomponent_code: x for x in strategy.swot}
    lines = [f"COMPOSANTE PEV : {comp.label(language)}", "", "FFOM par sous-composante :"]
    for sub in comp.subcomponents:
        it = sw.get(sub.code)
        if not it:
            continue
        lines.append(f"- {sub.label(language)} :")
        if it.strengths: lines.append(f"    Forces: {'; '.join(it.strengths)}")
        if it.weaknesses: lines.append(f"    Faiblesses: {'; '.join(it.weaknesses)}")
        if it.opportunities: lines.append(f"    Opportunités: {'; '.join(it.opportunities)}")
        if it.threats: lines.append(f"    Menaces: {'; '.join(it.threats)}")
    rcs = [rc for rc in strategy.root_causes if rc.component_code == comp.code]
    if rcs:
        lines.append("\nCauses profondes (POURQUOI) :")
        for rc in rcs[:12]:
            lines.append(f"- {rc.weakness} ⇒ {rc.final_why}")
    return "\n".join(lines)


def _narrative_documents(strategy):
    """Source documents + built-in IA2030/Gavi reference tables, for grounding the write-up."""
    docs = list(getattr(strategy, "documents", []) or [])
    try:
        from core import reference_docs
        docs += reference_docs.get_reference_documents()
    except Exception:
        pass
    return docs


def _generate_situation_by_component(strategy, language, progress=None, base=0, total=0):
    """Deep situation analysis: one sub-section per EPI component (## heading)."""
    from core.epi_components import EPI_COMPONENTS
    parts = []
    draft = getattr(strategy, "snv_draft_text", "")
    docs = _narrative_documents(strategy)
    for j, comp in enumerate(EPI_COMPONENTS):
        if progress:
            progress(base + j, total, f"Analyse situation — {comp.label(language)}")
        try:
            ctx = _situation_context(comp, strategy, language)
            prose = _call_claude_text(build_narrative_prompt(
                strategy.profile, language, f"Analyse de la composante « {comp.label(language)} »",
                ctx, draft, documents=docs))
        except Exception as e:
            prose = f"[Erreur: {e}]"
        parts.append(f"## {comp.label(language)}\n{prose}")
    return "\n\n".join(parts)


def generate_narrative(strategy, language: str, progress=None) -> dict:
    """Write polished prose for every NIS section; store in strategy.narrative.
    The situation analysis is generated component-by-component for depth."""
    from core.epi_components import EPI_COMPONENTS
    from concurrent.futures import ThreadPoolExecutor, as_completed
    all_docs = _narrative_documents(strategy)
    draft = getattr(strategy, "snv_draft_text", "")
    # Only the document-dependent chapters carry the source documents (lighter, faster calls).
    DOC_SECTIONS = {"exec", "positioning", "situation", "financing", "special"}
    total = len(NARRATIVE_SECTIONS)

    def _ctx_for(key):
        if key == "situation":
            return (_narrative_context(key, strategy, language)
                    + "\n\nDÉTAIL PAR COMPOSANTE (FFOM + causes profondes) :\n"
                    + "\n\n".join(_situation_context(c, strategy, language) for c in EPI_COMPONENTS)
                    + "\n\n(STRUCTURE OBLIGATOIRE : rédige une sous-partie « ## <nom de la composante> » "
                      "pour CHACUNE des 7 composantes du PEV, approfondie et chiffrée.)")
        return _narrative_context(key, strategy, language)

    def _run(key, title):   # runs in a worker thread — no Streamlit access here
        docs = all_docs if key in DOC_SECTIONS else None
        return _call_claude_text(build_narrative_prompt(
            strategy.profile, language, title, _ctx_for(key), draft=draft, documents=docs))

    tasks = [(key, (fr if language == "fr" else en)) for (key, fr, en) in NARRATIVE_SECTIONS]
    out = {}
    workers = max(1, min(int(getattr(settings, "AI_CONCURRENCY", 4)), total))
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:   # sections are independent -> parallel
        futs = {ex.submit(_run, key, title): (key, title) for key, title in tasks}
        for fut in as_completed(futs):
            key, title = futs[fut]
            try:
                out[key] = fut.result()
            except Exception as e:
                out[key] = f"[Erreur de rédaction: {e}]"
            if progress:   # as_completed runs in the caller (main) thread -> UI-safe
                progress(done, total, title)
            done += 1
    strategy.narrative = {key: out.get(key, "") for key, _, _ in NARRATIVE_SECTIONS}
    return strategy.narrative


def generate_financial(profile, language: str, niscost_text: str) -> str:
    return _call_claude_text(build_financial_prompt(profile, language, niscost_text))


def generate_qa(profile, language: str, document_text: str) -> dict:
    return _call_claude(build_qa_prompt(profile, language, document_text))


def _call_claude(prompt: str) -> dict:
    """Structured-JSON call. STREAMS the response (keeps the connection alive — avoids the
    non-streaming hang on Streamlit Cloud) with a lower effort for speed; retries on invalid JSON."""
    client = _client()
    last_err = None
    truncated = False
    effort = (settings.AI_EFFORT or "").strip().lower()
    use_effort = [effort in ("low", "medium", "high")]   # list = mutable flag for the closure

    def _stream(p):
        kw = dict(model=settings.ANTHROPIC_MODEL, max_tokens=settings.AI_MAX_TOKENS,
                  system=SYSTEM_PROMPT, messages=[{"role": "user", "content": p}])
        if use_effort[0]:
            try:
                with client.messages.stream(**kw, extra_body={"output_config": {"effort": effort}}) as s:
                    return s.get_final_message()
            except Exception:
                use_effort[0] = False   # effort not supported -> stop trying it
        with client.messages.stream(**kw) as s:
            return s.get_final_message()

    for attempt in range(settings.AI_MAX_RETRIES + 1):
        suffix = "" if attempt == 0 else \
            "\n\nIMPORTANT: Your previous reply was not valid JSON. Reply with ONE valid JSON object only, " \
            "and keep it concise enough to finish completely."
        try:
            msg = _stream(prompt + suffix)
        except Exception as e:
            last_err = e
            continue
        truncated = getattr(msg, "stop_reason", None) == "max_tokens"
        text = "".join(getattr(b, "text", "") for b in msg.content)
        try:
            return _extract_json(text)
        except Exception as e:
            last_err = e
    if truncated:
        raise AIError("réponse trop longue (coupée par la limite de tokens). "
                      "Réessayez ; la génération est désormais découpée pour éviter cela.")
    raise AIError(f"JSON invalide après {settings.AI_MAX_RETRIES + 1} tentatives: {last_err}")


# --------------------------------------------------------------------------- #
# Section-level generation
# --------------------------------------------------------------------------- #
def generate_section(section: str, profile: CountryProfile,
                     documents: list[UploadedDocument], language: str, progress=None,
                     strategy=None) -> dict:
    """Return the raw validated dict for a section (caller maps it onto the model).

    SWOT is generated component-by-component. Root causes are generated from the FFOM
    weaknesses (the AI applies the 5-Whys to each), not freshly invented from documents.
    """
    if section not in SECTIONS:
        raise ValueError(section)
    # Append the IA2030/Gavi CODE tables only where exact codes matter (objectives, interventions,
    # indicators, activities) — SWOT & root causes are diagnostic and don't need them (keeps calls light).
    CODE_SECTIONS = {"objectives", "interventions", "indicators", "activities"}
    if section in CODE_SECTIONS:
        try:
            from core import reference_docs
            documents = list(documents) + reference_docs.get_reference_documents()
        except Exception:
            pass
    if section == "swot":
        return _generate_swot_chunked(profile, documents, language, progress, strategy)
    if section == "root_causes" and strategy is not None:
        rc = _generate_root_causes_from_weaknesses(profile, documents, language, strategy, progress)
        if rc["items"]:
            return rc
        # no FFOM weaknesses yet -> fall back to the document-based prompt
    if section == "interventions" and strategy is not None and strategy.objectives:
        iv = _generate_interventions_from_objectives(profile, documents, language, strategy, progress)
        if iv["items"]:
            return iv
    if section == "indicators" and strategy is not None:
        ind = _generate_indicators_from_objectives(profile, documents, language, strategy, progress)
        if ind["items"]:
            return ind
    if section == "activities" and strategy is not None and strategy.interventions:
        act = _generate_activities_from_interventions(profile, documents, language, strategy, progress)
        if act["items"]:
            return act
    prompt = build_generation_prompt(profile, documents, language, section)
    return _call_claude(prompt)


def _generate_activities_from_interventions(profile, documents, language, strategy, progress=None) -> dict:
    """Break each main intervention into fully-completed key activities (grouped per component)."""
    from core.epi_components import EPI_COMPONENTS
    iv_by_comp: dict[str, list] = {}
    for iv in strategy.interventions:
        if (iv.title or "").strip():
            iv_by_comp.setdefault(iv.component_code or "?", []).append(iv)
    items = []
    groups = list(iv_by_comp.items())
    for i, (comp_code, ivs) in enumerate(groups):
        comp = next((c for c in EPI_COMPONENTS if c.code == comp_code), None)
        label = comp.label(language) if comp else "Interventions"
        if progress:
            progress(i, len(groups), label)
        try:
            data = _call_claude(build_activity_prompt(profile, documents, language, label, ivs))
            items.extend(_items(data))
        except Exception:
            pass
    return {"items": items}


def _generate_indicators_from_objectives(profile, documents, language, strategy, progress=None) -> dict:
    """≥1 fully-completed M&E indicator per objective, with targets for ALL years."""
    from core.epi_components import EPI_COMPONENTS
    objs_by_comp: dict[str, list] = {}
    for o in strategy.objectives:
        if (o.objective_text or "").strip():
            objs_by_comp.setdefault(o.component_code or "?", []).append(o)
    if objs_by_comp:
        groups = list(objs_by_comp.items())
    else:
        # No objectives yet -> derive key indicators per component from the reference documents.
        groups = [(c.code, []) for c in EPI_COMPONENTS]
    items = []
    for i, (comp_code, objs) in enumerate(groups):
        comp = next((c for c in EPI_COMPONENTS if c.code == comp_code), None)
        label = comp.label(language) if comp else "Objectifs"
        if progress:
            progress(i, len(groups), label)
        try:
            prompt = build_indicator_prompt(profile, documents, language, label, objs)
            data = _call_claude(prompt)
            items.extend(_items(data))
        except Exception:
            pass
    return {"items": items}


def _generate_interventions_from_objectives(profile, documents, language, strategy, progress=None) -> dict:
    """For each strategic objective, generate fully-completed, evidence-grounded interventions
    (grouped per component to keep responses valid). Consults the uploaded documents."""
    from core.epi_components import EPI_COMPONENTS, find_subcomponent
    objs_by_comp: dict[str, list] = {}
    for o in strategy.objectives:
        if (o.objective_text or "").strip():
            objs_by_comp.setdefault(o.component_code or "?", []).append(o)
    items = []
    groups = list(objs_by_comp.items())
    for i, (comp_code, objs) in enumerate(groups):
        comp = next((c for c in EPI_COMPONENTS if c.code == comp_code), None)
        label = comp.label(language) if comp else "Objectifs"
        if progress:
            progress(i, len(groups), label)
        try:
            prompt = build_intervention_prompt(profile, documents, language, label, objs)
            data = _call_claude(prompt)
            items.extend(_items(data))
        except Exception:
            pass
    return {"items": items}


def _generate_root_causes_from_weaknesses(profile, documents, language, strategy, progress=None) -> dict:
    """For each FFOM weakness, ask the AI to apply the 5-Whys (its reasoning, informed by the
    reference documents/directives) per component."""
    from core.epi_components import EPI_COMPONENTS
    weak_by_comp: dict[str, list] = {}
    for sw in strategy.swot:
        for w in sw.weaknesses:
            if w and w.strip():
                weak_by_comp.setdefault(sw.component_code, []).append((sw.subcomponent_code, w.strip()))
    comps = [c for c in EPI_COMPONENTS if weak_by_comp.get(c.code)]
    items = []
    for i, comp in enumerate(comps):
        if progress:
            progress(i, len(comps), comp.label(language))
        try:
            prompt = build_root_cause_prompt(profile, documents, language, comp, weak_by_comp[comp.code])
            data = _call_claude(prompt)
            items.extend(_items(data))
        except Exception:
            pass
    return {"items": items}


def _weak_by_sub(strategy) -> dict:
    out: dict[str, list] = {}
    if strategy is not None:
        for sw in strategy.swot:
            ws = [(sw.subcomponent_code, w.strip()) for w in sw.weaknesses if w and w.strip()]
            if ws:
                out[sw.subcomponent_code] = ws
    return out


def regenerate_swot_subset(profile, documents, language, strategy, sub_codes, progress=None) -> dict:
    """Regenerate FFOM for specific subcomponents only (e.g. the ones still empty)."""
    from core.epi_components import find_subcomponent
    weak_by_sub = _weak_by_sub(strategy)
    targets = [t for t in (find_subcomponent(c) for c in sub_codes) if t]
    items, errors = [], []
    for i, (comp, sub) in enumerate(targets):
        if progress:
            progress(i, len(targets), sub.label(language))
        try:
            data = _call_claude(build_swot_prompt(profile, documents, language, comp,
                                                  weak_by_sub.get(sub.code), only_subs=[sub], doc_budget=18000))
            chunk = _items(data)
            _assign_subcomponents(comp, chunk, candidate_subs=[sub])
            items.extend(chunk)
        except Exception as e:
            errors.append(f"{sub.code}: {e}")
    return {"items": items, "_errors": errors}


def _items(data) -> list:
    """Tolerant extraction: accept {'items':[...]}, a bare list, or the first list-valued field."""
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    if isinstance(data.get("items"), list):
        return data["items"]
    for v in data.values():
        if isinstance(v, list):
            return v
    return []


def _generate_swot_chunked(profile, documents, language, progress=None, strategy=None) -> dict:
    """Generate the FFOM/SWOT ONE SUBCOMPONENT AT A TIME (26 small calls). Small responses never
    get truncated, so coverage is reliable. Builds on any already-documented weaknesses."""
    from core.epi_components import subcomponent_pairs
    weak_by_sub: dict[str, list] = {}
    if strategy is not None:
        for sw in strategy.swot:
            ws = [(sw.subcomponent_code, w.strip()) for w in sw.weaknesses if w and w.strip()]
            if ws:
                weak_by_sub[sw.subcomponent_code] = ws
    pairs = subcomponent_pairs()  # [(component, subcomponent), ...] — the 26
    items, errors = [], []
    for i, (comp, sub) in enumerate(pairs):
        if progress:
            progress(i, len(pairs), sub.label(language))
        try:
            data = _call_claude(build_swot_prompt(profile, documents, language, comp,
                                                  weak_by_sub.get(sub.code), only_subs=[sub], doc_budget=18000))
            chunk = _items(data)
            _assign_subcomponents(comp, chunk, candidate_subs=[sub])
            items.extend(chunk)
        except Exception as e:
            errors.append(f"{sub.code}: {e}")
    if not items and errors:
        raise AIError("FFOM non générée — " + " · ".join(errors[:5]))
    return {"items": items, "_errors": errors}


def _resolve_sub(comp, item: dict):
    """Find which subcomponent of `comp` an AI item belongs to: by code, then by label."""
    text = f"{item.get('subcomponent_code', '')} {item.get('component_code', '')}"
    m = re.search(r"\d+\.\d+", str(text))
    if m:
        found = find_subcomponent(m.group())
        if found and found[1] in comp.subcomponents:
            return found[1]
    low = str(item.get("subcomponent_code", "") or "").strip().lower()
    if low:
        for sub in comp.subcomponents:
            for lbl in (sub.label_fr.lower(), sub.label_en.lower()):
                # compare ignoring the leading code (e.g. "1.1 politiques…" -> "politiques…")
                lbl_text = lbl.split(" ", 1)[-1] if lbl[:1].isdigit() else lbl
                if low in lbl or lbl in low or (lbl_text and lbl_text in low):
                    return sub
    return None


def _assign_subcomponents(comp, chunk: list, candidate_subs=None) -> None:
    """Ensure every item maps to one of the component's subcomponents (restricted to
    candidate_subs when given, e.g. for gap-fill). Resolution: code → label → positional."""
    subs = list(candidate_subs) if candidate_subs else comp.subcomponents
    if not subs:
        return
    used = set()
    for idx, it in enumerate(chunk):
        sub = _resolve_sub(comp, it)
        if sub is None or sub not in subs or sub.code in used:
            sub = next((s for s in subs if s.code not in used), None)
        if sub is None:
            sub = subs[min(idx, len(subs) - 1)]
        used.add(sub.code)
        it["component_code"] = comp.code
        it["subcomponent_code"] = sub.code


def apply_section(strategy: NISStrategy, section: str, data: dict) -> None:
    """Map a section's JSON payload onto the NISStrategy in place."""
    if section == "vision":
        strategy.vision = CountryVision(**_clean(data, CountryVision))
    elif section == "swot":
        new = [_fix_codes(SWOTItem(**_clean(x, SWOTItem))) for x in _items(data)]
        _merge_swot(strategy, new)
    elif section == "root_causes":
        strategy.root_causes = [_fix_codes(RootCauseAnalysis(**_clean(x, RootCauseAnalysis)))
                                for x in _items(data)]
    elif section == "objectives":
        strategy.objectives = [_fix_codes(StrategicObjective(**_clean(x, StrategicObjective)))
                               for x in _items(data)]
    elif section == "interventions":
        out = []
        for x in _items(data):
            sc = x.pop("score", {}) or {}
            iv = Intervention(**_clean(x, Intervention))
            iv.score = PrioritizationScore(**_clean(sc, PrioritizationScore))
            iv.priority_level = iv.score.level()
            out.append(_fix_codes(iv))
        strategy.interventions = out
    elif section == "indicators":
        inds = [_fix_codes(MEIndicator(**_clean(x, MEIndicator))) for x in _items(data)]
        years = getattr(strategy.profile, "nis_duration_years", 5)
        for ind in inds:
            _carry_forward_targets(ind, years)
        strategy.indicators = inds
    elif section == "activities":
        strategy.activities = [_fix_codes(Activity(**_clean(x, Activity)))
                               for x in _items(data)]


def _merge_swot(strategy, new_items) -> None:
    """Merge generated SWOT into existing (preserve imported weaknesses; dedup by text)."""
    by = {x.subcomponent_code: x for x in strategy.swot}
    for it in new_items:
        cur = by.get(it.subcomponent_code)
        if cur is None:
            by[it.subcomponent_code] = it
            continue
        for f in ("strengths", "weaknesses", "opportunities", "threats"):
            merged = list(getattr(cur, f))
            for v in getattr(it, f):
                if v and v.strip() and v not in merged:
                    merged.append(v)
            setattr(cur, f, merged)
        cur.evidence = (cur.evidence or []) + (it.evidence or [])
    strategy.swot = list(by.values())


def _carry_forward_targets(indicator, years: int) -> None:
    """Ensure every year Y1..Yn has a target; fill any blank year with the last known value
    (so years 4-5 are never empty). Does not invent new figures — it maintains the last target."""
    t = dict(indicator.targets or {})
    last = ""
    for k in range(years):
        y = f"Y{k + 1}"
        v = str(t.get(y, "") or "").strip()
        if v:
            last = v
        elif last:
            t[y] = last
    indicator.targets = t


def _fix_codes(obj):
    """Normalize AI-returned codes to exact subcomponent codes.

    Finds a 'X.Y' pattern anywhere in subcomponent_code or component_code, e.g.
    '1.1 Politiques…', 'Sous-composante 1.1', 'Composante 1 — 1.1' all map to '1.1' / '1'.
    """
    for field in ("subcomponent_code", "component_code"):
        raw = getattr(obj, field, "") or ""
        m = re.search(r"\d+\.\d+", str(raw))
        if m:
            found = find_subcomponent(m.group())
            if found:
                obj.component_code = found[0].code
                obj.subcomponent_code = found[1].code
                break
    return obj


def _clean(d: dict, model_cls) -> dict:
    """Keep only known fields (schema drift tolerance)."""
    try:
        fields = set(model_cls.model_fields.keys())  # pydantic v2
    except AttributeError:
        fields = set(model_cls.__fields__.keys())    # pydantic v1
    return {k: v for k, v in (d or {}).items() if k in fields}


# --------------------------------------------------------------------------- #
# Central orchestrator (spec §10)
# --------------------------------------------------------------------------- #
def generate_nis_strategy(country_profile: CountryProfile, documents: list[UploadedDocument],
                          language: str, years: int, sections: list[str] | None = None,
                          progress=None) -> NISStrategy:
    """Generate the full strategy. `progress(section, i, n)` is an optional callback."""
    country_profile.nis_duration_years = years
    country_profile.language = language
    strategy = NISStrategy(profile=country_profile, documents=documents)
    todo = sections or SECTIONS
    if not settings.ai_available():
        return offline_scaffold(strategy)
    for i, section in enumerate(todo):
        if progress:
            progress(section, i, len(todo))
        data = generate_section(section, country_profile, documents, language)
        apply_section(strategy, section, data)
    return strategy


def offline_scaffold(strategy: NISStrategy) -> NISStrategy:
    """Build empty editable rows for all 26 subcomponents (no API key / manual mode)."""
    strategy.swot = [SWOTItem(component_code=c.code, subcomponent_code=s.code)
                     for c, s in subcomponent_pairs()]
    return strategy
