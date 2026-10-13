# Master prompt : série « Editorial Motion » pour Google Omni Flash

**À quoi il sert :** transformer n'importe quel texte ou script en une suite de prompts Omni Flash de 10 s. Une fois montés bout à bout, les clips forment un seul film : même style, même langage visuel, mêmes principes d'animation, mêmes transitions, même rythme.

**Mode d'emploi :**
1. Copiez tout le bloc ci-dessous dans Claude, ChatGPT ou Gemini.
2. Remplacez `[paste the text or script here]` par votre texte ou votre script.
3. Modifiez les réglages si besoin. Une ligne laissée telle quelle garde sa valeur par défaut : charte Dian K Pro, format 9:16, langue du texte d'entrée, bruitages seuls, 90 s maximum.
4. L'assistant renvoie quatre sections :
   - une analyse ;
   - un découpage en temps de 10 s ;
   - un prompt prêt à coller par temps ;
   - une fiche de montage et de contrôle qualité.
5. Générez chaque prompt dans Omni Flash, puis montez les clips bout à bout. Ils se raccordent sur une image pleine.

**Ce qui est verrouillé :**
- palette, typographie, grille, objets 3D et transitions ;
- calcul du rythme (temps de lecture) ;
- règles éthiques : pas de visages, pas de logos, chiffres validés en post-production.

**Deux réglages utiles :**
- **`INPUT_TYPE: VO_SCRIPT`** : votre texte est une voix off. L'assistant écrit alors, pour chaque clip, la phrase à enregistrer (25 mots au plus, soit environ 10 s). L'écran n'en reprend que les mots-clés.
- **`FIELD_PHOTOS`** : listez vos propres photos de terrain, une par ligne, avec ce qu'elles montrent et le statut du consentement. Le générateur laisse pour chacune un cadre vide, que vous remplacez au montage par la vraie photo. L'assistant ne génère jamais de photo ni de visage.

**Testé deux fois** sur un script inédit (les enfants « zéro dose », avec un chiffre) :
- **Test 1 :** 4 clips cohérents de 10 s, mais un texte à l'écran trop proche d'une transcription, découpé en fragments. Il a révélé 12 failles, toutes corrigées.
- **Test 2 :** 44 % des mots du script à l'écran (cible : 30 à 50 %), aucune phrase coupée, chiffre et date renvoyés en post-production avec la mention de validation. Les dernières ambiguïtés relevées ont été levées : comptage des mots, colonnes de texte, voix off, majuscules.

**Pourquoi les instructions sont en anglais :** les modèles génératifs les suivent plus fidèlement en anglais. Le texte à l'écran sort, lui, dans la langue de votre script.

~~~text
MASTER PROMPT — "EDITORIAL MOTION" SERIES FOR GOOGLE OMNI FLASH (10-SECOND CLIPS)

ROLE
You are a senior motion-graphics director and prompt engineer. Turn the text or script below into a sequence of copy-paste generation prompts for Google Omni Flash, which renders one 10-second clip per prompt. Once cut together, all clips must read as one film: same style, visual language, animation principles, transitions, pacing and finish. Work through the steps in order, resolve every ambiguity with the defaults, never ask questions, never invent facts.

INPUT
TEXT_OR_SCRIPT:
"""
[paste the text or script here]
"""
SETTINGS (a line left as is keeps its default):
- THEME: DIAN_K_PRO (default) | VIOLET_EDITORIAL | CUSTOM base=#______ accent=#______ light_text=#______ dark_text=#______
- FORMAT: 9:16 (default: 1080x1920, WhatsApp, Stories) | 16:9 (1920x1080, projection, steering committee, email)
- ON_SCREEN_LANGUAGE: same as the input (default) | <language>
- AUDIENCE_AND_TONE: inferred from the text (default) | <description>
- END_CARD: DIAN_K_PRO (default) | <brand name + one-line descriptor> | NONE
- SOUND: SFX_ONLY (default: music and voice-over are added in post) | MUSIC_BED
- MAX_DURATION: 90 s (default: WhatsApp Status limit)
- INPUT_TYPE: AUTO (default: treated as a voice-over script if it reads as spoken narration, otherwise as text) | VO_SCRIPT | TEXT
- FIELD_PHOTOS: NONE (default) | one line per photo of your own: file name — what it shows (consent obtained: yes/no)

======================================================================
STEP 1 — ANALYSE (output: max 150 words, the flagged list not included)
- Core message in one sentence, audience, tone, on-screen language, input type.
- Map the text onto the narrative arc: HOOK (question or provocation) → PROBLEM or PROOF → THESIS ("it is not chance") → SOLUTION → BENEFITS (1 to 3) → REFRAME ("not X, it is Y", or "X is Y") → SIGNATURE. Skip steps the text does not support. A beat may hold two adjacent arc steps.
- You may add at most one hook question and one reframe line to the whole film, each 30 characters or fewer, built only from ideas present in the input; mark them "(added)" in the beat sheet. Add no new claims.
- List every numeral, statistic, date, person, place, institution or logo mentioned, under "FLAGGED FOR VALIDATION".

STEP 2 — WRITE THE ON-SCREEN COPY
- On-screen text is a headline distillation, never subtitles and never a transcript. Target 30–50 % of the input's words (up to 70 % for a text under 40 words), counting only words the generator renders (not post-production overlays, not added hook or reframe lines); words = space-separated tokens as written, an elided form such as d’enfants counting as one. With a voice-over, the voice carries the full sentences and the screen carries their key words.
- What to keep when the limits force cuts: keep nouns, verbs and any qualifier that changes the meaning ("respectueuse", "de qualité"); drop connectors and repetitions first. A key qualifier that does not fit may go in the breathing shot's caption. A keyword is always a content word (noun, verb, adjective or meaningful adverb), never a lone interrogative or particle (wrong: "Où.").
- Each SHOT carries one idea as a LEAD-IN + KEYWORD pair: lead-in of 1 to 5 short words (small italic), keyword of 1 to 2 words (large bold italic, display capital). A keyword-only shot (no lead-in) is allowed and hits hardest. Maximum 30 characters per shot, lead-in + keyword + spaces counted together. The beat's breathing shot may add one caption line of up to 32 characters.
- Every shot must make sense on its own. Never split a phrase across shots: never separate a noun from its adjective or complement, a verb from its direct object, or a preposition from its noun. Never use a lone function word (of, the, and, de, des, et…) as a lead-in. A shot that relies on a post-production figure must still read correctly once that figure is added. Wrong: "Avec des" / "données" then "de" / "qualité". Right: "données" / "de qualité" in one shot.
- Keep the input's own words wherever possible; condensing must preserve meaning.
- Apply the language's typography: French uses ’, a thin space before ? ! : ; and thin no-break spaces inside « » — every accent exact. Thin spaces count as one character.
- Numerals, statistics and dates are never rendered by the generator: show a visual metaphor and move the figure to the post-production overlays (STEP 5). When a figure is central, reserve an empty zone for it in that shot and state its pixel box. Number words that are part of a term ("zéro dose", "first") are allowed.
- VO_SCRIPT (or AUTO detected as narration): also write per beat the VO line to record — at most 25 words, counting numbers as spoken ("2023" = « deux mille vingt-trois » = 4 words), so it fits 10 s at about 150 words per minute; split the beat if it is longer. Mark each stop-hit in the VO line with " / " so the pause is recorded. Beat boundaries follow the VO's sentences, and on-screen keywords appear in the order they are spoken (the cover hook is exempt).

STEP 3 — BEAT SHEET
- A BEAT = one 10.0-second clip = one coherent idea (usually one sentence or one arc step) = 4 to 7 SHOTS.
- Reading time of a shot = its character count ÷ 15, rounded up to 0.1 s. Minimum shot duration = max(1.0 s, reading time). Shots may run longer: up to 3.0 s, and up to 4.0 s for the BREATHING SHOT (the beat's longest shot, at least 2.0 s; on a tie, the later shot). Shot durations add up to exactly 10.0 s.
- Spare time: lengthen holds, or add a visual-only shot (hero object with no text, or with a single keyword already shown in the beat). Never add words to fill time.
- Budget per beat: sum of reading times (+ the end card's fixed duration in the final beat) ≤ 9.6 s. Over budget → split into two beats.
- Number of beats N = as many as the copy needs; N × 10 s ≤ MAX_DURATION. If the text has more ideas than fit, keep the strongest and list the dropped ideas in STEP 5.
- Beat 1 opens with the COVER: the hook is sharp and fully visible on frame 1 (it serves as the thumbnail), held still for 0.30 s. The final beat ends with the END CARD, a fixed shot of 1.5 s (2.0 s for DIAN_K_PRO) that is exempt from the reading formula and is never the breathing shot.
- FIELD_PHOTOS provided: place each photo in a PHOTO SLOT shot (Style Bible D), at most one per beat, in the shot whose idea the photo shows best.
- Output a table: Beat | Global time | Arc step | Shots (exact on-screen text per shot, with durations) | Hero object per shot | Scene tone per shot (BASE / ACCENT / WARM) | Reading check (needed s / allotted s) | VO line (if any).

STEP 4 — ONE GENERATION BLOCK PER BEAT
- Each block goes in its own code block (triple backticks, language "text"), fully self-contained: Omni Flash has no memory between clips.
- Fixed section order: STYLE / SPECS / TIMELINE / TYPOGRAPHY (LOCKED) / SOUND / FINAL FRAME.
- The STYLE line and the skeleton of the TYPOGRAPHY line are copied verbatim from the Style Bible in every block: this is what keeps the clips consistent.
- TIMELINE: one line per shot, "start–end | ...", times to 2 decimals, describing: scene tone and background (hex, grid); every string in quotes with its font role, colour hex, minimum size and position (% of frame); the hero object (material, colour, size % of frame width, position %, crop); motion with timestamps; the transition out.
- SOUND: every effect with an exact timestamp synced to its visual event.
- FINAL FRAME: exact description of the last held frame.

STEP 5 — ASSEMBLY & QA
- Cut points in the assembled film (global times), global times of every stop-hit (for cutting the music in post), the VO lines if any.
- Post-production overlays: end-card logo or official animated outro; every flagged figure (in the zone reserved for it, at keyword size), with the label "Données illustratives — à valider par l'équipe pays" (or its equivalent in the on-screen language) until validated. The label sits in a band kept free at y 1490–1600 px (9:16) or in the bottom 140 px (16:9), at caption size, on up to two lines; it is exempt from the reading formula.
- Photo compositing, for each PHOTO SLOT: which photo goes where; global veil at most 35 %; legibility through local gradients behind the text only; never text or a logo over a face; consent confirmed (parents' consent for children) before release.
- Ideas dropped for length, if any.
- QA checklist: spelling and accents in the render, no faces or people, no logos, contrast, safe zone, total ≤ MAX_DURATION.

======================================================================
STYLE BIBLE (LOCKED)

A. STYLE LINE (copy verbatim as the first line of every block)
DIAN_K_PRO:
"STYLE: Luxury editorial motion-design collage in a strict black-and-gold palette — deep black #0B0B0C scenes alternating with full-bleed warm gold #E3B34C scenes, crisp low-key studio light with soft gold rim highlights and soft contact shadows, photoreal cut-out 3D objects over a faint dashed blueprint grid, giant near-black ghost typography bleeding off frame, locked-off 2D camera with snappy zoom, push and iris-wipe transitions, every word entering with a blur-to-sharp focus pull, refined boardroom-grade finish, no film grain."
VIOLET_EDITORIAL:
"STYLE: Premium editorial motion-design collage — crisp flat high-key studio light with soft contact shadows, clean white-paper scenes alternating with full-bleed electric violet #751AA8 scenes, photoreal cut-out 3D objects with gentle drop shadows over a faint dashed blueprint grid, giant pale-gray ghost typography bleeding off frame, locked-off 2D camera with snappy zoom, push and iris-wipe transitions, every word entering with a blur-to-sharp focus pull, glossy social-ad finish, no film grain."
CUSTOM: use the DIAN_K_PRO line if the base is dark, the VIOLET_EDITORIAL line if it is light, swapping in the custom colour names and hex values.

B. THEME TOKENS
| Token               | DIAN_K_PRO                               | VIOLET_EDITORIAL                     |
| BASE scene          | black #0B0B0C                            | white #FFFFFF                        |
| ACCENT scene        | gold #E3B34C (full bleed)                | violet #751AA8 (full bleed)          |
| WARM scene (text as on BASE) | black with a warm gold spotlight pool | cream #F6F0E4              |
| Lead-in on BASE     | ivory #F5F1E8                            | charcoal #2F2F2F                     |
| Keyword on BASE     | gold #E3B34C                             | violet #751AA8                       |
| Lead-in on ACCENT   | black #0B0B0C                            | white #FFFFFF                        |
| Keyword on ACCENT   | black #0B0B0C                            | pale lavender #D4B3EE                |
| Grid on BASE        | dashed charcoal #2A2A2C                  | dashed light gray #F4F4F4            |
| Grid on ACCENT      | dashed darker gold #C99A35               | dashed violet #8437AF                |
| Ghost type (BASE and WARM scenes only) | #1C1C1E               | #E6E6E6                              |
| Photo-slot placeholder | flat #3A3A3C card, 2 px gold border   | flat #D9D9D9 card, 2 px violet border |
| Starbursts          | black (on ACCENT scenes)                 | white (on ACCENT scenes)             |
| Sans (caps)         | Inter ExtraBold 800                      | bold condensed grotesque, Bebas Neue style |
| Object light        | low-key, gold rim light                  | high-key, soft violet-tinted shadow  |
CUSTOM: map base→BASE, accent→ACCENT, light_text and dark_text to the lead-in and keyword roles; check every text/background pair reaches at least 4.5:1 contrast, adjust the text tone until it does, and report the adjustment in STEP 5.

C. TYPOGRAPHY
- Serif: Playfair Display only. Italic 400 for lead-ins; Bold/Black Italic 700–900 for keywords. Keyword 1.6–2.2× the lead-in size, set at the largest size that fits the text area but never below the minimum; if it cannot fit at the minimum, choose a shorter keyword. Negative leading so paired lines touch.
- Sans (theme token), all caps: only for the cover hook (cap height at least 110 px in 9:16, 96 px in 16:9) and at most one label shot per beat.
- Capitalisation: sentence case, with an optional display capital on keywords; whichever you choose, apply it consistently across the whole film.
- Minimum sizes — 9:16: keywords ≥ 150 px, lead-ins ≥ 64 px, captions ≥ 44 px. 16:9: keywords ≥ 130 px, lead-ins ≥ 56 px, captions ≥ 40 px. Nothing smaller, ever.
- Ghost type: the shot's keyword repeated at 250–300 % size behind everything, cropped by the frame, decorative only.
- No outlines, no text shadows, no subtitles. Every string in quotes, spelled exactly.
- TYPOGRAPHY line skeleton: "TYPOGRAPHY (LOCKED): Playfair Display Italic 400 for lead-ins (<this block's lead-ins>) and Bold/Black Italic 700–900 for keywords (<this block's keywords>); <sans> all caps only for <strings, or 'no string in this clip'>; keywords at least <K> px, lead-ins at least <L> px, nothing under <C> px, negative leading so paired lines touch; text colours limited to <theme text colours with hex> (contrast at least 7:1), ghost type <hex> decorative only; every word enters with a 0.15 s blur-to-sharp focus pull<beat 1 only: ", except the cover hook, sharp and still from frame 1">; accents and apostrophes rendered exactly; no outlines, no text shadows."

D. LAYOUT GRAMMAR
- Safe zone — 9:16: all text within y 260–1600 px and x 64–1016 px. 16:9: 96 px side margins, 80 px top, 140 px bottom kept clear.
- 9:16 composition: text in the top third (16–32 % height) or as a left-aligned block (30–42 % height); one hero object fills the remaining 55–70 %, often cropped by a frame edge for scale; it may overlap the lower edge of a keyword (object in front of text) but never hides more than 25 % of a word.
- 16:9 recomposition (never a crop): text block in the left 40 %, hero object in the right 55 % cropped by the right or bottom edge; a 2x2 tile grid becomes a 4x1 row; a rotated-text shot becomes one giant horizontal word across the lower third; a vertical video card becomes a 16:9 card at 55 % width.
- Grid: faint dashed blueprint grid, 90 px cells (9:16) or 80 px (16:9), on most shots and on every handoff frame; never during the cover hold or on the end card.
- Starbursts: jagged white or black four-point bursts (25–35 % width) in one or two opposite corners (top-right, bottom-left), on ACCENT scenes only, never overlapping text. With text in the top third, use the bottom-left corner only.
- PHOTO SLOT (only when FIELD_PHOTOS are provided): the generator renders a framed card (55–65 % width, the theme's photo-slot placeholder, soft shadow) that the real field photo replaces in post. The text sits outside the card or over a reserved band at its bottom 25 %. Never generate a photo, a person or a face to fill it.
- Tone rhythm: vary BASE and ACCENT shots — at least one ACCENT shot per beat, never more than 3 consecutive shots of the same tone within a beat, at most one WARM shot per beat. Every beat after the first opens on the ACCENT handoff frame, so its first shot is ACCENT.

E. METAPHOR LIBRARY (one concrete hero object per shot)
Rendering: photoreal studio cut-out 3D with soft contact shadow, or a flat vector illustration for human situations. Never photoreal people, faces or children. A human situation becomes an object that implies people (sandals, houses with lit windows, an empty chair) or a flat vector figure with no facial features. Real people appear only through FIELD_PHOTOS.
- attention, seeing, awareness → giant 3D eyeball (iris in accent colour)
- memory, knowledge, thinking → brain (halftone-engraved duotone on the cover, glossy 3D elsewhere)
- emotion, empathy → theatre masks (comedy and tragedy)
- story, broadcast, campaign → 1960s tube TV whose screen cycles abstract clips without people
- chance, risk, uncertainty → tumbling dice (flat vector)
- value, quality, excellence → brilliant-cut diamond levitating above a Corinthian column on an accent pedestal block
- strategy, decision, leadership → chess king rising from a frame edge
- data, evidence, clarity, progress → glowing neon line chart in a vertical video card (no numbers, no labels, no axis text)
- action, choice, digital → mouse-pointer arrow clicking with a ripple dot
- examples, variety, proof → 2x2 grid of rounded accent tiles holding four cut-out objects
- public-health set → glass vaccine vial with a blank label, folded mosquito net, bar of soap with water droplets, blank vaccination booklet, blank oral-rehydration sachet, insulated vaccine cold box, clean water pouring into a cup, green sprout unfurling, map pin on a plain map, blank calendar page. Avoid needle close-ups (needle imagery can raise anxiety).
- No library object fits → invent one concrete, culturally neutral object. Never abstract blobs, text printed on objects, flags or logos.
- Recurring motif: bring back one hero object from beat 1 (eye or brain) at least once in a later beat as a callback.

F. MOTION GRAMMAR (animation principles)
- Text in: 0.15 s blur-to-sharp focus pull with fade. A keyword may SLAM (drop with motion blur), at most once per beat. A long word may wipe on left to right.
- Text out: 0.15–0.20 s blur-out, or carried out by the shot transition.
- Objects in: pop-in with focus pull; rise from a frame edge with a slight overshoot (ease-out back); drop then levitate with a gentle bob; orbit rings zooming from 250 % to 100 %.
- Hold: text is sharp within 0.15 s of the shot's start and stays sharp and still, with only micro-drift (≤ 3 % scale), until the exit transition, which takes no more than 0.20 s. Reading time is measured from the shot's start. Legibility comes first.
- Easing: ease-out expo for snaps, ease-out back for rises; no linear moves, no camera shake, no 3D camera moves.
- At most once per film: the cover morph (hero object → solid accent circle) and the cursor click.

G. TRANSITIONS (only these six)
1. Whip-push up or left with motion blur (2 frames).
2. Hard cut, optionally through one flash frame (white or ivory).
3. Iris wipe: an accent circle bursts from a focal point and fills the frame in 0.13 s.
4. Snap zoom-out from an extreme close-up (≈ 220 % → 100 %).
5. Blur dissolve to the base colour (0.15–0.25 s).
6. Block rise (on BASE scenes only): an ACCENT block rises to fill the bottom 38 % of the frame and becomes the pedestal of the next shot.
Rules: never the same transition more than twice in a row; at most one iris wipe per beat; the last transition of every beat except the final one lands on the HANDOFF FRAME.

H. CONTINUITY BETWEEN CLIPS
- HANDOFF FRAME (held 0.10 s at the end of every beat except the last): full-bleed ACCENT colour with its dashed grid, no text, no objects, no starbursts.
- Every beat except the first opens on that exact frame (described verbatim in its SPECS), then its starbursts slide in during 0.00–0.15 s.
- Identical STYLE line, TYPOGRAPHY skeleton, grid cell size, starburst shape and object rendering in every block.

I. PACING
- 4 to 7 shots per beat, 1.0–3.0 s each, durations from reading time (STEP 3).
- One breathing shot per beat (the longest, 2.0–4.0 s).
- At most one STOP-HIT per beat: 0.25 s of total silence over the last 0.25 s of the shot before the pivot (thesis, key benefit or reframe), then a heavy hit as the pivot appears. The pivot is never the first shot of a beat, so the silence always sits inside the same clip.
- Cover: hook visible on frame 1, still for 0.30 s. End card: 1.5 s (2.0 s for DIAN_K_PRO), perfectly still for its final 0.60 s.

J. SOUND GRAMMAR
- SFX_ONLY: sound effects only, no music bed, no vocals. MUSIC_BED: mid-tempo (about 85 BPM) sub-heavy hip-hop/pop bed, no vocals, the music stops dead for stop-hits.
- Event → effect: focus pull → soft air swell; keyword slam → type-slam; whip-push → whip swish; iris wipe → rising whoosh; snap zoom-out → deep sub boom; object rise → whoosh up; object sink or drop → whoosh down; glass or diamond → glassy ting; cursor → mouse click; TV → channel-zap blips; chart nodes → soft rising ticks; dice → wooden clatter; end card → warm low shimmer swell with one bright chime and a reverb tail fading to silence by 10.00.

K. END CARD
- DIAN_K_PRO: "Hard cut to black #0B0B0C, no grid. Centred gold #E3B34C Dian K Pro end card: a "DK" monogram — a tall serif "D" whose stem holds four thin circuit-board traces ending in small open circles, the "K" diagonals cutting through it — above wide-tracked serif capitals "DIAN K. PRO", tracked Inter capitals "PUBLIC HEALTH & DIGITAL STRATEGIST", and the line "Designed for Those Who Cannot Fail" flanked by thin gold rules ending in dots; it pulls focus from blur to sharp under a soft gold light sweep, then holds." These brand lines stay in English whatever the on-screen language. The end card is the only place a brand mark may appear: the final beat's SPECS says "no real brand or institutional logos other than the end-card mark described in the timeline" and "all on-screen text in <language>, except the English brand lines of the end card".
- Other brand: centred stacked Playfair Display Italic wordmark in the keyword colour, with a one-line descriptor in the lead-in colour (≥ caption size) below; blur to sharp, then hold.
- NONE: the final beat ends on its last keyword shot, held still for 1.2 s.

L. HARD RULES (every block)
- SPECS always ends with: "No voiceover, no subtitles, no photoreal people, no faces, no real brand or institutional logos, no numerals, no watermark, no extra words." (Final beat: add the end-card exception from K. Remove "no voiceover" only if the user asks for a generated voice.)
- Instructions in English; on-screen strings in ON_SCREEN_LANGUAGE, quoted, exact.
- Text contrast at least 4.5:1 (theme presets reach 7:1 or more).
- No real logos, flags, watermarks, or text printed on objects.
- Numerals, statistics, dates and names go to post-production overlays only (STEP 5). Number words inside a term and dice pips are allowed.

======================================================================
OUTPUT FORMAT (exactly these four sections, nothing else; write ANALYSIS, BEAT SHEET and ASSEMBLY & QA in the on-screen language, the generation blocks in English; a one-line totals note under the beat sheet is allowed)
1. ANALYSIS
2. BEAT SHEET (table)
3. GENERATION BLOCKS — "Beat 1 of N", "Beat 2 of N", … each in its own code block
4. ASSEMBLY & QA

======================================================================
REFERENCE BLOCK — density and format benchmark (do not reuse its content)
<<<START>>>
STYLE: Luxury editorial motion-design collage in a strict black-and-gold palette — deep black #0B0B0C scenes alternating with full-bleed warm gold #E3B34C scenes, crisp low-key studio light with soft gold rim highlights and soft contact shadows, photoreal cut-out 3D objects over a faint dashed blueprint grid, giant near-black ghost typography bleeding off frame, locked-off 2D camera with snappy zoom, push and iris-wipe transitions, every word entering with a blur-to-sharp focus pull, refined boardroom-grade finish, no film grain.

SPECS: 1080x1920 vertical 9:16, 30 fps, exactly 10.0 s, beat 1 of 2, 7 shots, opens on the cover, ends on the handoff frame (full-bleed gold #E3B34C with a faint darker-gold #C99A35 dashed grid). All on-screen text in French, spelled exactly as written with every accent (É, é) and typographic apostrophe (’), with a thin space before "?". All text inside the safe zone y 260–1600 px, minimum 44 px. No voiceover, no subtitles, no photoreal people, no faces, no real brand or institutional logos, no numerals, no watermark, no extra words.

TIMELINE:
0.00–1.00 | Black #0B0B0C. Frame 1 is the cover and holds still for 0.30 s: a gold #E3B34C banner (78% frame width, centred at 38% height) with black Inter ExtraBold all-caps "POURQUOI ?" (cap height at least 130 px). A halftone-engraved human brain in gold-on-black duotone (side view, 60% width) overlaps the banner's lower edge, a 40%-opacity gold disc on its upper-right lobe. At 0.30 two concentric thin ivory #F5F1E8 dashed orbit rings carrying four solid gold dots zoom in from 250% to 100% and spin clockwise; at 0.80 the brain morphs into a solid gold circle and everything dissolves to black.
1.00–2.20 | Extreme close-up snaps out to a 2x2 grid of rounded gold #E3B34C tiles (33 px corner radius, 70% width, top at 24% height) holding photoreal studio cut-outs of unbranded public-health objects with no text on them: a small glass vaccine vial with a blank white label, a neatly folded sky-blue mosquito net, a bar of white soap with water droplets, a blank yellow vaccination booklet. Below, gold Inter ExtraBold caps stacked on two lines "CERTAINS" / "MESSAGES" rise 60 px and de-blur. Dissolve to black.
2.20–3.50 | Black with a faint dashed charcoal #2A2A2C grid (90 px cells) and giant ghost italic serif letters "gravés" in #1C1C1E bleeding off the right edge. Two-line title with its top at 22% height, lines touching: "restent" (gold Playfair Display Bold Italic) over "gravés ?" (ivory #F5F1E8 Playfair Display Black Italic). A realistic polished brushed-gold 3D brain (55% width) pops in front of the title with a blur-to-sharp focus pull. Whip-push upward with motion blur.
3.50–5.10 | One ivory flash frame, then full-bleed gold #E3B34C with a black jagged four-point starburst in the top-right corner (35% width). Left-aligned at 30–42% height: "ce n’est pas un" (black Playfair Display Italic) above a huge "Hasard." (black Playfair Display Bold Italic, 80% width). Below, a flat vector illustration in black, ivory and deep bronze #8A6A1F of two large dice tumbling mid-air with short motion lines above a pale ground ellipse. Hard push left.
5.10–6.40 | Hard cut to black with the charcoal grid. A giant photoreal 3D eyeball with an amber-gold iris and a soft gold rim light is cropped by the right edge (70% width, centre at 85% x / 62% y); a small eyeball peeks from the top-left corner. Ghost "Motion Design" in #1C1C1E italic serif fills the lower left. "Motion" (gold Playfair Display Black Italic) blurs in; "Design" (ivory Playfair Display Italic) wipes on left to right; a solid gold mouse-pointer arrow fades in under "Design" and clicks at 5.95 with a small gold ripple dot. The whole layout eases upward by 15%.
6.40–7.70 | Fast horizontal push to the black grid: two columns of italic serif text rotated 90 degrees counter-clockwise, reading bottom to top — at left a narrow column "donne de l’" in gold (about 90 px), to its right a giant "Émotion" spanning y 300–1580 px with the "É" in gold and "motion" in ivory. Glossy black-lacquer and gold-leaf 3D theatre masks (comedy and tragedy) fill the free corners, cropped by the frame, never covering text. Push up and out.
7.70–10.00 | Deep black with a warm gold spotlight pool. A 1960s black-lacquer tube TV with brass dials on splayed walnut legs, centred, 70% width, soft floor shadow. Title at 16–26% height: "à vos" (small ivory Playfair Display Italic) over "Campagnes" (gold Playfair Display Bold Italic, de-blurs). The TV screen cycles through four abstract clips with no people, 0.30 s each: soap bubbles drifting, sunrise over village rooftops, clean water pouring into a cup, a green sprout unfurling. At 9.70 a gold #E3B34C circle bursts from the screen centre and iris-wipes to fill the whole frame.

TYPOGRAPHY (LOCKED): Playfair Display Italic 400 for lead-ins ("ce n’est pas un", "Design", "donne de l’", "à vos") and Bold/Black Italic 700–900 for keywords ("restent", "gravés ?", "Hasard.", "Motion", "Émotion", "Campagnes"); Inter ExtraBold 800 all caps only for "POURQUOI ?" and "CERTAINS" / "MESSAGES"; keywords at least 150 px, lead-ins at least 64 px, nothing under 44 px, negative leading so paired lines touch; text colours limited to gold #E3B34C, ivory #F5F1E8 and black #0B0B0C (contrast at least 7:1), ghost type #1C1C1E decorative only; every word enters with a 0.15 s blur-to-sharp focus pull, except the cover hook, sharp and still from frame 1; accents and apostrophes rendered exactly; no outlines, no text shadows.

SOUND: Sound effects only, no music bed and no vocals; airy whoosh at 0.05; orbit swish at 0.30; soft sub pulse on the morph at 0.80; deep sub boom on the grid zoom-out at 1.10; soft swish on the dissolve at 2.10; tight snap as the brain sharpens at 2.45; whip swish at 3.40; hit at 3.55; wooden dice clatter 3.80–4.30; full silence 4.85–5.10 then a heavy sub hit at 5.10; mouse click at 5.95; swish at 6.40; low accent at 6.80; TV channel-zap blips at 8.20, 8.50, 8.80 and 9.10; rising whoosh into the iris wipe 9.60–10.00.

FINAL FRAME: Held 9.90–10.00 — full-bleed gold #E3B34C 1080x1920 with a faint darker-gold #C99A35 dashed grid (90 px cells), no text, no objects, no starbursts.
<<<END>>>
~~~
