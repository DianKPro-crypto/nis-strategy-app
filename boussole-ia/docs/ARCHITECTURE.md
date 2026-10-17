# Architecture de Boussole IA

## 1. Intention

Profil visé : professionnel de santé publique, **utilisateur expert de l'IA** (pas bâtisseur de modèles), qui apprend **juste-à-temps**, en préparant des missions réelles.

Conséquence de conception : on n'entre pas dans l'application par un cours, mais par une **tâche réelle** (Mode Mission). Les leçons arrivent au moment où elles servent.

Les trois priorités forment une chaîne de valeur unique : **données → décision → communication**.

## 2. Écrans

| Écran | Rôle | Contenu clé |
|---|---|---|
| Accueil | Orienter en dix secondes | 3 portes d'entrée (tâche, progresser, bibliothèque), compétences, repères chiffrés, 5 règles d'or |
| Mode Mission | Cœur de l'application | Cadrer → Protéger → Produire → Vérifier → Apprendre |
| Bibliothèque | Prompts prêts à l'emploi | 15 fiches filtrables : modèle, annotations CADRE, adaptation, pièges, vérifications, outil |
| Parcours | Apprentissage court | Modules M0 à M6, micro-leçons, quiz, exercices |
| Checklist éthique | Avant tout usage | Checklist en 12 questions, matrice outils × données, repères 54 pays, cadres de référence |
| Ma progression | Tableau de bord | Compétences, journal des missions, export et import |
| Aide-mémoire | Référence rapide | Règles d'or, CADRE, VÉRIF, niveaux N0 à N3, relances, formules PEV |

Sur ordinateur, la navigation passe par un rail latéral. Sur mobile, elle passe par une barre d'onglets en bas de l'écran ; la checklist et l'aide-mémoire sont accessibles depuis la barre du haut.

## 3. Le Mode Mission

```
① CADRER     Choix parmi 15 tâches (filtre par domaine, recherche)
② PROTÉGER   Checklist en 12 questions + pays (facultatif) → feu vert / orange / rouge
             Le feu rouge bloque l'accès à l'étape suivante.
③ PRODUIRE   Formulaire → prompt assemblé en direct → copie → lien vers l'outil
             Annotations CADRE, conseils d'adaptation, 8 relances utiles
④ VÉRIFIER   Grille VÉRIF (5 critères, chacun : conforme / à corriger / sans objet)
             Contrôles propres à la tâche, pièges fréquents, journal de mission
⑤ APPRENDRE  Micro-leçon liée à la tâche
```

La mission en cours est enregistrée : on peut quitter l'application et reprendre plus tard.

## 4. Méthodes maison

- **CADRE** (écrire un prompt) : Contexte · Action · Données · Règles · Exemple de sortie.
- **VÉRIF** (contrôler une réponse) : Véracité · Équité · Raisonnement · Intégrité des données · Faisabilité.
- **Sensibilité des données** : N0 Public · N1 Interne · N2 Confidentiel · N3 Personnel.
- **Matrice outils × données** : 4 types d'outils (institutionnel, personnel payant, gratuit, non vérifié) croisés avec les niveaux N0 à N3. Chaque case donne un statut (autorisé, sous conditions, interdit) et un conseil.

## 5. Modèle de progression

Cinq compétences : Fondamentaux, Art du prompt, Cas d'usage, Évaluation critique, Éthique et réglementation.

| Action | Points |
|---|---|
| Micro-leçon lue | +1 sur la compétence de la leçon |
| Quiz ≥ 80 % (50 à 79 %) | +3 (+1) sur la compétence du module |
| Exercice réussi à ≥ 66 % (sinon) | +2 (+1) |
| Mission enregistrée | +1 Cas d'usage, +1 Art du prompt, +1 Éthique, +1 Évaluation critique si VÉRIF complète |
| Checklist autonome enregistrée | +1 Éthique (5 au maximum) |

Niveaux : **Découverte** (0 à 4 points), **Pratique** (5 à 9), **Maîtrise** (10 et plus). La compétence « Cas d'usage » ne progresse que par les missions : environ 10 missions mènent à la Maîtrise.

## 6. Choix techniques

| Choix | Raison |
|---|---|
| Un seul fichier HTML, sans bibliothèque ni framework | Ouverture par double-clic, fonctionnement hors ligne, aucune dépendance qui vieillit |
| Contenu séparé du moteur (`source/contenu/`) | Enrichir l'application sans toucher au code de l'interface |
| Validation automatique du contenu (`valider.js`) | Éviter qu'un prompt ou une leçon mal formé ne casse l'application |
| Progression dans le stockage local du navigateur, avec export et import JSON | Confidentialité totale : rien ne quitte l'appareil |
| Aucune IA appelée par l'application | Pas de coût, pas de clé d'API, pas de fuite de données ; outil indépendant du fournisseur d'IA |
| Identité Dian K Pro : logo intégré (navigation, couverture, signature, icône d'onglet), châssis noir et or, Playfair Display, Inter et Cinzel pour la signature ; thèmes sombre et clair | Plateforme premium et cohérente avec la marque ; lisibilité, contraste conforme WCAG AA |
| Logo intégré en masque alpha (`source/marque/`) | Une seule image, colorée par le thème : or vif sur noir, or foncé sur fond clair ; fichier autonome, sans téléchargement externe |

### Données enregistrées localement (clé `boussole-ia/v1`)

```json
{ "v": 1, "lecons": {"m0-quoi": "date"}, "quiz": {"m0": 0.8}, "exercices": {"err-abandon": {"score": 1}},
  "missions": [{ "promptId": "...", "date": "...", "verdict": "attention", "verif": {"V": "ok"}, "gain": 60, "note": "..." }],
  "verifs": [], "favoris": [], "prefs": {"pays": "SN"}, "brouillon": null }
```

## 7. Qualité

- `python3 source/construire.py` valide le contenu, puis construit `boussole-ia.html`.
- `node source/tests/parcours.test.js` lance 44 contrôles automatisés :
  - mission complète, feu rouge bloquant, copie du prompt ;
  - quiz, exercices, favoris, recherche ;
  - 54 pays affichés, export et import, persistance après rechargement ;
  - absence de défilement horizontal sur mobile, absence d'erreur JavaScript.
