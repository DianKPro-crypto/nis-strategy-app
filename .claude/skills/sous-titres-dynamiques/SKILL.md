---
name: sous-titres-dynamiques
description: Sous-titres dynamiques (karaoké mot à mot, mot actif en or, pastille, chiffres clés, accroche XXL, sous-titres institutionnels accessibles) pour les vidéos et animations HyperFrames de Dr Dian Sidibé, aux couleurs Dian K Pro. À utiliser quand on demande des sous-titres, captions, sous-titrage animé, texte synchronisé à la voix off, karaoké, « style Captions / TikTok / Reels », ou d'importer des sous-titres (.srt/.vtt) faits dans une autre application (Captions, Descript, YouTube). Couvre la transcription française sans traduction parasite, le nettoyage (hallucinations Whisper, sigles PEV/OMS/Gavi), la coupe des groupes de mots, six styles maison, le placement 16:9 / 9:16, le contraste et le contrôle qualité.
---

# Sous-titres dynamiques — charte Dian K Pro

Outil : `scripts/captions.mjs` (Node ≥ 18, aucune dépendance). Depuis la racine du dépôt :

```bash
CAP=.claude/skills/sous-titres-dynamiques/scripts/captions.mjs
node $CAP styles      # les six styles
node $CAP aide        # toutes les options
```

## 0. Garde-fous (à lire avant tout)

- **Par défaut, pas de sous-titres** (CLAUDE.md). Cette compétence ne s'applique que si Dr Sidibé les demande explicitement pour la vidéo en cours. Une demande pour une vidéo ne vaut pas pour la suivante.
- Les sous-titres reprennent **exactement ce qui est dit**, sans paraphrase. Noms propres, sigles et chiffres sont vérifiés à l'écoute.
- Si les chiffres prononcés ne sont pas validés, la mention « Données illustratives — à valider par l'équipe pays » reste affichée à l'écran. C'est un calque à part, pas un sous-titre.
- Jamais de texte sur un visage. Statut WhatsApp : 90 s maximum (`--whatsapp` contrôle la durée).
- L'application **Captions** n'a pas de connecteur : Claude ne peut ni s'y connecter ni y lire des préréglages. Si une vidéo y a déjà été sous-titrée, exporter le fichier de sous-titres (.srt/.vtt) si l'application le permet, sinon le texte, puis passer par `from-srt` (§ 1-C). Les styles d'ici sont des créations originales à la charte : ils ne copient pas les modèles de Captions.

## 1. Obtenir les mots minutés

**A. Voix off de Dr Sidibé (cas normal) : transcrire le fichier VOIX SEUL, jamais le mixage avec la musique Suno.**

```bash
npx hyperframes transcribe assets/voix.wav --model small --language fr     # voix propre
npx hyperframes transcribe assets/voix.wav --model medium --language fr    # voix bruitée ou sur musique
```

⚠ Ne jamais lancer `transcribe` sans `--model` : le modèle par défaut (`small.en`) **traduit le français en anglais** sans prévenir. Le contrôle (étape 2) détecte ce cas.

**B. API externe (meilleure précision, clé requise)** : OpenAI ou Groq Whisper avec `timestamp_granularities[]=word`, `language=fr`. Le JSON obtenu est lu directement par `captions.mjs`.

**C. Fichier .srt / .vtt venu d'ailleurs (Captions, Descript, YouTube)** : le minutage n'existe que par phrase. Le karaoké est alors reconstitué au prorata des caractères, donc approximatif.

```bash
node $CAP from-srt export.srt --out assets/mots.json
```

**D. Projet Descript existant** (connecteur actif) : `export_transcript` au format `srt`, puis C.

## 2. Contrôler puis nettoyer (obligatoire)

```bash
node $CAP check assets/transcript.json --whatsapp     # ✖ = bloquant, ⚠ = à vérifier
node $CAP fix   assets/transcript.json --out assets/mots.json
```

- `check` repère : un texte devenu anglais, plus de 20 % de jetons musique (♪), les hallucinations Whisper connues (« Sous-titres réalisés par la communauté d'Amara.org », « Merci d'avoir regardé », « Merci. » isolé), les chevauchements, les mots trop courts, les silences et la durée.
- `fix` retire hésitations (« euh ») et hallucinations certaines. Il rattache la ponctuation isolée avec une espace fine (« Pourquoi ? », « 90 % »), recolle « 12 000 » et « l'UNICEF », remet le minutage dans l'ordre, puis applique `references/lexique-sante-publique.json` (PEV, OMS, Gavi, DTC3…).
- **Relire ensuite `mots.json`**. Ajouter au lexique les noms de lieux, de personnes et les sigles du pays mal reconnus, puis relancer `fix`.

## 3. Choisir le style

| Style | Pour | Groupe (16:9 / 9:16) |
| --- | --- | --- |
| `or-karaoke` **(défaut)** | Narration, plaidoyer, Statut WhatsApp, Stories | 5 / 3 mots |
| `pastille` | Accroches énergiques, réseaux sociaux, jeunes publics | 3 / 2 |
| `editorial` | Témoignages, récit de terrain, film institutionnel posé | 6 / 4 |
| `chiffre-cle` | Messages chiffrés, résultats, plaidoyer budgétaire | 4 / 3 |
| `mot-a-mot` | Teaser ≤ 30 s, slogans (fatigue au-delà) | 2 / 2 |
| `institutionnel` | Projection en comité, ministères, accessibilité | 2 lignes |

Détails, paramètres et contrastes : `references/styles.md`. Pour aider Dr Sidibé à choisir, générer la planche visuelle des styles : `node $CAP planche --format 9x16 --out planche.html`.

Règle de mise en valeur : **un seul mot ou expression en or par groupe**. Priorité aux chiffres, puis à `--emphase "mot,expression"`, puis au lexique (sigles, « zéro dose »…). `--sans-emphase` désactive la mise en valeur.

## 4. Générer la sous-composition

```bash
node $CAP build assets/mots.json --style or-karaoke --format 9x16 \
     --out compositions/captions.html [--emphase "zéro dose"] [--position bas|milieu|haut] [--scrim auto|aucun|doux|plein] --whatsapp
```

Le script écrit `compositions/captions.html` et affiche **l'hôte à coller dans `index.html`**. Mettre son `data-start` à l'instant où démarre l'`<audio>` de la voix off : les temps sont relatifs au fichier voix. Il ne peut y avoir qu'un seul hôte `data-track-kind="captions"` par vidéo.

Ce que garantit le générateur (contrat HyperFrames) :
- un seul groupe visible à la fois, avec un arrêt franc (`tl.set … visibility:hidden`) à la fin de chaque groupe, et un auto-contrôle intégré ;
- une coupe à la française : jamais de groupe qui finit sur « de », « et » ou « l' » ; « parce que », « zéro dose » et « 12 000 enfants » ne sont jamais coupés ; pas de mot orphelin en fin de phrase ;
- un balisage des mots qui résiste à GSAP quand une scène est mesurée alors qu'elle est encore masquée : les espaces entre mots ne sautent pas (bug réel constaté au rendu, corrigé) ;
- la taille ajustée à la largeur (`fitTextFontSize` à l'exécution, estimation au moment de la construction), avec un plancher de 40 px ou plus ;
- Inter et Playfair Display (polices fournies avec HyperFrames), sans `Math.random`, sans horloge, déterministe ;
- une zone de texte dans le cadre titre 80 %. En 9:16, la bande reste dans y 260–1600 (alerte sinon).

Ne jamais retoucher les minutages dans le HTML : corriger `mots.json`, puis régénérer.

## 5. Placement et lisibilité

- **Visages d'abord.** Regarder les photos ou plans sous la bande. Si un visage est dessous, utiliser `--position haut` ou `milieu`, ou `--y <px>`, ou recadrer le média.
- **Contraste.** Mesurer la luminance de la bande, puis appliquer la recommandation :
  ```bash
  node $CAP luminance assets/plan.mp4 --style or-karaoke --format 9x16
  ```
  - sous 60/255 : ombre portée seule ;
  - de 60 à 150 : `--scrim doux` (voile local de 45 %) ;
  - au-delà de 150 : `--scrim plein` (70 %).

  Le voile est local, à la taille du texte, jamais une bande pleine largeur. Le voile global sur photo reste ≤ 35 %.
- En 16:9, ne pas superposer les sous-titres à un bandeau nom/titre (lower third) : remonter l'un des deux.

## 6. Vérifier avant de livrer

```bash
npx hyperframes check --json --at-transitions   # échantillonne chaque entrée/sortie de groupe ; corriger chaque erreur
npx hyperframes snapshot --at 2,8,15            # trois instants : début, milieu, chiffre clé
```

Liste de contrôle :
- synchronisation : le mot en or tombe sur la syllabe prononcée (vérifier deux ou trois passages à l'aperçu) ;
- aucun groupe resté affiché, aucun texte sur un visage ;
- noms et sigles exacts ;
- chiffres identiques à la voix, avec mention illustrative si non validés ;
- lisible sur un téléphone tenu à bout de bras ;
- WhatsApp ≤ 90 s.

Rendre seulement après validation de l'aperçu par Dr Sidibé.

### Aperçu sans le CLI HyperFrames

Dans cet environnement cloud, le mode automatique bloque l'installation et l'exécution de HyperFrames, et le réseau bloque les CDN. Pour voir quand même les sous-titres bouger, `scripts/apercu.cjs` assemble le projet dans Chromium avec GSAP et encode un MP4 :

```bash
npm pack gsap@3.12.5 && tar -xzf gsap-3.12.5.tgz        # récupère GSAP sans rien installer (dossier de travail temporaire)
NODE_PATH=$(npm root -g) node .claude/skills/sous-titres-dynamiques/scripts/apercu.cjs <projet> apercu.mp4 --gsap package/dist/gsap.min.js
NODE_PATH=$(npm root -g) node .claude/skills/sous-titres-dynamiques/scripts/apercu.cjs <projet> cle.png --gsap package/dist/gsap.min.js --at 0,6,12
```

C'est un aperçu, pas le rendu de livraison : pas d'ajustement `fitTextFontSize` (ce sont les tailles calculées à la construction qui s'appliquent), pas de traitement média, un seul `<audio>`. La livraison passe par `npx hyperframes check` puis `render`. Les alertes `[caption-lint]` éventuelles sont affichées.

## 7. Autres voies

- **Composants du registre HyperFrames** (`npx hyperframes catalog --tag caption-style`, par exemple `caption-highlight`) : à recolorer aux couleurs de la charte avant usage. Utiles pour un effet absent d'ici (glitch, particules, texte derrière la personne via `remove-background`).
- **Descript** (connecteur actif) : pour une vidéo filmée déjà montée dans Descript, demander à Agent Underlord d'ajouter des sous-titres en précisant la charte (Inter 900, blanc, mot actif #E3B34C, ombre noire, bas d'écran hors visages), puis `publish_project`. Le rendu y est moins contrôlé qu'ici.

## 8. Faire évoluer la compétence

- Nouveau style : ajouter une entrée dans `STYLES` (`captions.mjs`) et sa fiche dans `references/styles.md`, puis vérifier avec `planche`.
- Nouveaux termes : `references/lexique-sante-publique.json` (`remplacements`, `expressions`, `emphase`).
