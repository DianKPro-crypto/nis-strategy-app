# CLAUDE.md — Boussole IA

Application HTML autonome (hors ligne, sans dépendance ni API) qui aide Dr Dian Sidibé, stratège international de santé publique, non développeur, à maîtriser l'usage opérationnel et critique de l'IA dans ses missions (vaccination/PEV, aide à la décision, communication stratégique), dans toute l'Afrique.

## Règles de travail
- Tout le contenu et toute la documentation sont en **français** ; l'utilisateur est vouvoyé, l'IA est tutoyée dans les prompts.
- Ne jamais modifier `boussole-ia.html` à la main : modifier `source/contenu/*.js` (contenu) ou `source/modele.html` (interface et moteur), puis reconstruire.
- Le contenu suit **`source/SPEC.md`** (schémas, règles d'écriture, exactitude). Aucun chiffre ni aucune référence inventés ; données d'exemple fictives et signalées comme telles.
- Charte : noir #0B0B0C, or #E3B34C, Playfair Display (titres) + Inter (texte) ; thèmes sombre et clair ; contraste WCAG AA ; mobile sans défilement horizontal.
- L'application n'appelle aucune IA et n'envoie aucune donnée. Ne pas introduire de dépendance réseau (seule exception tolérée : Google Fonts, chargées sans bloquer l'affichage).
- Repères réglementaires : `source/contenu/reglementation_afrique.json`. Toute mise à jour doit être recoupée et signaler les incertitudes (`confiance`).

## Commandes (depuis le dossier `boussole-ia/`)
- Construire (valide le contenu puis génère `boussole-ia.html` et `build/artifact.html`) : `python3 source/construire.py`
- Valider un fichier de contenu : `node source/valider.js source/contenu/prompts.js`
- Test de bout en bout (Playwright, 40 contrôles) : `node source/tests/parcours.test.js`

Avant tout commit : construire, puis lancer le test de bout en bout ; les deux doivent passer sans erreur.
