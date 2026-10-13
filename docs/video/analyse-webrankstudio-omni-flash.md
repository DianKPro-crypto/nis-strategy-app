# Analyse plan par plan et prompts Omni Flash : vidéo de référence « webrankstudio.MP4 »

> **Source :** `data/uploads/webrankstudio.MP4`, vidéo promotionnelle en motion design (vidéo de tiers, filigrane créateur `@alee.gfx_`).
> **Méthode :** extraction d'images sur toute la durée (4 i/s, plus 15 i/s autour de chaque transition), détection des changements de plan, échantillonnage colorimétrique au pixel (valeurs médianes), analyse spectrale de l'audio.
> **Limite :** la piste son a été analysée par le signal (énergie, spectre, attaques), pas à l'écoute. Le tempo et la nature des effets sonores sont donc des estimations.

---

## 1. Synthèse

| Paramètre | Valeur mesurée |
|---|---|
| Durée | **19,11 s** (572 images) |
| Résolution / format | **720 × 1280, 9:16 vertical** |
| Cadence | **30 i/s** constante |
| Codecs | H.264 + AAC stéréo 44,1 kHz |
| Sonie | −14,3 LUFS intégrés, crête −0,3 dBFS (calibrage réseaux sociaux) |
| Style en une ligne | Collage éditorial « magazine premium » : typographie Playfair italique XXL superposée, objets 3D et photos détourés à ombre douce, alternance blanc papier / violet électrique plein cadre, grille pointillée en fond. |
| Rythme | **12 temps en 19 s**, soit environ 1,6 s par temps. Une coupe toutes les 0,7 à 2,2 s, avec un seul plan long de 4,1 s (le graphique néon) qui sert de respiration. Trois « stop-hits » : la musique se coupe 0,2 à 0,3 s avant un impact, à chaque pivot du récit. |
| Arc narratif | Question → preuve (les marques) → thèse (« ce n'est pas un hasard ») → solution (le motion design) → 3 bénéfices (émotion, attention, clarté) → recadrage (« pas de la déco, de la stratégie ») → signature |
| Voix off | Aucune détectée : bande vocale faible et pas de modulation syllabique |

### Motifs récurrents
1. **L'œil et le cerveau** comme métaphores de l'attention et de la mémoire (cerveau gravé, cerveau 3D, globes oculaires).
2. **Paire typographique** : une amorce en italique fin et petite (« it's no », « to your », « this isn't »), puis un mot-clé en italique gras deux fois plus grand. Les lignes se chevauchent (interlignage négatif).
3. **Typographie fantôme** géante gris très pâle en arrière-plan, qui déborde du cadre.
4. **Grille pointillée** de type « plan d'architecte », sur fond blanc comme sur fond violet.
5. **Éclats blancs** (starbursts) aux coins de toutes les scènes violettes.
6. **Mise au point** : chaque mot apparaît par un passage du flou au net, et disparaît par l'inverse.

---

## 2. Palette mesurée

| Rôle | Hex | Usage |
|---|---|---|
| Violet primaire | `#751AA8` | Fonds pleins, mots-clés, tuiles, iris, aplats |
| Violet bannière | `#8331AE` | Bannière « EVER WONDERED? » |
| Violet logo | `#7B28A8` | Signature finale |
| Lavande | `#A763C8` | « Accident », « Movement. » (contraste 2,1:1 seulement) |
| Disque lavande translucide | `#BD6DF1` (≈ 50 %) | Superposé au cerveau gravé |
| Grille sur violet | `#8437AF` | Lignes pointillées |
| Blanc papier | `#FFFFFF` | Fonds clairs |
| Grille sur blanc | `#F4F4F4` | Lignes pointillées |
| Gris fantôme | `#E6E6E6` | Typographie géante d'arrière-plan |
| Anthracite | `#2F2F2F` | Texte sombre principal |
| Gris moyen | `#3D3D3D` | Mention « all right reserved » |
| Crème | `#F6F0E4` | Scène du téléviseur |
| Rouge téléviseur | `#A31D27` | Caisse du poste rétro |
| Noyer | `#72493F` | Pieds du poste |
| Rose cerveau | `#DE848D` | Cerveau 3D |
| Masques violet satiné | `#7C58B0` → `#A068D7` → `#C07FFA` | Masques de théâtre |
| Nuit marine | `#0B061A` | Fond du graphique |
| Cyan néon | `#40D5FE` | Courbe et nœuds lumineux |
| Grille du graphique | `#403182` | Perspective violette |
| Grès | `#C59C71` | Colonne corinthienne |
| Marbre blanc | `#D3D3D3` | Roi d'échecs |
| Jaune signalisation | `#FDD437` | Panneau « wet floor » |
| Bleu glacier / marine / ocre | `#E1EFFC` / `#365B87` / `#FEAF50` | Illustration du personnage qui glisse |

**Contrastes WCAG mesurés :**
- blanc sur violet et violet sur blanc : 8,5:1 (conforme) ;
- lavande sur violet : 2,1:1 (non conforme) ;
- gris de la mention finale : environ 2:1 (non conforme).

---

## 3. Typographie

| Usage | Police (identification visuelle) | Graisse / style | Taille approx. @ 720 px de large |
|---|---|---|---|
| Amorces (it's no, to your, Design, metaphors, Animated, Captures, instantly, this isn't, it's, Strategic) | **Playfair Display** | Italic 400 | 40 à 95 px |
| Mots-clés (stick in, your mind?, Motion, Story, text, Eyes, Visual, Decoration, Accident, Movement.) | **Playfair Display** | Bold / Black Italic 700–900 | 70 à 140 px |
| « EVER WONDERED? », « SOME BRANDS » | Grotesque condensée grasse, type Bebas Neue (identification approximative) | Capitales | Hauteur de capitale ≈ 75 à 90 px |
| Typographie fantôme | Playfair Display | Italic | 250 à 300 px, rognée par le cadre |
| Légende (make complicated concepts clear) | Playfair Display | Italic 400 | ≈ 30 px (trop petit sur téléphone) |

**Animation du texte :**
- l'entrée se fait par fondu et défloutage en 0,15 à 0,3 s, ou par balayage gauche → droite (« Design ») ;
- le mot « text » chute avec un flou de mouvement ;
- aucun contour ni ombre sur le texte.

---

## 4. Découpage plan par plan

*Positions données en % du cadre : x depuis la gauche, y depuis le haut. Caméra virtuelle 2D, sans profondeur de champ optique : le « flou » est un effet de mise au point simulé.*

### Temps 1 · 00.00–00.93 · Accroche « EVER WONDERED? »
- **Plan et caméra :** plan fixe centré, en collage 2D. Zoom avant rapide par la contraction des anneaux.
- **Éléments :**
  - fond blanc ; la première image est entièrement blanche, il n'y a donc **pas de vignette** ;
  - bannière violette `#8331AE` (≈ 78 % de la largeur, centrée à y ≈ 38 %) ;
  - cerveau en gravure demi-teinte noir et blanc, vu de profil (≈ 60 % de la largeur), qui chevauche le bas de la bannière ;
  - disque lavande translucide sur le lobe haut-droit, et demi-disque violet derrière le bas du cerveau ;
  - deux anneaux d'orbite noirs en pointillés, avec 4 billes noires pleines.
- **Texte :** « EVER WONDERED? » en blanc, grotesque condensée grasse en capitales, partiellement masqué par le cerveau.
- **Mouvement :**
  - 0,07–0,27 s : la bannière et le cerveau apparaissent par fondu et défloutage, avec une désaturation du violet vers le gris ;
  - 0,33–0,47 s : les anneaux entrent depuis le hors-champ (≈ 250 % → 100 %) et les billes tournent dans le sens horaire ;
  - 0,67–0,87 s : les anneaux s'effacent et le cerveau se transforme en disque violet plein ;
  - 0,93 s : écran blanc.
- **Transition :** fondu au blanc, puis zoom avant direct sur les tuiles.
- **Son :** whoosh d'ouverture vers 0,19 s, nappe grave.

### Temps 2 · 00.93–01.70 · Preuve « SOME BRANDS »
- **Plan et caméra :**
  - 1,00–1,20 s : très gros plan, l'échelle est ≈ 220 % ;
  - 1,27–1,33 s : dézoom rapide (ease-out exponentiel) vers une grille 2 × 2.
- **Éléments :**
  - 4 tuiles violettes `#751AA8` à coins arrondis (≈ 22 px), gouttière ≈ 26 px ; la grille fait ≈ 70 % de la largeur, son haut est à y ≈ 24 % ;
  - photos produits détourées : baskets sur boîte rouge, smartphone gris, bouchon d'objectif tenu en main, enseigne de restauration rapide ;
  - **les marques réelles sont visibles (Nike, Apple, Sony, McDonald's) : à ne jamais reproduire.**
- **Texte :** « SOME BRANDS », grotesque condensée violette, centré à y ≈ 71 %. Il monte et se défloute.
- **Transition :** 1,53–1,67 s, fondu au blanc avec flou.
- **Son :** impact grave sur le dézoom (≈ 75 % de l'énergie dans les sous-basses entre 1 et 2 s).

### Temps 3 · 01.70–03.07 · « stick in your mind? »
- **Éléments :**
  - fond blanc avec grille pointillée `#F4F4F4` (cellules ≈ 60 px) ;
  - lettres fantômes « stic / your » en `#E6E6E6`, qui débordent à droite ;
  - cerveau 3D réaliste rose `#DE848D` avec cervelet bordeaux (≈ 55 % de la largeur), placé **devant** le titre.
- **Texte :** sur deux lignes, en haut, à y ≈ 22–28 % :
  - « stick in » en Bold Italic violet ;
  - « your mind? » en Black Italic anthracite ;
  - les deux lignes se touchent.
- **Mouvement :**
  - 1,73–2,00 s : passage du flou au net, avec une échelle 95 → 100 % ;
  - maintien avec une dérive lente ;
  - 3,03 s : le plan est poussé vers le haut avec un flou de mouvement, en 2 images.
- **Transition :** poussée vers le haut, puis 1 image blanche, puis fondu lavande → violet.
- **Son :** accent à 2,09 s.

### Temps 4 · 03.07–04.33 · « it's no Accident »
- **Éléments :**
  - violet plein `#751AA8` ;
  - éclat blanc à 4–5 pointes acérées dans le coin haut-droit (≈ 35 % de la largeur) ;
  - illustration vectorielle en aplats : un homme roux glisse en arrière, une jambe en l'air ; il porte une sacoche ocre `#FEAF50`, un pull marine rayé `#365B87` et un pantalon bleu clair ; derrière lui, une tache bleu glacier `#E1EFFC` ; à côté, un panneau jaune « CAUTION WET FLOOR » `#FDD437` et une ellipse d'ombre au sol.
- **Texte :** ferré à gauche, à y ≈ 33–43 % :
  - « it's no » en Italic blanc ;
  - « Accident » en Bold Italic lavande, sur ≈ 90 % de la largeur.
- **Mouvement :** pose figée.
- **Transition :** 4,30 s, poussée vers la gauche en 2 images.
- **Son :** impact à 3,30 s, accents à 3,69 et 4,04 s. **Stop** (silence) de 4,15 à 4,45 s.

### Temps 5 · 04.33–06.13 · « Motion Design »
- **Éléments :**
  - fond blanc, après une coupe sèche depuis le violet en 2 images ;
  - grand œil 3D photoréaliste, iris violet, ombre violette, rogné à droite (≈ 70 % de la largeur, centre à x ≈ 85 % / y ≈ 65 %) ;
  - petit œil rogné dans le coin haut-gauche ;
  - texte fantôme « Motion Design » en bas à gauche ;
  - curseur de souris violet plein sous « Design ».
- **Texte :** « Motion » en Black Italic violet `#761DA8`, et « Design » en Italic anthracite, décalé à droite.
- **Mouvement :**
  - « Motion » se défloute (4,6–5,0 s) ;
  - « Design » se révèle par un masque gauche → droite (≈ 0,3 s) ;
  - le curseur apparaît en fondu, puis **clique** à 5,50 s avec une petite pastille violette ;
  - vers 6,0 s, toute la composition remonte d'environ 20 %.
- **Son :** impact grave à 4,46 s juste après le stop ; sous-basses dominantes entre 5 et 6 s.

### Temps 6 · 06.13–06.83 · « Motion bring »
- **Éléments :**
  - grille sur fond blanc ;
  - masques de théâtre 3D satinés violets (`#7C58B0` → `#C07FFA`) : une comédie en haut à gauche, une paire comédie + tragédie en bas à droite, toutes rognées par le cadre.
- **Texte :**
  - « Motion » géant, pivoté de 90° (lecture de bas en haut), en Italic anthracite, sur ≈ 70 % de la hauteur ;
  - « bring » pivoté lui aussi, en Italic violet, plus petit.
- **Mouvement :** entrée par poussée horizontale en 2 images, maintien de 0,5 s, sortie par poussée vers le haut.
- **Son :** attaque à 6,55 s.

### Temps 7 · 06.83–08.43 · « Feelings to your Story »
- **Éléments :**
  - fond crème `#F6F0E4`, avec un panneau photo plus clair ;
  - téléviseur à tube des années 60, rouge `#A31D27`, sur pieds compas en noyer (≈ 70 % de la largeur, à y ≈ 38–85 %), avec une ombre au sol.
- **Texte :** en haut, centré :
  - « Feelings » en Italic violet ;
  - « to your » en petit Italic anthracite ;
  - « Story » en Bold Italic anthracite, qui se défloute.
- **Mouvement :** l'écran enchaîne des extraits publicitaires toutes les ≈ 0,25 s : une main tenant une carte, un paysage, une coulure rouge, des rouges à lèvres.
- **Transition :** 8,40 s, un disque violet jaillit du centre de l'écran et remplit le cadre en ≈ 0,13 s (volet circulaire).
- **Son :** effets de « zapping » à 7,62 et 7,83 s.

### Temps 8 · 08.43–10.60 · « Animated text Captures Eyes instantly »
- **Éléments :**
  - fond violet avec grille `#8437AF` ;
  - éclats blancs en haut à droite et en bas à gauche ;
  - globe oculaire 3D blanc, iris gris (≈ 25 % de la largeur).
- **Texte :** construction en cascade diagonale :
  - « Animated » en Italic blanc ;
  - « text » en Black Italic blanc, ≈ 140 px ;
  - « Captures » en Italic ;
  - « Eyes » en Bold Italic ;
  - « instantly » en Italic.
- **Mouvement :**
  - « Animated » apparaît en fondu au centre, puis glisse vers le haut à gauche ;
  - l'œil apparaît teinté violet, puis se désature ;
  - « text » chute avec un flou de mouvement (9,07 s) ;
  - le reste de la cascade s'installe vers 9,5 s ;
  - 10,5–10,9 s : lavis lavande, puis blanc.
- **Son :** double impact de texte à 9,06 et 9,26 s, attaque à 10,29 s.

### Temps 9 · 10.60–14.70 · « Visual metaphors » (plan long)
- **Éléments :**
  - fond blanc ;
  - carte vidéo verticale (≈ 65 % de la largeur × 64 % de la hauteur), avec une ombre portée douce vers le bas à gauche ;
  - dans la carte : une courbe néon cyan `#40D5FE` à nœuds lumineux (halo) sur une grille en perspective `#403182`, fond `#0B061A` ; la courbe monte, marque un plateau, fait un pic vertical, puis redescend.
- **Texte :**
  - en haut, à y ≈ 6–11 % : « Visual » en Black Italic violet et « metaphors » en Italic anthracite ;
  - légende « make complicated concepts clear » à y ≈ 92 %, d'environ 30 px.
- **Mouvement :**
  - la carte se défloute, avec un fondu enchaîné interne depuis une silhouette de personnage ;
  - la caméra suit la courbe ;
  - 14,53 s : poussée vers le haut.
- **Son :** « ticks » à 11,68, 12,35, 12,70, 13,00 et 13,40 s, calés sur les nœuds de la courbe. **Stop** de 14,77 à 14,99 s.

### Temps 10 · 14.70–16.17 · « this isn't Decoration »
- **Éléments :**
  - fond blanc, avec un aplat violet qui monte occuper le **tiers inférieur** (≈ 38 %) ;
  - colonne corinthienne photoréaliste en grès `#C59C71`, qui part du bas du cadre et monte jusqu'à mi-hauteur ;
  - diamant taillé en brillant, qui tombe puis lévite au-dessus du chapiteau avec une légère oscillation.
- **Texte :** en haut, à y ≈ 7–11 % :
  - « this isn't » en Italic anthracite ;
  - « Decoration » en Black Italic violet, qui se défloute.
- **Transition :** 16,17 s, poussée vers la gauche, puis flash lavande, puis violet.
- **Son :** impact à 14,93 s ; « ting » cristallin du diamant à 15,37 s.

### Temps 11 · 16.17–17.87 · « it's Strategic Movement. »
- **Éléments :**
  - fond violet avec grille, éclat blanc en haut à droite ;
  - roi d'échecs 3D en marbre blanc laqué `#D3D3D3`, incliné de ≈ 10° vers la gauche.
- **Texte :** ferré à gauche :
  - « it's » et « Strategic » en Italic blanc ;
  - « Movement. » en Bold Italic lavande, qui se défloute.
- **Mouvement :**
  - le roi monte depuis le bas à droite avec un léger dépassement, et sa croix passe devant « Movement. » ;
  - 17,5–17,67 s : il redescend ;
  - le texte se floute et disparaît ;
  - 17,87 s : coupe au blanc.
- **Son :** impact à 16,39 s après un stop (16,08–16,35 s), swoosh de montée à 16,83 s, swoosh de descente à 17,55 s.

### Temps 12 · 17.87–19.11 · Signature
- **Éléments :** blanc uni, sans grille, avec le filigrane du créateur en bas, au centre.
- **Texte :**
  - « Web / Rank / Studio » empilé et centré, en Italic violet `#7B28A8` ;
  - « all right reserved » en Italic gris. **Faute d'anglais dans l'original** ; la forme correcte est « all rights reserved ».
- **Mouvement :** défloutage (17,9–18,3 s), maintien, puis floutage et fondu au blanc (18,9–19,0 s). **La dernière image est blanche.**
- **Son :** scintillement aigu (66 % de l'énergie dans les aigus entre 18 et 19 s), queue de réverbération, fin à −49 dB.

---

## 5. Compression vers 10 s (facteur 0,523)

| Temps | Original | 10 s | Durée |
|---|---|---|---|
| 1 Accroche | 0,00–0,93 | 0,00–0,50 | 0,50 |
| 2 Marques | 0,93–1,70 | 0,50–0,90 | 0,40 |
| 3 Cerveau | 1,70–3,07 | 0,90–1,60 | 0,70 |
| 4 Accident | 3,07–4,33 | 1,60–2,25 | 0,65 |
| 5 Motion Design | 4,33–6,13 | 2,25–3,20 | 0,95 |
| 6 Masques | 6,13–6,83 | 3,20–3,55 | 0,35 |
| 7 Téléviseur | 6,83–8,43 | 3,55–4,40 | 0,85 |
| 8 Œil / texte | 8,43–10,60 | 4,40–5,55 | 1,15 |
| 9 Graphique | 10,60–14,70 | 5,55–7,70 | 2,15 |
| 10 Colonne | 14,70–16,17 | 7,70–8,45 | 0,75 |
| 11 Échecs | 16,17–17,87 | 8,45–9,35 | 0,90 |
| 12 Signature | 17,87–19,11 | 9,35–10,00 | 0,65 |

**Risque :** compressés en 10 s, les 12 temps durent en moyenne 0,8 s, et deux tombent sous 0,4 s. C'est à la limite de la lisibilité, et les modèles génératifs tiennent mal plus de 6 à 8 scènes distinctes. **Option recommandée** : générer deux clips de 10 s enchaînés (temps 1 à 6, puis 7 à 12). On conserve ainsi le rythme original à l'identique, pour un total de 20 s.

---

## 6. Prompt Omni Flash : version fidèle

*Changements appliqués : les marques réelles sont remplacées par des produits génériques ; le filigrane et le nom de marque sont retirés (« Your Brand Studio » sert d'espace réservé) ; la faute « all right » est corrigée ; le titre est visible dès la première image ; la vidéo se termine sur la signature et non sur un écran blanc.*

```text
STYLE: Premium editorial motion-design collage for a creative-studio promo — crisp flat high-key studio light with soft contact shadows, clean white-paper scenes alternating with full-bleed electric violet #751AA8 scenes, photoreal cut-out 3D objects with gentle drop shadows over a faint dashed blueprint grid, giant pale-gray ghost typography bleeding off frame, locked-off 2D camera with snappy zoom, push and iris-wipe transitions, every word entering with a blur-to-sharp focus pull, glossy social-ad finish, no film grain.

SPECS: 1080x1920 vertical 9:16, 30 fps, exactly 10.0 s, 12 beats (19.1 s source pacing compressed x0.52), transitions every 0.35–1.15 s with one 2.15 s breathing beat at 5.55–7.70 s. All on-screen text in English, spelled exactly as written. No voiceover, no subtitles, no real brand logos, no watermark, no extra words.

TIMELINE:
0.00–0.50 | White #FFFFFF. Frame 1 already shows a violet #8331AE banner (78% frame width, centred at 38% height) with white bold condensed all-caps sans "EVER WONDERED?". A grayscale halftone-engraved human brain (side view, 60% width) overlaps the banner's lower edge, a 50%-opacity lavender #BD6DF1 disc on its upper-right lobe. Two concentric black dashed orbit rings carrying four solid black dots zoom in from 250% to 100% and spin clockwise; at 0.40 s the brain morphs into a solid violet #751AA8 circle and everything dissolves to white.
0.50–0.90 | Extreme close-up snaps out to a 2x2 grid of rounded violet #751AA8 tiles (22 px corner radius, 70% width, top at 24% height) holding cut-out generic unbranded products: sneakers on a red shoebox, a gray smartphone, a hand holding a black lens cap, a fast-food road sign. Below, violet bold condensed caps "SOME BRANDS" rises 40 px and de-blurs. Dissolve to white.
0.90–1.60 | White with a faint dashed light-gray #F4F4F4 grid (60 px cells) and giant ghost italic serif letters "your" in #E6E6E6 bleeding off the right edge. Two-line title upper-centre, lines touching: "stick in" (violet #751AA8 bold italic serif) over "your mind?" (charcoal #2F2F2F black italic serif). A realistic glossy pink #DE848D 3D brain with a darker maroon cerebellum (55% width) pops in front of the title with a blur-to-sharp focus pull. Whip-push upward with motion blur.
1.60–2.25 | One white flash frame, then full-bleed violet #751AA8 with a white jagged four-point starburst in the top-right corner (35% width). Left-aligned at 33–43% height: "it's no" (white light italic serif) above a huge "Accident" (lavender #A763C8 bold italic serif, 90% width). Below, a flat vector illustration of a red-haired man slipping backwards on a wet floor, one leg kicked high, ochre #FEAF50 satchel, striped navy #365B87 sweater, pale blue trousers, an ice-blue #E1EFFC blob behind him, a yellow #FDD437 "CAUTION WET FLOOR" A-frame sign, pale ground ellipse. Hard push left.
2.25–3.20 | Hard cut to white with grid. A giant photoreal 3D eyeball with a violet #751AA8 iris and soft violet shadow is cropped by the right edge (70% width, centre at 85% x / 65% y); a small eyeball peeks from the top-left corner. Ghost "Motion Design" in #E6E6E6 italic serif fills the lower left. "Motion" (violet black italic serif) blurs in; "Design" (charcoal italic serif) wipes on left to right; a solid violet mouse-pointer arrow fades in under "Design" and clicks with a small violet ripple dot. The whole layout eases upward by 20%.
3.20–3.55 | Fast horizontal push to the white grid: the word "Motion" rotated 90 degrees counter-clockwise in giant charcoal italic serif (70% of frame height) beside a smaller rotated violet "bring"; glossy satin-violet (#7C58B0 to #C07FFA) 3D theatre masks, a comedy mask top-left and a comedy-and-tragedy pair bottom-right, all cropped by the frame. Push up and out.
3.55–4.40 | Warm cream #F6F0E4 backdrop with a lighter photo panel. A 1960s red #A31D27 tube TV on splayed walnut #72493F legs, centred, 70% width, soft floor shadow. Title top-centre: "Feelings" (violet italic serif), "to your" (small charcoal italic), "Story" (charcoal bold italic, de-blurs). The TV screen zaps through four abstract ad clips (a hand holding a white card, a misty landscape, a red paint drip, lipstick tubes), 0.2 s each. A violet #751AA8 circle bursts from the screen centre and iris-wipes to fill the frame.
4.40–5.55 | Violet #751AA8 with a dashed violet #8437AF grid and white starbursts in the top-right and bottom-left corners. "Animated" (white italic serif) fades in at centre then slides top-left; a white 3D eyeball with a gray iris (25% width) fades in violet-tinted and desaturates to white; "text" (white black italic serif, very large) slams down with motion blur; "Captures", "Eyes" (bold) and "instantly" cascade diagonally down-right, the eyeball wedged between "text" and "Captures". Wash to pale lavender, then white.
5.55–7.70 | White. Title top-centre with overlapping lines: "Visual" (violet black italic serif) over "metaphors" (charcoal italic serif). A tall vertical video card (65% width x 64% height, square corners, soft bottom-left drop shadow) de-blurs in, showing a glowing neon cyan #40D5FE line chart with bright bloom nodes on a dark navy #0B061A perspective grid with violet #403182 lines; the line climbs, plateaus, spikes sharply upward then dips while the camera tracks it. Small charcoal italic serif caption at 92% height: "make complicated concepts clear". Fast push upward with motion blur.
7.70–8.45 | A violet #751AA8 block rises to fill the bottom 38% of the white frame. At the top, "this isn't" (small charcoal italic serif) and "Decoration" (violet black italic serif, blur-in). A photoreal sandstone #C59C71 Corinthian column rises from the bottom edge to mid-frame; a brilliant-cut diamond drops onto it and levitates just above the capital, gently bobbing. Push left with a lavender flash.
8.45–9.35 | Violet #751AA8 with dashed grid and a white starburst top-right. Left-aligned white italic serif "it's" / "Strategic", then "Movement." in lavender #A763C8 bold italic blurs in. A glossy white-marble #D3D3D3 3D chess king, tilted 10 degrees left, rises from the bottom-right with a slight overshoot, its cross overlapping "Movement."; it sinks back down while all text blurs out.
9.35–10.00 | Hard cut to plain white #FFFFFF, no grid. Centred stacked violet #7B28A8 italic serif wordmark "Your / Brand / Studio" with tight leading, and below it the small charcoal #3D3D3D italic serif line "all rights reserved"; it pulls focus from blur to sharp and holds.

TYPOGRAPHY (LOCKED): Serif is Playfair Display only — Italic 400 for lead-ins ("it's no", "to your", "Design", "metaphors", "Animated", "Captures", "instantly", "this isn't", "it's", "Strategic"), Bold/Black Italic 700–900 for keywords ("stick in", "your mind?", "Motion", "Accident", "Story", "text", "Eyes", "Visual", "Decoration", "Movement."); a bold condensed all-caps grotesque (Bebas Neue style) only for "EVER WONDERED?" and "SOME BRANDS"; keyword about 2x the lead-in size with negative leading so lines touch; text colours limited to violet #751AA8, lavender #A763C8, charcoal #2F2F2F, white #FFFFFF, ghost gray #E6E6E6; every word enters with a 0.15 s blur-to-sharp focus pull; no outlines, no text shadows.

SOUND: Mid-tempo (about 85 BPM) sub-heavy hip-hop/pop bed, no vocals; airy whoosh at 0.10; deep sub boom on the grid zoom-out at 0.65; tight snap at 1.10; whip swish at 1.58; hit at 1.73 with light accents at 1.93 and 2.11; music stops dead 2.17–2.33 then a heavy sub hit at 2.33; mouse click at 2.88; swish at 3.20 and accent at 3.43; TV channel-zap blips at 3.99 and 4.10; whoosh into the iris wipe at 4.40; double type-slam at 4.74 and 4.85; soft rising tick on each chart node at 6.11, 6.46, 6.65, 6.80, 7.01; whoosh up at 7.60; dead-stop silence 7.73–7.84 then an impact at 7.85 and a glassy diamond "ting" at 8.04; stop 8.41–8.56 then a hit at 8.58; whoosh up at 8.81, whoosh down at 9.18; hard cut at 9.36 into a bright shimmer sparkle 9.45–9.80 with a reverb tail fading to silence by 10.00.

FINAL FRAME: Held 9.70–10.00 — plain white #FFFFFF 1080x1920, no grid; centred at 30–45% height a three-line stacked italic serif wordmark "Your / Brand / Studio" in violet #7B28A8 (about 110 px cap height, tight leading), with "all rights reserved" in charcoal #3D3D3D italic serif (about 46 px) at 50% height; everything else empty, perfectly sharp, no watermark.
```

---

## 7. Prompt Omni Flash : version charte Dian K Pro

*Changements appliqués :*
- *palette noir `#0B0B0C` / or `#E3B34C` / ivoire `#F5F1E8` : les scènes blanches passent en noir, les scènes violettes en or ;*
- *typographie Playfair Display + Inter ;*
- *tout le texte dans la zone sûre (y 260–1600 px), taille minimale 44 px, contraste ≥ 10:1 ;*
- *page de garde dès la première image ;*
- *bruitages seuls, la musique Suno et la voix off étant ajoutées au montage ;*
- *signature Dian K Pro à la fin ;*
- *le texte à l'écran reste celui de l'original.*

```text
STYLE: Luxury editorial motion-design collage in a strict black-and-gold palette — deep black #0B0B0C scenes alternating with full-bleed warm gold #E3B34C scenes, crisp low-key studio light with soft gold rim highlights and soft contact shadows, photoreal cut-out 3D objects over a faint dashed blueprint grid, giant near-black ghost typography bleeding off frame, locked-off 2D camera with snappy zoom, push and iris-wipe transitions, every word entering with a blur-to-sharp focus pull, refined boardroom-grade finish, no film grain.

SPECS: 1080x1920 vertical 9:16, 30 fps, exactly 10.0 s, 12 beats, transitions every 0.35–1.15 s with one 2.15 s breathing beat at 5.55–7.70 s. All on-screen text in English, spelled exactly as written, kept inside the safe zone y 260–1600 px, minimum 44 px. No voiceover, no music, no subtitles, no real brand logos, no watermark, no text over any face, no extra words.

TIMELINE:
0.00–0.50 | Black #0B0B0C. Frame 1 is the cover: a gold #E3B34C banner (78% frame width, centred at 38% height) with black Inter ExtraBold all-caps "EVER WONDERED?" (cap height at least 110 px). A halftone-engraved human brain in gold-on-black duotone (side view, 60% width) overlaps the banner's lower edge, a 40%-opacity gold disc on its upper-right lobe. Two concentric thin ivory #F5F1E8 dashed orbit rings carrying four solid gold dots zoom in from 250% to 100% and spin clockwise; at 0.40 s the brain morphs into a solid gold circle and everything dissolves to black.
0.50–0.90 | Extreme close-up snaps out to a 2x2 grid of rounded gold #E3B34C tiles (33 px corner radius, 70% width, top at 26% height) holding cut-out generic unbranded products: sneakers on a black shoebox, a dark smartphone, a hand holding a black lens cap, a road sign. Below, gold Inter ExtraBold caps "SOME BRANDS" rises 60 px and de-blurs. Dissolve to black.
0.90–1.60 | Black with a faint dashed charcoal #2A2A2C grid (90 px cells) and giant ghost italic serif letters "your" in #1C1C1E bleeding off the right edge. Two-line title with its top at 20% height, lines touching: "stick in" (gold Playfair Display Bold Italic) over "your mind?" (ivory #F5F1E8 Playfair Display Black Italic). A realistic polished brushed-gold 3D brain (55% width) pops in front of the title with a blur-to-sharp focus pull. Whip-push upward with motion blur.
1.60–2.25 | One ivory flash frame, then full-bleed gold #E3B34C with a black jagged four-point starburst in the top-right corner (35% width). Left-aligned at 30–42% height: "it's no" (black Playfair Display Italic) above a huge "Accident" (black Playfair Display Bold Italic, 90% width). Below, a flat vector illustration in black, ivory and deep bronze #8A6A1F of a man slipping backwards on a wet floor, one leg kicked high, a small "CAUTION WET FLOOR" A-frame sign, pale ground ellipse. Hard push left.
2.25–3.20 | Hard cut to black with the charcoal grid. A giant photoreal 3D eyeball with an amber-gold iris and a soft gold rim light is cropped by the right edge (70% width, centre at 85% x / 62% y); a small eyeball peeks from the top-left corner. Ghost "Motion Design" in #1C1C1E italic serif fills the lower left. "Motion" (gold Playfair Display Black Italic) blurs in; "Design" (ivory Playfair Display Italic) wipes on left to right; a solid gold mouse-pointer arrow fades in under "Design" and clicks with a small gold ripple dot. The whole layout eases upward by 15%.
3.20–3.55 | Fast horizontal push to the black grid: the word "Motion" rotated 90 degrees counter-clockwise in giant ivory italic serif (spanning y 300–1580 px) beside a smaller rotated gold "bring"; glossy black-lacquer and gold-leaf 3D theatre masks, a comedy mask top-left and a comedy-and-tragedy pair bottom-right, all cropped by the frame. Push up and out.
3.55–4.40 | Deep black backdrop with a warm gold spotlight pool. A 1960s black-lacquer tube TV with brass dials on splayed walnut legs, centred, 70% width, soft floor shadow. Title at 16–26% height: "Feelings" (gold italic serif), "to your" (small ivory italic), "Story" (ivory bold italic, de-blurs). The TV screen zaps through four abstract clips (a hand holding a white card, a misty landscape, a paint drip, gold tubes), 0.2 s each. A gold #E3B34C circle bursts from the screen centre and iris-wipes to fill the frame.
4.40–5.55 | Gold #E3B34C with a dashed darker-gold #C99A35 grid and black starbursts in the top-right and bottom-left corners. "Animated" (black italic serif) fades in at centre then slides top-left; a white 3D eyeball with a gray iris (25% width) fades in gold-tinted and settles to natural white; "text" (black Playfair Display Black Italic, at least 200 px) slams down with motion blur; "Captures", "Eyes" (bold) and "instantly" cascade diagonally down-right in black, the eyeball wedged between "text" and "Captures". Dissolve to black.
5.55–7.70 | Black. Title at 16–24% height with overlapping lines: "Visual" (gold black italic serif) over "metaphors" (ivory italic serif). A tall vertical video card (62% width x 52% height, thin 2 px gold border, soft shadow) de-blurs in, showing a glowing gold #E3B34C neon line chart with bright bloom nodes on a dark perspective grid; the line climbs, plateaus, spikes sharply upward then dips while the camera tracks it. Ivory Inter Medium caption at 80% height: "make complicated concepts clear". Fast push upward with motion blur.
7.70–8.45 | A gold #E3B34C block rises to fill the bottom 38% of the black frame. At 16–24% height, "this isn't" (ivory italic serif) and "Decoration" (gold black italic serif, blur-in). A photoreal sandstone Corinthian column rises from the bottom edge to mid-frame; a brilliant-cut diamond drops onto it and levitates just above the capital, gently bobbing. Push left with an ivory flash.
8.45–9.35 | Gold #E3B34C with the darker-gold dashed grid and a black starburst top-right. Left-aligned black italic serif "it's" / "Strategic" at 18–30% height, then "Movement." in black bold italic blurs in. A glossy black 3D chess king with a thin gold edge light, tilted 10 degrees left, rises from the bottom-right with a slight overshoot, its cross overlapping "Movement."; it sinks back down while all text blurs out.
9.35–10.00 | Hard cut to black #0B0B0C, no grid. Centred gold #E3B34C Dian K Pro end card: a "DK" monogram — a tall serif "D" whose stem holds four thin circuit-board traces ending in small open circles, the "K" diagonals cutting through it — above wide-tracked serif capitals "DIAN K. PRO", tracked Inter capitals "PUBLIC HEALTH & DIGITAL STRATEGIST", and the line "Designed for Those Who Cannot Fail" flanked by thin gold rules ending in dots; it pulls focus from blur to sharp under a soft gold light sweep, then holds.

TYPOGRAPHY (LOCKED): Playfair Display Italic 400 for lead-ins ("it's no", "to your", "Design", "metaphors", "Animated", "Captures", "instantly", "this isn't", "it's", "Strategic") and Bold/Black Italic 700–900 for keywords ("stick in", "your mind?", "Motion", "Accident", "Story", "text", "Eyes", "Visual", "Decoration", "Movement."); Inter ExtraBold 800 caps for "EVER WONDERED?" and "SOME BRANDS", Inter Medium 500 for the caption and end-card subline; keywords at least 150 px, lead-ins at least 64 px, nothing under 44 px, negative leading so paired lines touch; text colours limited to gold #E3B34C, ivory #F5F1E8 and black #0B0B0C (contrast at least 10:1), ghost type #1C1C1E decorative only; every word enters with a 0.15 s blur-to-sharp focus pull; all text inside y 260–1600 px; no outlines, no text shadows.

SOUND: Sound effects only, no music bed and no vocals; airy whoosh at 0.10; deep sub boom on the grid zoom-out at 0.65; tight snap at 1.10; whip swish at 1.58; hit at 1.73 with light accents at 1.93 and 2.11; full silence 2.17–2.33 then a heavy sub hit at 2.33; mouse click at 2.88; swish at 3.20 and accent at 3.43; TV channel-zap blips at 3.99 and 4.10; whoosh into the iris wipe at 4.40; double type-slam at 4.74 and 4.85; soft rising tick on each chart node at 6.11, 6.46, 6.65, 6.80, 7.01; whoosh up at 7.60; silence 7.73–7.84 then an impact at 7.85 and a glassy diamond "ting" at 8.04; silence 8.41–8.56 then a hit at 8.58; whoosh up at 8.81, whoosh down at 9.18; hard cut at 9.36 into a warm low shimmer swell with a single bright chime at 9.45, reverb tail fading to silence by 10.00.

FINAL FRAME: Held 9.70–10.00 — black #0B0B0C 1080x1920, no grid; centred gold #E3B34C "DK" monogram (40% width) at 30–48% height, "DIAN K. PRO" wide-tracked serif capitals (80% width) at 53% height, "PUBLIC HEALTH & DIGITAL STRATEGIST" tracked capitals (85% width) at 60% height, "Designed for Those Who Cannot Fail" flanked by thin gold rules with dot ends at 66% height; everything perfectly sharp, no watermark.
```

---

## 8. Notes de production et de conformité

| Point | Recommandation |
|---|---|
| **Logo Dian K Pro** | Aucun modèle génératif ne reproduit fidèlement un logo. Au montage, remplacer les 0,65 dernières secondes par l'outro animée officielle, ou poser `assets/dk_pro_logo.png` par-dessus. |
| **Musique** | Poser le morceau Suno au montage avec trois coupes franches aux « stops » : 2,17–2,33 s, 7,73–7,84 s et 8,41–8,56 s. C'est la signature rythmique de la référence. |
| **Marques et droits** | Ne jamais reproduire les logos Nike, Apple, Sony ou McDonald's, ni le filigrane `@alee.gfx_`, ni le nom « Web Rank Studio ». La vidéo source est l'œuvre d'un tiers : elle sert de référence de style et ne doit pas être republiée. |
| **Fichier source dans le dépôt** | `data/uploads/` est normalement exclu par `.gitignore`, mais le dépôt web l'a contourné. Retirer la vidéo de la branche avant toute fusion dans `main`. |
| **Lisibilité** | Dans l'original, la lavande sur violet (2,1:1) et la légende de ≈ 30 px échouent au test de lecture sur téléphone. La version Dian K Pro corrige les deux. |
| **Rythme** | Si le rendu en 10 s paraît saccadé, générer deux clips de 10 s : les temps 1 à 6 et les temps 7 à 12, aux durées d'origine. |
