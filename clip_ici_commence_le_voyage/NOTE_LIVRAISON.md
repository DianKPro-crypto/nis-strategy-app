# « Ici commence le voyage » — note de livraison

## Fichiers

| Livrable | Emplacement |
|---|---|
| Version 16:9 (1920 × 1080, 25 i/s) | `exports/Ici_commence_le_voyage_16x9.mp4` |
| Version 9:16 (1080 × 1920, 25 i/s) | `exports/Ici_commence_le_voyage_9x16.mp4` |
| Projet Remotion | `project/` (`npm install`, puis `npm run studio` ou `npm run render:16x9` / `render:9x16`, puis `tools/finalize.sh`) |
| Configuration des scènes, durées, cadrages | `project/src/config/scenes.ts` |
| Vignettes extraites | `project/public/scenes/scene_01.jpg` … `scene_13.jpg` |

Encodage : H.264 High, yuv420p, CRF 17, audio AAC 320 kb/s 48 kHz repris directement du fichier original, `faststart`.

Contrôles effectués sur les deux fichiers : 6 657 images, 266,28 s, 13 scènes dans l'ordre, pic audio −2,5 dBFS (aucun écrêtage), −15,4 LUFS (identique à l'original), aucun noir involontaire (seul noir : fondu final 265,5–266,2 s), titres lisibles hors visages.

Rendu : `cd project && npm install && node scripts/render.mjs Voyage16x9 ../exports/_raw_16x9.mp4` (puis `Voyage9x16`), puis `tools/finalize.sh`. Les titres sont des PNG pré-rendus en Playfair Display (`tools/make_titles.py`), ce qui évite tout chargement de police au rendu.

## Ajustements réalisés

1. **Durée : 4 min 26,28 s, pas 4 min 20 s.** Le fichier audio dure 266,28 s. Les dernières paroles (« Au cœur de ma vie ») se terminent à 255,0 s, mais la musique reste pleine (environ −11 à −13 dB RMS) jusqu'à 262 s, puis décroît naturellement jusqu'à 266 s. Pour tenir 260 s, il faudrait couper ou fondre cette fin instrumentale : ce serait une vraie modification musicale. Conformément à la consigne, je n'ai pas modifié l'audio. Le film suit la chanson entière, et son fondu au noir (262,6 → 265,8 s) accompagne la réverbération finale.
   *Si le format de 260 s est impératif :* fondu audio de 255,5 à 260 s. La voix reste intacte, mais la cadence instrumentale finale est perdue. Ce choix vous revient.
2. **Synchronisation sur les paroles réelles.** J'ai récupéré l'alignement mot à mot de la chanson auprès de Suno (identifiant intégré au fichier). Les 13 coupes de scène tombent dans les respirations entre deux phrases. Exemples : « Le même banc, mais une place offerte » (131 s) arrive pendant la scène 07, et « la forme d'un pardon » (202 s) pendant la scène 10. L'ordre narratif est respecté.

   | Scène | Début | Repère chanté |
   |---|---|---|
   | 01 Recueillement | 0:00 | Intro « Ya Allah… Je reviens à Ton amour » |
   | 02 Les départs | 0:23 | « Je regardais les départs sur la mer » |
   | 03 Le souffle | 0:47,5 | « Un vent léger a traversé mon voile » |
   | 04 Le cœur | 1:07,6 | 1er refrain « Ici, ici commence le voyage » |
   | 05 Le premier pas | 1:26,6 | « Je fais un pas, je laisse entrer le jour » |
   | 06 Déposer les regrets | 1:46 | « J'ai déposé mes regrets sur la table » |
   | 07 Offrir une place | 2:05,5 | « Le même banc, mais une place offerte » |
   | 08 S'ouvrir au monde | 2:25,6 | 2e refrain |
   | 09 Partager | 2:44,6 | « Au creux du monde, une lumière veille » |
   | 10 Pardonner | 3:04 | Pont « … la forme d'un pardon » |
   | 11 Avancer | 3:24,5 | Refrain final |
   | 12 Cheminer ensemble | 3:43,6 | « Mon cœur apprend une route nouvelle » |
   | 13 Être ici | 4:03 | Outro « Je suis ici… Au cœur de ma vie » |

3. **Page de garde.** Le titre est visible dès la première image, posé sur la mer et le soleil du portrait de référence, sans visage. Un fondu mène ensuite au gros plan de la scène 01 avant « Ya Allah » (6,3 s).
4. **Portrait de référence HD.** Je l'ai utilisé en priorité là où il correspond au storyboard : au détail « main sur le cœur » de la scène 04 et au portrait final de la scène 13, avec un lent recul qui révèle la mer, puis le titre.
5. **Format vertical recomposé.** Chaque plan a un cadrage défini à part. Les images sont intégrées en bande sur un fond flou issu de la même photo. Un recadrage plein écran aurait coupé l'une des deux femmes ou agrandi la source de plus de 8 fois. Le titre reste dans la zone sûre (y 260–1600).
6. **Numéros du storyboard supprimés** par un recadrage de 46 px à gauche de chaque vignette, qui ne coupe aucun sujet. Les séparations de la planche sont retirées, et aucune image n'est étirée.

## Limites des sources (à connaître avant diffusion)

- **Définition.** Les vignettes de la planche ne mesurent qu'environ 360 × 220 px. Pour le 1080p, elles sont agrandies de 4,8 à 7 fois. J'ai utilisé un agrandissement Lanczos avec une accentuation légère et un grain fin. **Ce n'est pas un gain de définition réel** : les plans des scènes 01 à 12 restent doux, surtout en gros plan. Seul le portrait de référence (1672 × 941) est net. Pour un rendu « broadcast », fournissez les 13 images originales en haute définition : il suffit de remplacer les fichiers dans `public/scenes/` et de relancer le rendu.
- **Animation.** C'est un film photographique : rapprochements, reculs et glissements latéraux lents, fondus de 0,4 à 0,8 s. **Aucun mouvement corporel n'a été généré** (respiration, voile, vagues). Un outil de génération vidéo (Higgsfield) est connecté, mais je ne l'ai pas utilisé : il consomme des crédits et peut altérer les visages et les mains. Je peux l'essayer sur 2 ou 3 plans si vous le souhaitez.
- **Provenance des images.** Les visuels fournis semblent générés par IA, et non issus de vos photos de terrain. Ils conviennent à un clip de fiction, mais ne doivent pas être présentés comme des scènes réelles ou documentaires. Une mention du type « Images de fiction » est recommandée si le clip accompagne une communication institutionnelle.
- **Charte Dian K Pro.** L'outro animée Dian K Pro, prévue par votre charte vidéo, **n'est pas incluse**. Le brief demandait de ne mettre ni logo ni signature et de finir par un fondu au noir. Je peux l'ajouter après la fin de la chanson sur demande.
- **Statut WhatsApp.** Avec 4 min 26 s, la version 9:16 dépasse la limite de 90 s. Pour un Statut, il faut un extrait, par exemple le refrain final avec les scènes 11 à 13, de 3:24 à 4:26 environ (62 s).
- Pas de sous-titres, ni d'ambiance de mer ajoutée (aucun fichier fourni). Pas de voix off.
