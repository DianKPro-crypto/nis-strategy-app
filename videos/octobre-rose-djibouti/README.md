# Octobre Rose Djibouti 2026 — film 3D 9:16

Film de sensibilisation au dépistage du cancer du sein (58,4 s, 1080 × 1920), calé sur le morceau Suno
« Ensemble, protégeons la vie » fourni par Dr Dian Sidibé. Storyboard validé : [`STORYBOARD.md`](STORYBOARD.md).

## Livrables (`out/`)

| Fichier | Usage | Spécifications |
|---|---|---|
| `OctobreRose_Djibouti_2026_9x16_WhatsApp.mp4` | Statut WhatsApp, partage mobile | H.264 High, 30 i/s, ≈ 15,3 Mo, AAC 128 kb/s |
| `OctobreRose_Djibouti_2026_9x16_master60.mp4` | Reels, Shorts, TikTok, projection verticale | H.264 High, 60 i/s, CRF 18, AAC 192 kb/s |
| `…_sans-logos.mp4` (×2) | Mêmes usages, **sans logos OMS ni Ministère** (diffusion possible avant autorisation) | Identiques |

## Découpage final (calé sur les paroles chantées)

| Temps | Séquence | Parole |
|---|---|---|
| 0,0 – 10,6 s | Page de garde « OCTOBRE ROSE » en relief or + ruban rose satiné qui se déroule | En ce mois d'Octobre Rose… peuvent sauver une vie |
| 10,6 – 17,4 s | Trois filaments roses (mères, sœurs, filles) qui se tressent | Mères, sœurs, filles de Djibouti : votre santé est précieuse |
| 17,4 – 22,5 s | Photo réelle du Centre Housseina (carte 3D) | Faites-vous dépister au Centre National Housseina, à Balbala |
| 22,5 – 26,8 s | Mammographe holographique en particules d'or, balayage rose | seul centre du pays doté d'une mammographie de dernière génération |
| 26,8 – 30,2 s | Photo réelle de l'Hôpital de Balbala « Cheiko » | ou à l'Hôpital Cheiko Balbala |
| 30,2 – 43,4 s | Ruban or (soutien) qui enlace le ruban rose, puis cercle familial | Pères, frères, époux… protéger toute la famille |
| 43,4 – 46,8 s | Carte 3D de Djibouti, zoom Balbala, 2 repères + carton récapitulatif | Un message de Dian K. Pro |
| 46,8 – 50,5 s | Ruban rose + fil d'or, logos Ministère de la Santé et OMS | Ensemble, protégeons la vie |
| 50,5 – 58,4 s | Logo Dian K. Pro en particules d'or → logo net + balayage lumineux | Designed for those who cannot fail |

## Régénérer

```bash
npm install
node render.mjs --stills 0,20,45            # contrôle de quelques images (frames/)
node render.mjs --from 0 --to 29.2 --out out/segA.mp4 &
node render.mjs --from 29.2 --to 58.4 --out out/segB.mp4
./finalize.sh                               # assemble + encode les deux livrables
```

Correction ciblée sans tout re-rendre : re-rendre le passage concerné puis `./patch.sh out/video_60.mp4 out/v2.mp4 out/passage.mp4:<début_s>`.

Version sans logos : `node render.mjs --from 46.8 --to 50.6 --partners 0 --out out/segNoLogo.mp4` avant `./finalize.sh`, qui l'insère automatiquement.

Rendu déterministe (Three.js r169, Chromium sans affichage, rendu logiciel) : chaque image est une fonction pure du temps.

## Points de vigilance avant diffusion

- **Logo OMS** : son usage est réglementé ; il faut une autorisation écrite du bureau OMS de Djibouti. Idem pour le logo du Ministère.
- **« Seul centre du pays doté d'une mammographie de dernière génération »** : affirmation à faire confirmer par écrit par le Ministère.
- **Orthographe** : le film suit l'enseigne officielle « Hôpital de Balbala “Cheiko” » (et non « Cheicko »).
- **Carte** : les repères des deux structures à Balbala sont **indicatifs** (même commune, positions non géoréférencées).
- **Photos** : photos des façades fournies par Dr Sidibé, sans visage. Confirmer qu'il s'agit de prises de vue réelles et non retouchées par IA.
