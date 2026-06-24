# NIS Strategy Builder — Plateforme d’élaboration de la Stratégie Nationale de Vaccination

Transforme l’outil Excel WHO **« All-in-1 SWOT to Activities »** en une application web
interactive qui guide les pays de l’analyse situationnelle jusqu’aux activités opérationnelles,
avec génération assistée par IA, traçabilité des sources, validation humaine et exports
professionnels (Excel, Word, PDF, PowerPoint).

## Fonctionnalités

- Sélection du pays (liste mondiale via `pycountry`) et de la langue (**FR / EN**).
- Téléversement multi-documents : `.docx .xlsx .pptx .pdf .csv .txt` avec extraction de texte,
  tableaux, métadonnées et repères (page / diapositive / feuille).
- Génération IA (Claude) structurée et **anti-hallucination** : chaque élément cite source,
  repère, extrait et niveau de confiance ; les informations manquantes sont marquées
  *« À compléter par l’équipe pays »*.
- Couverture des **7 composantes et 26 sous-composantes** du PEV (fidèle à l’outil OMS).
- Atelier guidé en 11 étapes : Profil → Documents → Vision → FFOM → Causes profondes →
  Obstacles & objectifs SMART → Interventions & priorisation → S&E → Activités →
  Contrôle qualité → Exports.
- Priorisation multicritère (méthode 1, 8 critères, seuils 17-24 / 9-16 / 1-8) et matrice 2×2
  impact × faisabilité (méthode 2).
- Tout le contenu est **éditable** avant export ; le contrôle qualité **bloque l’export**
  tant que les sections clés ne sont pas complètes et validées.
- **Mode hors-ligne** : sans clé API, l’application fonctionne en saisie 100 % manuelle.

## Guides utilisateur (équipes pays)

- 🇫🇷 **[GUIDE_UTILISATEUR_FR.md](GUIDE_UTILISATEUR_FR.md)** — guide pas à pas en français.
- 🇬🇧 **[USER_GUIDE_EN.md](USER_GUIDE_EN.md)** — step-by-step guide in English.

## Installation locale

```bash
cd nis-strategy-app
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # puis collez votre clé ANTHROPIC_API_KEY dans .env
streamlit run app.py
```

L’application s’ouvre sur http://localhost:8501.
Sans clé API, elle démarre quand même en **mode manuel**.

### Tests

```bash
pip install pytest
pytest -q
```

## Déploiement en ligne

> 📘 Guide détaillé pas à pas (pour non-techniciens) : **[DEPLOIEMENT.md](DEPLOIEMENT.md)**.
> ⚠️ Netlify ne convient pas (site statique uniquement) — cette app est un serveur Python.

**Streamlit Community Cloud (le plus simple)**
1. Poussez ce dossier sur un dépôt GitHub.
2. Sur https://share.streamlit.io, « New app » → sélectionnez le dépôt et `app.py`.
3. Dans *Settings → Secrets*, ajoutez `ANTHROPIC_API_KEY="..."` (jamais dans le code).

**Docker / VM**
```bash
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=... \
  $(docker build -q .)          # voir Dockerfile d’exemple ci-dessous
```
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit","run","app.py","--server.address=0.0.0.0","--server.port=8501"]
```

## Architecture

```
nis-strategy-app/
├── app.py                  # Application Streamlit (11 pages / étapes)
├── config/                 # settings.py (env/.env), countries.py
├── core/                   # models.py, epi_components.py, document_loader.py,
│                           # ai_engine.py, validators.py, prioritization.py,
│                           # translations.py, storage.py (SQLite)
├── exports/                # excel/word/pdf/ppt_exporter.py
├── templates/              # prompts.py (prompt central Claude + schémas JSON)
├── data/                   # uploads / outputs / temp
└── tests/                  # test_models.py, test_exports.py
```

## Sécurité & confidentialité

- Clé API uniquement dans `.env` / *Secrets* ; jamais affichée dans l’UI.
- Types de fichiers restreints, taille limitée (`MAX_FILE_MB`), extraction défensive.
- Documents traités localement et temporairement ; suppression possible depuis l’UI.
- Avertissement sur les documents confidentiels ; mode hors-ligne disponible.

## Limites connues du MVP

- Stockage local SQLite mono-utilisateur, pas d’authentification ni de rôles.
- L’état vit dans la session Streamlit ; sauvegardez régulièrement (bouton 💾).
- Fidélité visuelle de l’export Excel proche mais non identique au gabarit OMS d’origine
  (logique et structure préservées).
- La qualité IA dépend des documents fournis et de la fenêtre de contexte (texte tronqué
  par document). Les chiffres doivent être revérifiés par l’équipe pays.
- Pas d’OCR pour PDF scannés (texte image non extrait).

## Recommandations pour une version « production »

- **Backend** FastAPI + **frontend** React ; **PostgreSQL** ; **stockage objet** chiffré (S3).
- Authentification (OIDC/SSO), **RBAC** (rédacteur / validateur / administrateur), **audit trail**.
- Pipeline d’ingestion asynchrone (file d’attente), OCR (Tesseract) pour PDF scannés,
  recherche sémantique (embeddings) pour citer précisément les passages sources.
- Génération IA par lots avec mise en cache des invites et journalisation des coûts.
- Versionnage des stratégies, collaboration multi-utilisateurs, et intégration **NIS.COST**.
- Hébergement conforme (données de santé), sauvegardes, et observabilité.
```
