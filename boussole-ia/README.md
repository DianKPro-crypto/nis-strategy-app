# Boussole IA · Santé publique

**Préparer, protéger, produire et vérifier chaque usage de l'IA dans vos missions de santé publique, de la donnée à la décision.**

Boussole IA est une application autonome qui fait passer d'un usage occasionnel de l'IA à une maîtrise opérationnelle et critique. Elle ne remplace pas Claude, ChatGPT ou Copilot : elle structure le travail **autour** de ces outils, mission après mission.

> Une création **Dian K. Pro** · Public Health & Digital Strategist · *Designed for Those Who Cannot Fail*
>
> Version 0.1.0 (MVP) · contenu à jour en octobre 2026

---

## Démarrer en deux minutes

### Sur Mac (usage principal, entièrement hors ligne)
1. Téléchargez le fichier **`boussole-ia.html`**. Sur GitHub : dépôt `nis-strategy-app`, dossier `boussole-ia/`, ouvrez le fichier puis cliquez sur l'icône « Download raw file ».
2. Rangez-le dans un dossier stable, par exemple `Documents/Boussole IA/`.
3. Double-cliquez dessus : il s'ouvre dans Safari ou Chrome. Aucune installation, aucun compte, aucune connexion requise.
4. Ajoutez la page aux favoris de votre navigateur pour la retrouver en un clic.

> **Important.** Ouvrez toujours le fichier avec **le même navigateur** et depuis **le même emplacement** : c'est là que votre progression est enregistrée.

### Sur iPhone ou iPad
Un fichier HTML ouvert depuis l'app Fichiers ne fonctionne pas correctement sur iOS. Utilisez le **lien privé en ligne** fourni avec la livraison : c'est la même application.
- Dans Safari : bouton Partager, puis « Sur l'écran d'accueil », pour l'ouvrir comme une application.
- La progression du téléphone est distincte de celle du Mac. Pour transférer : **Ma progression → Exporter**, puis **Importer** sur l'autre appareil.

---

## Le parcours recommandé (juste-à-temps)

| Quand | Quoi | Durée |
|---|---|---|
| **Jour 1** | Accueil → « Je progresse » : Démarrage express (3 micro-leçons) | 15 min |
| **Jour 1** | Parcours → Module 3 : une mission d'entraînement avec des données fictives | 10 min |
| **À chaque tâche réelle** | Accueil → « J'ai une tâche maintenant » (Mode Mission) | 10 min de méthode |
| **Toutes les deux semaines** | Un module court, son quiz et un exercice « Trouvez l'erreur » | 20 min |

Le **Mode Mission** est le cœur de l'application. Il se déroule en cinq temps :

1. **Cadrer** : choisir la tâche parmi 15 tâches de santé publique.
2. **Protéger** : checklist éthique de 12 questions. Elle aboutit à un feu vert, orange ou rouge, et peut afficher la loi nationale du pays concerné.
3. **Produire** : remplir le formulaire, copier le prompt assemblé selon la méthode CADRE, le coller dans votre outil d'IA.
4. **Vérifier** : appliquer la grille VÉRIF à la réponse, puis noter dans le journal le temps gagné et la leçon retenue.
5. **Apprendre** : lire la micro-leçon liée à la tâche.

---

## Ce que contient la version 0.1

| Élément | Contenu |
|---|---|
| **Mode Mission** | Parcours complet en 5 étapes. Le feu rouge bloque la suite tant que la situation n'est pas corrigée. |
| **Bibliothèque** | 15 prompts annotés : 5 sur les données PEV, 5 sur l'aide à la décision, 5 sur la communication stratégique. Chacun indique pourquoi il fonctionne, comment l'adapter, les pièges à éviter, les vérifications à faire et l'outil conseillé. |
| **Parcours** | 17 micro-leçons réparties en 5 modules (M0, M1, M2, M4, M5), 5 quiz (29 questions), 2 exercices de réécriture et 3 exercices « Trouvez l'erreur ». |
| **Pratique guidée (M3)** | Les 15 tâches en mode entraînement, pré-remplies avec des données fictives. |
| **Éthique** | Checklist autonome et matrice outils × sensibilité des données (N0 à N3). |
| **Repères réglementaires** | Les lois de protection des données des 54 pays africains, les cadres de l'UA, de la CEDEAO, de la SADC, de l'OMS et de l'UNESCO, le RGPD et le calendrier de l'AI Act. |
| **Progression** | 5 compétences sur 3 niveaux, journal des missions, export et import. |
| **Aide-mémoire** | L'essentiel sur une page : règles d'or, CADRE, VÉRIF, niveaux de données, relances, formules. |

Le module 6, « Déployer l'IA dans une équipe », est prévu pour la version 1.0.

---

## Vos données

- **Rien n'est envoyé nulle part.** L'application n'appelle aucune IA et aucune API. Votre progression reste dans le navigateur de votre appareil.
- Seule exception : lorsque vous êtes connecté, les polices de la charte (Playfair Display, Inter) sont chargées depuis Google Fonts. Hors ligne, des polices système les remplacent.
- Les boutons « Claude », « ChatGPT », « Copilot » et « Gemini » ouvrent simplement ces sites dans un nouvel onglet.
- **Sauvegarde** : vider les données du navigateur efface la progression. Exportez-la de temps en temps depuis **Ma progression**.

---

## Limites à connaître

- **La checklist est une règle de prudence.** Elle ne remplace ni la politique d'usage de votre organisation, ni l'avis de votre délégué à la protection des données ou d'un juriste.
- **Les repères réglementaires** ont été établis en octobre 2026 à partir de sources secondaires recoupées : DLA Piper, CIPESA, ALT Advisory, communiqués officiels. Les pays signalés « À confirmer » et les dates récentes doivent être vérifiés auprès de l'autorité nationale ou sur EUR-Lex avant toute citation officielle.
- **Les gains de temps** affichés sont des repères indicatifs. Le journal mesure vos propres gains.
- **Toutes les données d'exemple sont fictives.** Les districts A, B, C et les pays « Mabandé » ou « Kouri » sont inventés.
- La **détection CADRE** des exercices de réécriture repose sur des mots-clés : elle est indicative.

---

## Faire évoluer l'application

Voir **[docs/FAIRE-EVOLUER.md](docs/FAIRE-EVOLUER.md)**. Le plus simple : ouvrir une session Claude Code sur le dépôt `nis-strategy-app` et demander l'évolution souhaitée de Boussole IA. Des demandes prêtes à copier y figurent.

L'architecture fonctionnelle et technique est décrite dans **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

## Structure du dossier

Boussole IA est rangée dans le dossier `boussole-ia/` du dépôt `nis-strategy-app`, indépendamment de l'application Streamlit qui l'héberge.

```
boussole-ia/
  boussole-ia.html          L'application : le seul fichier à ouvrir
  README.md                 Ce guide
  docs/
    ARCHITECTURE.md         Écrans, parcours, modèle de progression, choix techniques
    FAIRE-EVOLUER.md        Comment enrichir et faire évoluer l'application
  source/                   Fichiers de travail (modifiés par Claude lors des évolutions)
    contenu/                Prompts, leçons, quiz, exercices, checklist, repères pays
    modele.html             Interface et moteur de l'application
    marque/                 Logo Dian K Pro (original et déclinaisons numériques)
    construire.py           Assemble boussole-ia.html à partir du contenu
    valider.js              Contrôle la cohérence du contenu
    tests/                  Test de bout en bout dans un navigateur
    SPEC.md                 Règles de rédaction du contenu
```
