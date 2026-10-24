# Habillage vidéo « Djibouti × India » — Dian K. Pro

Script Python qui transforme la vidéo client en rendu « campagne de luxe » :
page de garde animée, étalonnage chaud et lumineux, netteté, drapeaux discrets,
fondus au noir, outro **Dian K. Pro**, export H.264 haute qualité.

---

## 1. Contenu du dossier

| Fichier | Rôle |
|---|---|
| `montage_dian_k_pro.py` | le script |
| `requirements.txt` | dépendances Python |
| `drapeau_djibouti.png` | drapeau de Djibouti |
| `drapeau_inde.png` | drapeau de l'Inde, **corrigé** : Ashoka Chakra à 24 rayons (l'image d'origine en comptait 27) |
| `dk_monogramme.png` | monogramme DK doré de l'outro (facultatif) |
| `fonts/` | Playfair Display et Inter (licence libre OFL) |

À ajouter vous-même : **`video_client.mp4`** (`.mov` accepté).

---

## 2. Installation (une seule fois)

1. Installez **Python 3.10 ou plus récent** : <https://www.python.org/downloads/>
   *Windows : cochez « Add Python to PATH » pendant l'installation.*
2. Ouvrez un terminal **dans ce dossier** :
   - Windows : clic droit dans le dossier > « Ouvrir dans le Terminal »
   - macOS : clic droit sur le dossier > « Nouveau terminal au dossier »
3. Installez les dépendances :

```bash
python -m pip install -r requirements.txt
```

*macOS : remplacez `python` par `python3`.*

FFmpeg est installé automatiquement avec MoviePy (paquet `imageio-ffmpeg`).
Vous n'avez **pas** besoin de `ffmpeg-python` : c'est une simple surcouche, non
maintenue depuis 2019, qui n'installe pas FFmpeg.

---

## 3. Lancer le rendu

Copiez `video_client.mp4` dans ce dossier, puis :

```bash
# 1) Aperçu des 20 premières secondes (environ 2 min de calcul) : validez le rendu
python montage_dian_k_pro.py --preview 20

# 2) Rendu complet
python montage_dian_k_pro.py
```

Le script produit :

- `video_client_final.mp4` : la vidéo finale ;
- `video_client_final_vignette.png` : la page de garde, à utiliser comme miniature ;
- `video_client_final.log` : le journal technique, utile en cas de problème.

Une barre de progression affiche le pourcentage et le temps restant.
Le fichier final n'apparaît qu'une fois le rendu complet : une interruption
(Ctrl+C, coupure) ne laisse jamais de vidéo corrompue.

---

## 4. Ce que fait le script

| Étape | Outil | Détail |
|---|---|---|
| Page de garde (5 s) | MoviePy | Diptyque des drapeaux en satin, lente poussée caméra et reflet lumineux. Titre visible **dès la première image**, qui sert de miniature. |
| Étalonnage | FFmpeg | Luminosité, contraste et saturation légèrement relevés. Ombres teal, hautes lumières chaudes, diffusion lumineuse type « Pro-Mist ». La dominante verte des téléphones est neutralisée. |
| Netteté | FFmpeg | Débruitage léger, mise à l'échelle Lanczos, accentuation de la luminance. |
| Drapeaux | FFmpeg | Deux médaillons cerclés d'or qui se chevauchent, symbole du partenariat. Ils apparaissent en fondu après l'ouverture. En 16:9 avec une source portrait, les drapeaux deviennent des panneaux latéraux flous et assombris. |
| Fondus | FFmpeg | Fondu au noir de 2 s à l'entrée et à la sortie de la vidéo client. Le son a des fondus de 0,5 s pour ne couper ni le premier ni le dernier mot. |
| Son | FFmpeg | Stéréo 48 kHz, volume normalisé à −16 LUFS (norme web et mobile). |
| Outro (5 s) | MoviePy | Monogramme DK, « Dian K. Pro » avec reflet doré, filet qui se dessine, signature. |
| Export | FFmpeg | H.264 High, CRF 18, BT.709, AAC 192 kb/s, `faststart` (lecture immédiate en ligne). |

**Pourquoi ce partage MoviePy / FFmpeg ?** Traiter 56 minutes image par image en
Python prendrait plusieurs heures et saturerait la mémoire. Ici, MoviePy compose
les séquences graphiques courtes. FFmpeg traite le corps de la vidéo en flux
continu et assemble le tout en **un seul encodage**. La mémoire reste donc
constante, quelle que soit la durée.

---

## 5. Options utiles

```bash
python montage_dian_k_pro.py --help                  # toutes les options
python montage_dian_k_pro.py --format 16:9 --output video_16x9.mp4   # projection, comité
python montage_dian_k_pro.py --title "Two Shores,|One Ocean"         # | = retour à la ligne
python montage_dian_k_pro.py --music musique_suno.mp3                # musique sous garde et outro
python montage_dian_k_pro.py --grade subtil                          # étalonnage plus discret
python montage_dian_k_pro.py --emblem top-right                      # position des médaillons
python montage_dian_k_pro.py --crf 16 --preset slow                  # master archive (plus lent)
python montage_dian_k_pro.py --preset faster                         # brouillon rapide
```

| Option | Défaut | Effet |
|---|---|---|
| `--format` | `auto` | `auto` suit l'orientation de la source : portrait → 1080×1920, paysage → 1920×1080 |
| `--kicker` / `--title` / `--subtitle` | voir page de garde | textes de la page de garde |
| `--cover-seconds` / `--outro-seconds` | 5 / 5 | durées de la page de garde et de l'outro |
| `--fade` / `--audio-fade` | 2 / 0,5 | durée des fondus image et son |
| `--grade` | `luxe` | `luxe`, `subtil` ou `aucun` |
| `--sharpen` | 0,7 | netteté (0 = désactivée) |
| `--emblem` / `--emblem-opacity` | `top-left` / 0,9 | position et opacité des médaillons (`off` pour les masquer) |
| `--crf` | 18 | qualité : 16 = master, 18 = haute, 21 = web léger |
| `--no-loudnorm` | — | conserver le volume d'origine |

---

## 6. Temps de calcul indicatifs

Mesurés sur une machine à 4 cœurs ; un ordinateur portable récent à 8 cœurs va environ 2 fois plus vite.

| Vidéo source | Temps de rendu | Mémoire |
|---|---|---|
| 56 s, portrait (votre fichier) | environ 4 min | environ 1,5 Go |
| 56 min, 1080p | 1 h 30 à 3 h selon la machine | environ 1,5 Go, **constante** |

Avec `--preset faster`, le rendu est environ 2 fois plus rapide, au prix d'un fichier un peu plus lourd.
La consommation mémoire ne dépend pas de la durée : elle a été vérifiée stable du début à la fin d'un rendu 1080p.

---

## 7. Points de vigilance avant diffusion

1. **Qualité de la source.** Le fichier reçu fait 368×656 pixels : il a été
   compressé par WhatsApp. Aucun filtre ne recrée un détail perdu. Demandez
   l'**original du téléphone** (1080×1920 ou plus), via un lien Drive ou
   WeTransfer, ou un envoi WhatsApp « en tant que document ».
2. **Drapeau de l'Inde.** L'image fournie comportait un Ashoka Chakra à 27 rayons ;
   le Flag Code of India en impose 24. Le fichier livré est corrigé. Si vous
   changez de drapeau, vérifiez ce point.
3. **Consentement.** Confirmez l'accord écrit de l'intervenante pour une
   diffusion publique de la vidéo.
4. **Textes.** « Two Shores, One Ocean / Voices of a shared future » est une
   proposition. Ajustez-la au message exact de la vidéo avec `--title` et `--subtitle`.
5. **Statut WhatsApp.** La limite est de 90 s. Le script vous avertit si la version
   9:16 dépasse cette durée.

---

## 8. Dépannage

| Message | Solution |
|---|---|
| `Dépendance manquante ou trop ancienne` | `python -m pip install --upgrade -r requirements.txt` |
| `Fichier introuvable` | vérifiez le nom du fichier et que le terminal est ouvert dans ce dossier |
| `Échec de FFmpeg` | envoyez le fichier `.log` produit à côté de la vidéo |
| `Espace disque faible` | libérez de la place : prévoyez environ 7 Go pour 56 min |
