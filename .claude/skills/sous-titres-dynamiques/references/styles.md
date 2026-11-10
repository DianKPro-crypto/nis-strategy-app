# Catalogue des styles — sous-titres dynamiques Dian K Pro

Charte : noir `#0B0B0C`, or `#E3B34C`, blanc `#FFFFFF`, crème `#F6F1E7`. Polices : Inter, Playfair Display (toutes deux fournies avec HyperFrames, sans `@font-face`).
Les valeurs ci-dessous sont celles de `scripts/captions.mjs` (objet `STYLES`). En cas d'écart, le script fait foi.

Commun à tous les styles :
- texte blanc ou crème, ombre portée noire (3 px + halo de 26 px), ou voile local si le fond est clair ;
- mot actif et emphase en or ;
- un groupe visible à la fois ; entrée dès le premier mot (0,06 s avant) ; sortie au plus tard 0,25 s après le dernier mot, avec arrêt franc ;
- karaoké : chaque mot redevient blanc à la fin de sa prononciation, sauf le dernier du groupe, qui reste actif jusqu'à la sortie ;
- les mots sont espacés par une vraie espace placée avant chaque mot, dans un enveloppeur non animé. Ce balisage résiste à GSAP quand une scène est encore masquée : sans lui, « 12 000 enfants » s'affichait « 12 000enfants ».

## Contrastes vérifiés (WCAG 2.1)

| Combinaison | Ratio | Seuil |
| --- | --- | --- |
| Or sur noir | 10,1:1 | AAA ✔ |
| Blanc sur noir | 19,7:1 | AAA ✔ |
| Crème sur noir | 17,5:1 | AAA ✔ |
| Noir sur pastille or | 10,1:1 | AAA ✔ |
| Or, voile doux 45 %, fond moyen (luminance ≈ 120) | 4,8:1 | AA texte large ✔ |
| Or, voile doux 45 %, fond ≈ 150 | 3,7:1 | AA texte large ✔ (limite haute du voile doux) |
| Or, voile doux 40 %, fond ≈ 180 | 2,5:1 | ✖ → passer en voile plein |
| Or, voile plein 70 %, fond blanc (255) | 3,9:1 | AA texte large ✔ |
| Blanc, voile plein 70 %, fond blanc | 7,5:1 | AAA ✔ |

D'où les seuils de `luminance` : sous 60, rien ; de 60 à 150, voile doux ; au-delà de 150, voile plein.

---

## `or-karaoke` — signature (style par défaut)

- **Intention** : narration claire et chaleureuse. Le regard suit la voix mot à mot ; l'or signe la marque.
- **Typo** : Inter 900, casse normale, interlettrage −0,01 em, espacement des mots +0,1 em.
- **Taille** : 76 px (min 48) en 16:9 ; 92 px (min 56) en 9:16.
- **Groupes** : 5 mots / 36 caractères en 16:9 ; 3 mots / 22 caractères en 9:16. Un mot-outil compte pour un demi-mot.
- **Animation** : le groupe monte de 26 px en fondu (0,22 s, `power3.out`). Le mot actif passe à l'or, grossit à ×1,04 et se soulève de 6 % (0,04 à 0,1 s). Le mot en emphase reste en or et grossit à ×1,08 avec rebond (`back.out(2)`). Sortie en fondu de 0,12 s.
- **Pour** : Statut WhatsApp, Stories, plaidoyer, explications.
- **Éviter** : témoignages très émotionnels (préférer `editorial`).

## `pastille` — mot actif surligné

- **Intention** : énergie, rythme, lecture immédiate sur petit écran.
- **Typo** : Inter 900 en MAJUSCULES, interlettrage +0,02 em.
- **Taille** : 72 px (min 48) en 16:9 ; 88 px (min 56) en 9:16.
- **Groupes** : 3 mots / 26 caractères en 16:9 ; 2 mots / 14 caractères en 9:16.
- **Animation** : le groupe apparaît en pop (de ×0,86 à ×1, `back.out(1.7)`, 0,18 s). Une pastille or (rayon 0,22 em) passe d'un mot à l'autre ; le mot actif devient noir sur or, à ×1,04. Les mots en emphase restent en or hors pastille.
- **Lisibilité** : sur le mot actif, l'ombre du texte s'éteint (texte noir net sur or) et une ombre douce passe SOUS la pastille. Avec un halo noir autour de lettres noires, la lecture devenait floue et fatigante (retour de Dr Sidibé sur le premier test).
- **Pour** : accroches, campagnes jeunes, réseaux sociaux.
- **Éviter** : contenus solennels, projection en comité.

## `editorial` — récit et témoignage

- **Intention** : sobriété éditoriale, ton magazine, respect de la parole.
- **Typo** : Playfair Display 700, couleur crème ; emphase en *italique* or.
- **Taille** : 64 px (min 44) en 16:9 ; 78 px (min 52) en 9:16.
- **Groupes** : 6 mots / 42 caractères en 16:9 ; 4 mots / 26 caractères en 9:16. Coupure sur pause ≥ 0,25 s.
- **Animation** : fondu lent avec montée de 14 px (0,5 s, `power2.out`). Mot actif en or, à ×1,02. Sortie de 0,25 s.
- **Pour** : témoignages d'agents de santé ou de mères (consentement vérifié), récit de terrain, film institutionnel.
- **Éviter** : débits rapides (plus de 170 mots/min).

## `chiffre-cle` — les données frappent

- **Intention** : faire retenir un chiffre.
- **Typo** : Inter 700. Seuls les chiffres passent en Playfair Display 700, en or, à 1,45 em. Les autres mots en emphase (« zéro dose ») restent en Inter, en or.
- **Taille** : 70 px (min 46) en 16:9 ; 84 px (min 54) en 9:16.
- **Groupes** : 4 mots / 32 caractères en 16:9 ; 3 mots / 20 caractères en 9:16. Un chiffre n'est jamais séparé du nom qui le suit (« 12 000 enfants »).
- **Animation** : le chiffre est invisible jusqu'à sa prononciation, puis « tombe » (de ×1,6 à ×1, `expo.out`, 0,28 s). Les autres mots suivent le karaoké discret (or, ×1,03, soulèvement de 4 %).
- **Pour** : résultats, couverture vaccinale, besoins de financement.
- **Obligatoire** : chiffres validés, sinon mention « Données illustratives — à valider par l'équipe pays » à l'écran.

## `mot-a-mot` — accroche XXL

- **Intention** : capter l'attention dans les 3 premières secondes.
- **Typo** : Inter 900 en MAJUSCULES, très grand.
- **Taille** : 132 px (min 64) en 16:9 ; 150 px (min 72) en 9:16.
- **Groupes** : 1 à 2 mots, 10 à 16 caractères. Coupure sur pause ≥ 0,12 s.
- **Animation** : pop rapide (de ×0,6 à ×1, `back.out(2.2)`, 0,16 s). Emphase en or à ×1,06.
- **Pour** : teaser ≤ 30 s, slogans, dernière phrase avant l'outro.
- **Éviter** : vidéos longues (fatigue visuelle), contenus techniques.

## `institutionnel` — sous-titres classiques accessibles

- **Intention** : lisibilité maximale, conformité aux usages des institutions et accessibilité pour les personnes sourdes ou malentendantes.
- **Typo** : Inter 700 blanc, ponctuation conservée, 2 lignes au maximum, lignes équilibrées (`text-wrap: balance`).
- **Taille** : 52 px en 16:9 ; 60 px en 9:16 (fixe).
- **Groupes** : jusqu'à 14 mots / 84 caractères en 16:9 ; 9 mots / 44 caractères en 9:16. Coupure sur fin de phrase ou pause ≥ 0,6 s.
- **Animation** : fondu de 0,15 s, sans karaoké ni emphase.
- **Voile** : plein (70 %) par défaut, arrondi, à la taille du texte.
- **Pour** : projection en comité de pilotage, ministères, partenaires, sous-titrage d'accessibilité.

---

## Placement par format

| Format | `bas` (défaut) | `haut` | `milieu` |
| --- | --- | --- | --- |
| 16:9 (1920 × 1080) | bas du texte à environ 110 px du bord | haut du texte à environ 110 px | centre à 540 |
| 9:16 (1080 × 1920) | centre de bande à y 1280 (≈ 640 px du bas) | centre de bande ≥ y 420, bande ≥ y 280 | centre à 960 |

- Marges latérales de 10 % : largeur utile de 1536 px en 16:9 et de 864 px en 9:16.
- En 9:16, la bande doit rester dans y 260–1600 (CLAUDE.md) ; le script alerte sinon.
- `--y <px>` impose le centre de la bande.
