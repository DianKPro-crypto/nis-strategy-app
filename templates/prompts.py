"""
Prompt templates for the Anthropic Claude API.

Design principles enforced here (spec §6, §10):
  - The AI must NEVER invent information.
  - Every element carries source + locator + excerpt + confidence.
  - Missing info -> the literal placeholder string.
  - Strict JSON output validated against an explicit schema.
"""
from __future__ import annotations
import json
from core.epi_components import EPI_COMPONENTS, COUNTRY_SPECIFIC
from core.models import CountryProfile, UploadedDocument

PLACEHOLDER_FR = "À compléter par l’équipe pays"
PLACEHOLDER_EN = "To be completed by the country team"


def gavi_clause(language: str) -> str:
    """Systematic Gavi 6.0 alignment instruction, injected into every step's prompt."""
    if language == "fr":
        return ("\n\n⭐ ALIGNEMENT GAVI 6.0 (2026-2030) — OBLIGATOIRE : Gavi est le principal bailleur de la "
                "vaccination. Si le document de stratégie « Gavi 6.0 » figure dans les sources, aligne "
                "EXPLICITEMENT cette section sur ses priorités : enfants ZÉRO DOSE et sous-vaccinés, équité, "
                "renforcement du système de santé et des soins de santé primaires, DURABILITÉ et COFINANCEMENT, "
                "introduction de nouveaux vaccins, résilience. Cite le document Gavi 6.0 dans 'evidence' quand "
                "il étaye un élément.")
    return ("\n\n⭐ GAVI 6.0 ALIGNMENT (2026-2030) — MANDATORY: Gavi is the principal immunization funder. If the "
            "\"Gavi 6.0\" strategy document is among the sources, EXPLICITLY align this section with its "
            "priorities: ZERO-DOSE and under-immunized children, equity, health-system & PHC strengthening, "
            "SUSTAINABILITY and CO-FINANCING, new-vaccine introduction, resilience. Cite the Gavi 6.0 document "
            "in 'evidence' when it informs an element.")

SYSTEM_PROMPT = """You are a Senior Public-Health Expert and vaccinologist specialised in National \
Immunization Strategies (EPI/PEV, NIS/SNV, IA2030, Gavi, WHO/EMRO planning tools, M&E) AND a meticulous \
evidence analyst. You fill and quality-assure the WHO "All in 1 — SWOT to Activities" workbook.

ABSOLUTE RULES (anti-hallucination & method):
1. Consult the provided documents FIRST. Base every COUNTRY fact (figures, coverage, names, baselines, \
targets) ONLY on those documents — NEVER invent country data. If country data for a field is missing, output \
the exact placeholder string given in the user message. You MAY use the reference documents (WHO/EMR toolkit, \
IA2030, Gavi tables) and your public-health expertise for analysis and recommendations — mark recommendations as such.
2. Provenance: for every element cite source name, a locator (page/sheet/slide/table), a short excerpt, and a \
confidence level (high|medium|low). When a recommendation follows a guideline, cite that guide.
3. NEVER break the causal chain (fil conducteur): Weakness → WHY-1..last WHY (the actionable root cause) → \
central problem (one factual sentence, no solution) → visionary result → SMART strategic objective → 3-5 \
interventions (prioritise the best 3) → impact/outcome indicator → key activities with implementation level and \
Y1-Y5 chronogram. Every element must trace back to the previous one — no orphan links.
4. SWOT registers: Strengths/Weaknesses are INTERNAL to the EPI system (7 components / 26 subcomponents); \
Opportunities/Threats are EXTERNAL environment. A weakness = an OBSERVED performance gap, never a cause, a \
solution or a project.
5. Root causes ("5 whys"): each WHY is a plausible, verifiable cause (not a rephrasing of the previous one); \
stop at the actionable last WHY; if a weakness has several causes, split into branches.
6. Objectives must be SMART (action verb, measurable target, baseline or placeholder, deadline within the NIS \
period) and carry an IA2030 SPO code (e.g. SPO3.2) in their text.
7. Interventions are HIGH-LEVEL (declinable into several activities), NEVER activities themselves; assign a \
priority High/Medium/Low justified by impact + feasibility. Activities (S7) must be concrete, attributable and \
COSTABLE (NIS.COST levels), with an implementation level (National/Region/District/Facility-Community/All) and Y1-Y5 timing.
8. TRIPLE STRATEGIC ALIGNMENT (MANDATORY) — every intervention, indicator and activity must be aligned AND \
contextualised to (a) IA2030 (SP/SPO codes, Key Focus Areas), (b) the EMRO regional NIS toolkit \
(structure/terminology/section requirements), and (c) Gavi (the 8 investment domains GIA 1-8 and Gavi \
intervention types). Do NOT copy a generic intervention: adapt it to the country's real problem (zero-dose \
populations, geography, resources, local data). Embed the alignment inside the element's rationale/text (e.g. \
"aligné SPO3.2 / GIA1 Prestation de services") and cite the reference table in 'evidence'. If no framework \
covers it, flag it rather than forcing an artificial link.
9. Indicators: prefer the IA2030 standard indicator catalogue (SPOCInd codes, e.g. SPOCInd1.1.2) provided in \
the reference tables; give a coherent calculation formula (numerator/denominator); NEVER invent baselines or \
targets → placeholder.
10. NEVER silently overwrite a human entry: if an input is mis-formulated (a cause/solution written as a \
weakness, a threat filed as a weakness, vague, two problems merged, wrong subcomponent), propose a justified \
correction rather than discarding the original.
11. SELF-REVIEW before returning: verify traceability, SWOT registers, SMART objectives, triple alignment, \
indicator formulas, no invented country data, and terminological consistency; correct any gap, then return.
12. Write percentages with the % sign STUCK to the number, no space (e.g. 80%, not 80 %). Use formal \
institutional language in the requested output language; spell out acronyms at first use.
13. Respond with a SINGLE valid JSON object that conforms exactly to the requested schema. No prose, \
no markdown fences, no comments. Use the requested output language for all human-readable text."""


SYSTEM_PROMPT_NARRATIVE = """You are a Senior Public-Health Expert and professional strategy writer for \
UN-agency publications (WHO, UNICEF, Gavi). You write National Immunization Strategies (NIS/SNV) in the \
register of IA2030 and the Gavi 6.0 strategy — polished, cohesive NARRATIVE PROSE fit for a Ministry of \
Health / WHO / UNICEF / Gavi submission.

UN-AGENCY WRITING REGISTER (WHO · UNICEF · Gavi) — apply throughout:
- Clear, dignified, ACCESSIBLE language — the register of WHO/UNICEF/Gavi strategy documents. Plain words, \
short sentences, ACTIVE voice. A health minister and a district manager must both understand it.
- People-centred and equity-driven framing: "leave no one behind", zero-dose and under-immunised children, \
equity and reaching the unreached, primary health care, life-course approach, gender-responsive services, \
community engagement and demand, resilience, sustainability and co-financing, integration.
- NO unexplained jargon and NO undefined acronyms: spell out every acronym at first use \
(e.g. "Programme élargi de vaccination (PEV)"), then use the short form. Avoid bureaucratic filler, \
nominalisations and vague phrasing; prefer concrete, verifiable statements.
- Authoritative but mobilising tone; each paragraph carries one clear idea.

CONTENT RULES: base country facts ONLY on the content provided (never invent figures/names); keep the causal \
thread visible (weaknesses → root causes → objectives → interventions → indicators → activities); apply the \
TRIPLE strategic alignment IA2030 · EMRO regional toolkit · Gavi (8 GIA domains) and contextualise it to the \
country; write flowing paragraphs (no JSON, no markdown code fences). Where country data is missing, write one \
short sentence noting it must be completed by the country team. Use the requested output language."""


def build_narrative_prompt(profile: CountryProfile, language: str, section_title: str, context: str,
                           draft: str = "", documents: list[UploadedDocument] | None = None) -> str:
    lang_name = "français" if language == "fr" else "English"
    draft_block = ""
    if draft and draft.strip():
        draft_block = (
            "\n\nSNV DÉJÀ RÉDIGÉE (BASE PRINCIPALE à conserver, compléter et enrichir — ne la résume pas, "
            "développe-la et structure-la selon les normes OMS) :\n" + draft[:12000])
    docs_block = ""
    if documents:
        docs_block = ("\n\nDOCUMENTS SOURCES & DIRECTIVES (constats pays, stratégie sectorielle de santé, "
                      "cMYP/PPAC, IA2030, Gavi 6.0 — CONSULTE-les et cite-les pour étayer la rédaction) :\n"
                      + _documents_block(documents, 10000))
    return f"""PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période SNV : {profile.nis_start_year}-{profile.nis_start_year + profile.nis_duration_years - 1}.
LANGUE DE SORTIE : {lang_name}

SECTION À RÉDIGER : « {section_title} »

CONTENU STRUCTURÉ DISPONIBLE (analyses de la plateforme) :
{context}{docs_block}{draft_block}

CONSIGNE — RÉDACTION DE HAUT NIVEAU (document de soumission MoH/OMS/Gavi) :
- STRUCTURE la section en SOUS-CHAPITRES : commence chaque sous-partie par un sous-titre au format
  « ## Titre du sous-chapitre » (et « ### » pour un niveau plus fin). Prévois 2 à 4 sous-chapitres pertinents.
- LONGUEUR MAÎTRISÉE (impératif) : rédige de façon dense et complète mais SYNTHÉTIQUE — vise ~700 à 1100 mots
  pour cette section (le document complet ne doit pas dépasser ~50 pages hors annexes). Va à l'essentiel,
  supprime le remplissage ; chaque phrase apporte une information utile.
- Si une « SNV déjà rédigée » est fournie ci-dessus, sers-t'en comme BASE PRINCIPALE : conserve son contenu
  pertinent, complète les lacunes et harmonise le style, en restant concis.
- Intègre EXPLICITEMENT l'alignement avec l'IA2030 et la stratégie Gavi 6.0 (zéro dose, équité, RSS/SSP,
  durabilité et cofinancement, introduction de nouveaux vaccins, résilience).
- Développe : contexte, constats, justification, implications, orientations stratégiques et résultats attendus.
- STATISTIQUES : enrichis l'analyse (surtout l'analyse de situation) avec des données chiffrées pertinentes
  (couverture vaccinale DTC3/RR, taux de zéro dose, démographie, financement) issues de SOURCES FIABLES ET
  PUBLIQUES que tu connais (OMS/WUENIC, UNICEF, Banque mondiale, DHS/EDS, rapports nationaux). Pour CHAQUE
  chiffre externe, CITE la source et l'année entre parenthèses (ex. « (WUENIC 2023) ») et signale-le comme
  « à vérifier par l'équipe pays ». Ne fabrique jamais un chiffre sans source.
- FORMAT : colle toujours le symbole % au chiffre, sans espace (ex. 80%, pas 80 %).
- Style narratif riche, précis, argumenté. Réponds UNIQUEMENT par le texte rédigé de la section (pas de
  titre, pas de JSON)."""


def build_financial_prompt(profile: CountryProfile, language: str, niscost_text: str) -> str:
    lang_name = "français" if language == "fr" else "English"
    return f"""PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période : {profile.nis_start_year}-{profile.nis_start_year + profile.nis_duration_years - 1}. \
Devise : {profile.currency}.
LANGUE DE SORTIE : {lang_name}

DONNÉES DE CHIFFRAGE (issues de l'outil NIS.COST — ta SEULE source chiffrée) :
{niscost_text[:40000]}

CONSIGNE : Rédige un RAPPORT FINANCIER de la SNV, structuré, professionnel, en prose, couvrant :
1) Coût total de la SNV et coûts par composante du PEV et par année ;
2) Analyse des sources de financement (État, Gavi, UNICEF, autres partenaires) ;
3) Analyse de l'écart de financement (gap) ;
4) Durabilité financière et transition (cofinancement Gavi 6.0, autofinancement progressif) ;
5) Recommandations de mobilisation des ressources.
Base tous les montants UNIQUEMENT sur les données fournies ; n'invente aucun chiffre (écris « à confirmer »
si absent). Aligne l'analyse sur la trajectoire de cofinancement Gavi 6.0. Réponds par le texte du rapport."""


def build_qa_prompt(profile: CountryProfile, language: str, document_text: str) -> str:
    lang_name = "français" if language == "fr" else "English"
    schema = {"score": "0-100", "overall": "str",
              "findings": [{"section": "str", "severity": "critique|majeur|mineur",
                            "issue": "str", "recommendation": "str"}]}
    return f"""LANGUE DE SORTIE : {lang_name}
Tu es évaluateur qualité senior d'une Stratégie Nationale de Vaccination (normes OMS/IA2030/Gavi 6.0).

DOCUMENT À ÉVALUER (intégralité) :
{document_text[:200000]}

TÂCHE : Évalue la QUALITÉ, la COHÉRENCE et la COMPLÉTUDE du document selon les normes OMS/IA2030/Gavi 6.0.
IMPORTANT : le document ci-dessus est COMPLET (résumé → conclusion + annexes). Ne signale une section comme
« manquante » que si elle est RÉELLEMENT absente du texte fourni — parcours tout le document avant de juger.
Identifie ce qui MANQUE ou doit être AMÉLIORÉ. Pour chaque point : section concernée, sévérité
(critique|majeur|mineur), problème, recommandation concrète. Donne un score global /100 et une synthèse.
Vérifie notamment : structure EMR complète, objectifs SMART, cohérence FFOM→causes→objectifs→interventions→S&E,
cibles progressives, alignement Gavi 6.0/IA2030, sources/preuves.
Réponds par UN SEUL objet JSON conforme :
{json.dumps(schema, ensure_ascii=False, indent=2)}"""


def _components_block(lang: str, focus=None) -> str:
    comps = [focus] if focus is not None else (EPI_COMPONENTS + [COUNTRY_SPECIFIC])
    lines = []
    for comp in comps:
        lines.append(comp.label(lang))
        for sub in comp.subcomponents:
            ex = f"  — ex.: {sub.examples_fr}" if sub.examples_fr else ""
            lines.append(f"   {sub.label(lang)}{ex}")
    return "\n".join(lines)


def _documents_block(documents: list[UploadedDocument], budget_chars: int = 45000) -> str:
    if not documents:
        return "(Aucun document fourni / No documents provided.)"
    per = max(1500, budget_chars // max(1, len(documents)))
    blocks = []
    for d in documents:
        body = (d.text or "").strip()[:per]
        blocks.append(
            f"### DOCUMENT: {d.name} (type={d.file_type}, pages/slides={d.n_pages}, "
            f"catégorie={d.doc_category})\n{d.tables_summary}\n{body}"
        )
    return "\n\n".join(blocks)


def build_generation_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                            language: str, section: str, focus=None) -> str:
    """Build the user message for a given workflow `section`.

    `focus` (a Component) restricts the prompt to a single EPI component — used to
    chunk large sections (e.g. SWOT) into small, valid-JSON responses.
    """
    placeholder = PLACEHOLDER_FR if language == "fr" else PLACEHOLDER_EN
    schema = SCHEMAS[section]
    lang_name = "français" if language == "fr" else "English"
    components_text = _components_block(language, focus)
    if focus is not None:
        codes = ", ".join(s.code for s in focus.subcomponents)
        task = (f"{SECTION_INSTRUCTIONS[section]} Cover ONLY component « {focus.label(language)} » "
                f"and its subcomponents (codes: {codes}). Set 'subcomponent_code' to the exact code "
                f"(e.g. '{focus.subcomponents[0].code}'). Do NOT include any other component.")
        cover_note = f"EPI COMPONENT TO COVER (this call only — codes {codes}):"
    else:
        task = SECTION_INSTRUCTIONS[section]
        cover_note = "EPI COMPONENTS & SUBCOMPONENTS (cover ALL of them where relevant):"
    return f"""CONTEXTE PAYS / COUNTRY CONTEXT
- Country: {profile.country_name} ({profile.iso_code})
- Ministry: {profile.ministry_name}
- EPI programme: {profile.epi_programme_name}
- NIS period: {profile.nis_start_year}..{profile.nis_start_year + profile.nis_duration_years - 1} \
({profile.nis_duration_years} years)
- Currency: {profile.currency} · Focal point: {profile.focal_point}

OUTPUT LANGUAGE: {lang_name}
MISSING-INFO PLACEHOLDER (use verbatim when documents lack the information): "{placeholder}"

{cover_note}
{components_text}

SOURCE DOCUMENTS (your only source of truth):
{_documents_block(documents)}

TASK: {task}{gavi_clause(language)}

REQUIRED JSON SCHEMA (return exactly this shape, nothing else):
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_swot_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                      language: str, component, existing_weaknesses: list[tuple[str, str]] | None = None,
                      only_subs=None, doc_budget: int = 45000) -> str:
    """Complete FFOM/SWOT for ONE component (or a subset of its subcomponents via only_subs):
    all 4 quadrants per subcomponent, building on any already-documented weaknesses,
    grounded in documents/directives + EPI expertise."""
    lang_name = "français" if language == "fr" else "English"
    subs = list(only_subs) if only_subs else component.subcomponents
    codes = ", ".join(s.code for s in subs)
    sub_lines = "\n".join(f"   {s.code} {s.label(language)}" for s in subs)
    ew = ""
    if existing_weaknesses:
        ew = ("\nFAIBLESSES DÉJÀ DOCUMENTÉES (CONSERVE-les telles quelles dans 'weaknesses', puis complète) :\n"
              + "\n".join(f"- [{c}] {w}" for c, w in existing_weaknesses))
    schema = SCHEMAS["swot"]
    ph = PLACEHOLDER_FR if language == "fr" else PLACEHOLDER_EN
    return f"""CONTEXTE PAYS : {profile.country_name} — {profile.epi_programme_name}.
OUTPUT LANGUAGE: {lang_name}

COMPOSANTE PEV : {component.label(language)}
SOUS-COMPOSANTES À COUVRIR (codes : {codes}) :
{sub_lines}

DOCUMENTS SOURCES & DIRECTIVES (ta source prioritaire — constats pays, guides OMS/IA2030, normes) :
{_documents_block(documents, doc_budget)}{ew}

TÂCHE — ANALYSE FFOM COMPLÈTE :
Pour CHACUNE des sous-composantes ci-dessus (un item par sous-composante, subcomponent_code = code exact),
fournis une analyse FFOM SUBSTANTIELLE en remplissant les QUATRE quadrants :
- strengths (Forces) et weaknesses (Faiblesses) = INTERNES au PEV
- opportunities (Opportunités) et threats (Menaces) = EXTERNES au PEV
RÈGLES DE COMPLÉTUDE (IMPÉRATIVES) :
- Tu DOIS fournir AU MOINS 1 élément dans CHACUN des 4 quadrants (Forces, Faiblesses, Opportunités,
  Menaces) pour CHAQUE sous-composante. Ne renvoie JAMAIS une sous-composante dont les 4 listes sont vides.
- Vise 1 à 3 éléments par quadrant.
- Appuie-toi sur : 1) les constats des documents, 2) les directives/guides de référence, 3) ton expertise
  PEV/IA2030. Les faits chiffrés viennent des documents ; si les documents sont muets, propose des éléments
  plausibles issus de ton expertise et marque-les confidence "low" (à valider par l'équipe pays).
- CONSERVE les faiblesses déjà documentées et AJOUTE celles qui manquent.
- 'evidence' : cite la source quand elle existe (document, page, extrait, confidence).
{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_root_cause_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                            language: str, component, weaknesses: list[tuple[str, str]]) -> str:
    """Root-cause prompt: the AI applies the 5-Whys (its reasoning) to EACH FFOM weakness,
    informed by the reference documents/directives."""
    lang_name = "français" if language == "fr" else "English"
    wlist = "\n".join(f"- [{code}] {w}" for code, w in weaknesses)
    schema = SCHEMAS["root_causes"]
    return f"""CONTEXTE PAYS : {profile.country_name} — Programme {profile.epi_programme_name}.
OUTPUT LANGUAGE: {lang_name}

COMPOSANTE PEV : {component.label(language)}

FAIBLESSES DOCUMENTÉES (issues de l'analyse FFOM — analyse CHACUNE d'elles) :
{wlist}

DOCUMENTS SOURCES & DIRECTIVES (consulte-les pour éclairer ton raisonnement : constats pays, guides OMS, normes) :
{_documents_block(documents)}

TÂCHE — ANALYSE DES CAUSES PROFONDES (méthode des POURQUOI) :
Pour CHAQUE faiblesse ci-dessus, applique la méthode des « 5 POURQUOI ». Les POURQUOI sont TON
RAISONNEMENT d'expert en santé publique, ÉCLAIRÉ par les documents et directives ci-dessus : pars de la
faiblesse et demande « pourquoi cela se produit-il ? », puis « pourquoi ? » sur la réponse, et ainsi de
suite (3 à 5 niveaux) jusqu'à la CAUSE PROFONDE.
- Appuie ton raisonnement sur les constats des documents quand ils existent ; ne fabrique pas de faits.
- Recopie la faiblesse mot pour mot dans 'weakness' et son code dans 'subcomponent_code'.
- 'whys' = liste ordonnée des POURQUOI ; 'final_why' = la cause profonde (dernier POURQUOI).
{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_objective_prompt(profile: CountryProfile, documents: list[UploadedDocument], language: str,
                           component, causes_ctx: str, per_sub: bool, doc_budget: int = 12000) -> str:
    """Strategic-objective prompt for ONE component, chained from its root causes/obstacles.
    per_sub=True -> one SMART objective per subcomponent (option ≥26); False -> one per component (≥7)."""
    lang_name = "français" if language == "fr" else "English"
    ph = PLACEHOLDER_FR if language == "fr" else PLACEHOLDER_EN
    schema = SCHEMAS["objectives"]
    sub_lines = "\n".join(f"   {s.code} {s.label(language)}" for s in component.subcomponents)
    count_rule = (
        "Produis UN objectif stratégique SMART par SOUS-COMPOSANTE ci-dessous qui présente un obstacle "
        "(subcomponent_code = code exact). Il y aura donc PLUSIEURS objectifs." if per_sub else
        "Produis UN seul objectif stratégique SMART CONSOLIDÉ pour toute la composante "
        "(subcomponent_code = la sous-composante la plus centrale).")
    return f"""CONTEXTE PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période SNV : {profile.nis_start_year}-{profile.nis_start_year + profile.nis_duration_years - 1}.
OUTPUT LANGUAGE: {lang_name}
PLACEHOLDER (donnée pays manquante — à recopier tel quel) : "{ph}"

COMPOSANTE PEV : {component.label(language)}
SOUS-COMPOSANTES :
{sub_lines}

OBSTACLES / CAUSES PROFONDES (ta base — chaîne : faiblesse → cause profonde → objectif) :
{causes_ctx or "(peu de causes documentées — appuie-toi sur les faiblesses et ton expertise, confidence low)"}

DOCUMENTS & TABLES DE RÉFÉRENCE (codes IA2030 SPO, mapping EPI↔SPO, domaines Gavi GIA) :
{_documents_block(documents, doc_budget)}

TÂCHE — OBJECTIFS STRATÉGIQUES PRIORITAIRES :
{count_rule}
Pour CHAQUE objectif : 'main_obstacle' (problème central issu des causes), 'visionary_result' (résultat
visé), puis 'objective_text' = objectif SMART (verbe d'action, cible chiffrée ou "{ph}", valeur de base
ou "{ph}", échéance dans la période). Rattache chaque objectif à un CODE SPO IA2030 pertinent (mets le
code SPO dans 'objective_text' ou 'evidence'). N'invente AUCUN chiffre pays.
{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_intervention_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                              language: str, comp_label: str, objectives: list,
                              doc_budget: int = 12000) -> str:
    """Interventions prompt: for EACH strategic objective, propose fully-completed,
    evidence-grounded interventions (every field filled, sourced from the documents)."""
    lang_name = "français" if language == "fr" else "English"
    years = profile.nis_duration_years
    olist = "\n".join(f"- [{o.obj_id} | {o.subcomponent_code}] {o.objective_text}"
                      for o in objectives if (o.objective_text or "").strip())
    schema = SCHEMAS["interventions"]
    return f"""CONTEXTE PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période SNV : {years} ans (Y1..Y{years}).
OUTPUT LANGUAGE: {lang_name}
PLACEHOLDER si l'information est absente des documents : "{PLACEHOLDER_FR if language == 'fr' else PLACEHOLDER_EN}"

COMPOSANTE PEV : {comp_label}

OBJECTIFS STRATÉGIQUES PRIORITAIRES (pour CHACUN, proposer 3 à 5 interventions) :
{olist}

DOCUMENTS SOURCES (ta SEULE source de vérité — consulte-les pour étayer chaque champ) :
{_documents_block(documents, doc_budget)}

TÂCHE — INTERVENTIONS PRINCIPALES ET PRIORISATION :
Pour CHAQUE objectif ci-dessus, propose 3 à 5 interventions à fort impact et réalisables. Pour CHAQUE
intervention, REMPLIS TOUS LES CHAMPS avec des arguments SOLIDES et ANCRÉS DANS LES DOCUMENTS (jamais inventés) :
- objective_id : l'ID de l'objectif lié (ex. {objectives[0].obj_id if objectives else 'OBJ1'})
- title, rationale (justification fondée sur les constats des documents), expected_impact, feasibility_note
- prerequisites[], risks[], partners[] (concrets et pertinents pour le contexte du pays)
- timeline : objet {{"Y1":true/false, ... jusqu'à "Y{years}"}}
- score : note de 1 à 3 (3 = meilleur) pour CHACUN des 8 critères (expertise, return_on_investment,
  effectiveness, ease_of_implementation, negative_consequences, legal_constraints, health_system_impact,
  feasibility), en cohérence avec les preuves
- evidence[] : pour CHAQUE intervention, cite au moins une preuve {{document_name, locator (page/section),
  excerpt, confidence}}. Si un champ n'est pas étayé par les documents, écris le PLACEHOLDER et mets confidence "low".
{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_activity_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                          language: str, comp_label: str, interventions: list,
                          doc_budget: int = 12000) -> str:
    """Operational-activities prompt: break EACH main intervention into fully-completed key activities."""
    lang_name = "français" if language == "fr" else "English"
    years = profile.nis_duration_years
    year_keys = [f"Y{k + 1}" for k in range(years)]
    ilist = "\n".join(f"- [{iv.intervention_id} | obj {iv.objective_id} | {iv.subcomponent_code}] {iv.title}"
                      for iv in interventions if (iv.title or "").strip())
    schema = SCHEMAS["activities"]
    return f"""CONTEXTE PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période SNV : {years} ans ({', '.join(year_keys)}).
OUTPUT LANGUAGE: {lang_name}

COMPOSANTE PEV : {comp_label}

INTERVENTIONS PRINCIPALES À DÉCLINER EN ACTIVITÉS :
{ilist}

DOCUMENTS SOURCES & DIRECTIVES (constats pays, guides OMS/IA2030, Gavi 6.0) :
{_documents_block(documents, doc_budget)}

TÂCHE — ACTIVITÉS OPÉRATIONNELLES (compatibles NIS.COST) :
IMPÉRATIF DE COMPLÉTUDE : produis des activités pour CHACUNE des interventions listées ci-dessus —
n'en omets AUCUNE (au moins 2 activités par intervention, en recopiant son intervention_id).
Pour CHAQUE intervention ci-dessus, décompose-la en 2 à 4 ACTIVITÉS CLÉS concrètes. Pour CHAQUE activité,
REMPLIS TOUS LES CHAMPS : intervention_id (recopie l'ID lié), objective_id, subcomponent_code, activity,
implementation_level (National / Région-Gouvernorat / District / Formation sanitaire / Communauté /
Tous les niveaux), years (objet {{"Y1":true/false, … jusqu'à "Y{years}"}}), lead (entité responsable),
partners[], prerequisites[], risks[], deliverables[] (livrables concrets), evidence[] (cite la source).
Les activités doivent être réalistes, séquencées dans le temps et fondées sur les documents.{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


def build_indicator_prompt(profile: CountryProfile, documents: list[UploadedDocument],
                           language: str, comp_label: str, objectives: list) -> str:
    """M&E prompt: ≥1 fully-completed indicator per objective, with targets for ALL years."""
    lang_name = "français" if language == "fr" else "English"
    years = profile.nis_duration_years
    year_keys = [f"Y{k + 1}" for k in range(years)]
    targets_example = "{" + ", ".join(f'"{y}": "…"' for y in year_keys) + "}"
    olist = "\n".join(f"- [{o.obj_id} | {o.subcomponent_code}] {o.objective_text}"
                      for o in objectives if (o.objective_text or "").strip())
    schema = SCHEMAS["indicators"]
    ph = PLACEHOLDER_FR if language == "fr" else PLACEHOLDER_EN
    if olist:
        scope = (f"OBJECTIFS STRATÉGIQUES (pour CHACUN, au moins 1 indicateur d'IMPACT ou de PRODUIT) :\n{olist}")
        per = "Pour CHAQUE objectif, définis au moins un indicateur"
    else:
        scope = ("(Pas encore d'objectif saisi pour cette composante : propose 2 à 4 indicateurs CLÉS "
                 "pertinents pour cette composante.)")
        per = "Propose 2 à 4 indicateurs clés pour cette composante. Pour chaque indicateur, définis-le"
    return f"""CONTEXTE PAYS : {profile.country_name} — {profile.epi_programme_name}. \
Période SNV : {years} ans ({', '.join(year_keys)}).
OUTPUT LANGUAGE: {lang_name}

COMPOSANTE PEV : {comp_label}

{scope}

DOCUMENTS SOURCES & DIRECTIVES (ta SEULE source de vérité — ils contiennent souvent des LISTES/MENUS
d'indicateurs : IA2030, cadre de S&E OMS, indicateurs Gavi. ADAPTE les plus pertinents au contexte du pays) :
{_documents_block(documents)}

TÂCHE — CADRE DE SUIVI & ÉVALUATION :
{per} en t'appuyant en priorité sur les indicateurs standard trouvés dans les documents de référence
(IA2030, OMS, Gavi) ADAPTÉS au contexte, en REMPLISSANT TOUS LES CHAMPS : name, indicator_type
(impact/outcome/output/process), definition, formula, numerator_source, denominator_source, data_source,
frequency, responsible_measure, responsible_action, baseline, targets, assumptions, measurement_risks,
confidence, evidence.
RÈGLES IMPORTANTES :
- 'targets' DOIT contenir une valeur pour CHAQUE année : {targets_example}. NE LAISSE AUCUNE année vide
  (ni Y{years-1} ni Y{years}). Les cibles doivent être RÉALISTES et PROGRESSIVES (évolution cohérente
  de la référence vers l'objectif sur les {years} années).
- 'baseline' : si absente des documents, écris « {ph} » (ou « Situation de référence à confirmer par l'équipe pays »).
- 'evidence' : cite au moins une preuve (document, page/section, extrait, confidence). N'invente jamais de chiffre.
{gavi_clause(language)}

SCHÉMA JSON (retourne exactement cette forme, rien d'autre) :
{json.dumps(schema, ensure_ascii=False, indent=2)}
"""


# --------------------------------------------------------------------------- #
# Per-section instructions + JSON schemas (kept compact; validated downstream).
# --------------------------------------------------------------------------- #
SECTION_INSTRUCTIONS = {
    "vision": "Generate the country's 10-year immunization vision, the NIS goal for the period, and the "
              "overall objective, aligned with IA2030, equity, zero-dose/under-immunized children, PHC, "
              "health-system resilience, life-course vaccination and sustainable financing.",
    "swot": "For EACH EPI subcomponent (code like '1.1'), list strengths, weaknesses (INTERNAL) and "
            "opportunities, threats (EXTERNAL). Empty lists are allowed where evidence is absent.",
    "root_causes": "For each documented weakness, apply the '5 Whys'. Provide an array 'whys' (Why-1..n) and "
                   "a 'final_why' (root cause). Add as many whys as the evidence supports.",
    "objectives": "From the final whys, formulate the main obstacle, the visionary change result, and ONE "
                   "SMART strategic objective per item. Respect the requested grouping option.",
    "interventions": "For each strategic objective, propose 3-5 high-impact, feasible interventions with "
                      "rationale, expected impact, feasibility, prerequisites, risks, partners and a Y1..Yn "
                      "timeline. Score each on the 8 criteria (1-3).",
    "indicators": "For each strategic objective, define preferably 1 IMPACT or OUTPUT indicator with full "
                  "M&E metadata and progressive yearly targets. If no baseline -> baseline placeholder.",
    "activities": "Break each intervention into key activities with implementation level, Y1..Yn calendar, "
                  "lead, partners, prerequisites, risks and deliverables (NIS.COST-compatible).",
}

_EVIDENCE = {"document_name": "str", "locator": "str", "excerpt": "str", "confidence": "high|medium|low"}

SCHEMAS: dict[str, dict] = {
    "vision": {"vision": "str", "goal": "str", "overall_objective": "str", "evidence": [_EVIDENCE]},
    "swot": {"items": [{
        "component_code": "str", "subcomponent_code": "str",
        "strengths": ["str"], "weaknesses": ["str"], "opportunities": ["str"], "threats": ["str"],
        "evidence": [_EVIDENCE]}]},
    "root_causes": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "weakness": "str",
        "whys": ["str"], "final_why": "str", "evidence": [_EVIDENCE]}]},
    "objectives": {"items": [{
        "obj_id": "str", "component_code": "str", "subcomponent_code": "str",
        "main_obstacle": "str", "visionary_result": "str", "objective_text": "str",
        "is_smart": True, "evidence": [_EVIDENCE]}]},
    "interventions": {"items": [{
        "intervention_id": "str", "objective_id": "str", "component_code": "str", "subcomponent_code": "str",
        "title": "str", "rationale": "str", "expected_impact": "str", "feasibility_note": "str",
        "score": {"expertise": "1-3", "return_on_investment": "1-3", "effectiveness": "1-3",
                  "ease_of_implementation": "1-3", "negative_consequences": "1-3", "legal_constraints": "1-3",
                  "health_system_impact": "1-3", "feasibility": "1-3"},
        "timeline": {"Y1": True, "Y2": False}, "prerequisites": ["str"], "risks": ["str"],
        "partners": ["str"], "evidence": [_EVIDENCE]}]},
    "indicators": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "objective_id": "str", "name": "str",
        "indicator_type": "impact|outcome|output|process", "definition": "str", "formula": "str",
        "numerator_source": "str", "denominator_source": "str", "data_source": "str", "frequency": "str",
        "responsible_measure": "str", "responsible_action": "str", "baseline": "str",
        "targets": {"Y1": "str", "Y2": "str"}, "assumptions": "str", "measurement_risks": "str",
        "confidence": "high|medium|low", "evidence": [_EVIDENCE]}]},
    "activities": {"items": [{
        "component_code": "str", "subcomponent_code": "str", "objective_id": "str", "intervention_id": "str",
        "activity": "str", "implementation_level": "str", "years": {"Y1": True, "Y2": False},
        "lead": "str", "partners": ["str"], "prerequisites": ["str"], "risks": ["str"],
        "deliverables": ["str"], "evidence": [_EVIDENCE]}]},
}
