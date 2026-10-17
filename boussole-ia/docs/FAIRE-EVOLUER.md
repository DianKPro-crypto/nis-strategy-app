# Faire évoluer Boussole IA

L'application sépare le **contenu** (prompts, leçons, quiz, checklist, repères pays) du **moteur** (affichage, navigation, progression). Enrichir l'application revient presque toujours à modifier un fichier de `source/contenu/`, puis à reconstruire `boussole-ia.html`.

## Option 1 (recommandée) : demander à Claude

Ouvrez une session Claude Code sur le dépôt `nis-strategy-app` (claude.ai/code), dont le dossier `boussole-ia/` contient l'application,, puis copiez l'une des demandes ci-dessous en l'adaptant. Claude modifie le contenu, reconstruit le fichier, lance les tests et pousse la nouvelle version.

**Ajouter un prompt à la bibliothèque**
> Ajoute à la bibliothèque un prompt pour [tâche, ex. : préparer le rapport annuel conjoint OMS/UNICEF (JRF)], domaine [données / décision / communication], en respectant source/SPEC.md. Inspire-toi de ce prompt que j'utilise déjà : [coller votre prompt]. Reconstruis, teste et pousse.

**Transformer un de vos prompts éprouvés en fiche**
> Voici un prompt qui a très bien fonctionné lors de ma dernière mission : [coller]. Transforme-le en fiche de bibliothèque complète (champs, annotations CADRE, pièges, vérifications), selon source/SPEC.md.

**Ajouter une micro-leçon ou un exercice « Trouvez l'erreur »**
> Ajoute au module [n] une micro-leçon sur [sujet], et un exercice « Trouvez l'erreur » à partir de cette réponse d'IA réellement obtenue : [coller la réponse, anonymisée]. Les erreurs que j'y ai repérées sont : [liste].

**Mettre à jour les repères réglementaires** (à faire tous les six mois)
> Mets à jour source/contenu/reglementation_afrique.json : vérifie les lois de protection des données des 54 pays africains et le calendrier de l'AI Act. Signale-moi chaque changement avant de pousser.

**Mettre à jour la loi d'un pays**
> Le [pays] a adopté [loi n°…] le [date] ; l'autorité est [nom]. Mets à jour la fiche du pays.

## Option 2 : modifier vous-même un texte

Pour corriger une phrase ou ajuster un exemple :
1. Sur GitHub, ouvrez le fichier concerné dans `boussole-ia/source/contenu/`, puis cliquez sur le crayon (« Edit »).
2. Modifiez uniquement le texte situé entre guillemets ou entre accents graves (`` ` ``), sans toucher à la ponctuation du code autour.
3. Enregistrez avec « Commit changes ».
4. Demandez ensuite à Claude : « Reconstruis boussole-ia.html et lance les tests. »

Ne modifiez pas `boussole-ia.html` directement : il est régénéré à chaque construction.

## Feuille de route proposée

### Version 1.0 : consolider (4 à 6 semaines d'usage réel d'abord)
| Priorité | Évolution | Bénéfice |
|---|---|---|
| 1 | **Mes prompts** : ajouter, modifier et classer ses propres prompts depuis l'application, sans code | La bibliothèque devient la vôtre |
| 2 | **Domaine « Synthèse de littérature »** : 5 prompts, tableau d'extraction, vérification des références | Couvre la 4e priorité |
| 3 | **Analyseur de prompt CADRE** : collez un prompt, obtenez un diagnostic et des suggestions (règles transparentes, hors ligne) | Progression accélérée sur l'art du prompt |
| 4 | **Module 6 « Déployer l'IA dans une équipe »** : politique d'usage, gouvernance, formation en 3 sessions | Démultiplication auprès des équipes pays |
| 5 | **Journal enrichi** : export du journal en tableau (CSV) pour un bilan trimestriel | Mesure de l'impact |

### Version 2.0 : élargir
- **Hors ligne sur smartphone** : publication web avec mise en cache, pour un usage sans réseau sur iPhone.
- **Version anglaise** (interface et contenu) pour les équipes anglophones.
- **Synchronisation** de la progression entre appareils.
- **Kit équipe** : version allégée à diffuser à une équipe pays, avec sa propre bibliothèque.
- **Usages avancés** : agents, projets Claude, NotebookLM appliqués aux revues de programme.

## Indicateurs pour piloter les évolutions

Revoyez tous les trimestres, depuis **Ma progression** :
- le nombre de missions et le temps gagné cumulé ;
- la part des missions « utilisées après corrections » : si elle est élevée, les prompts concernés sont à améliorer ;
- les critères VÉRIF le plus souvent « à corriger » : ils indiquent où l'IA vous fait défaut et quelles leçons ajouter ;
- les leçons retenues dans le journal : c'est la matière première de nouveaux prompts.
