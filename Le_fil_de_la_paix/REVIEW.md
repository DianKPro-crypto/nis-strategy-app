# Note de revue

**Parti pris.** Film photographique animé, pas de vidéo générée : cadrages lents sur la photo originale et les 12 vignettes,
coupes franches sur les phrases chantées, un seul fondu (ellipse de la réparation, 147,2 s).
Deux mises en page : plein cadre pour l’intro et les couplets ; « cadre + texte » sur fond noir #0B0B0C pour les refrains, le pont et la fin.
Motif graphique unique : une couture or qui gagne un point à chaque vers chanté (27 points), sans effet surnaturel.
Paroles : mots révélés à l’instant chanté (alignement Suno du morceau, interpolé à l’intérieur de chaque vers) ; environ deux tiers des vers affichés.

**Mesuré.** `hyperframes check` : 0 erreur, contraste 9/9. Durée, dimensions, cadence, images noires et silences : voir `scripts/06_finalize.sh`.
**Seulement regardé.** Cadrages, fidélité des visages, lisibilité (planches de contrôle).
**Non vérifié.** Le chant n’a pas été écouté : le calage repose sur l’alignement Suno ; les vers 123–142 s (débit doublé) sont à contrôler à l’oreille.

**Plan le plus faible.** Les trois portraits serrés issus de la vignette 02 (21–47 s) se ressemblent ; les vignettes (≈ 500 × 245 px d’origine)
restent douces en plein cadre malgré l’agrandissement.
**Avec plus de moyens.** Régénérer chaque vignette en haute définition (ou tourner de vrais plans) et animer deux gestes : la bobine posée, la main sur l’étoffe.
**Avertissements conservés.** `duplicate_media_discovery_risk` (même image réutilisée sur plusieurs plans, voulu) ; `timeline_track_too_dense` (4 vers par refrain).
