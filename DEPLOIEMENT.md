# Mettre l’application en ligne (Streamlit Community Cloud) — guide pas à pas

> **Pourquoi pas Netlify ?** Netlify héberge des sites *statiques*. Cette application est un
> serveur Python (Streamlit), elle doit donc être hébergée sur une plateforme qui exécute Python.
> **Streamlit Community Cloud** est gratuit et conçu exactement pour ça.

Vous aurez besoin de **deux comptes gratuits** : un compte **GitHub** et un compte **Streamlit**.
Comptez ~15 minutes la première fois.

---

## Étape 1 — Créer un compte GitHub
1. Allez sur https://github.com → **Sign up** (s’inscrire). C’est gratuit.
2. Confirmez votre adresse e‑mail.

## Étape 2 — Déposer le code sur GitHub (sans ligne de commande)
1. Une fois connecté, cliquez sur **+** (en haut à droite) → **New repository**.
2. Nom : `nis-strategy-app`. Laissez **Private** (privé) si vous voulez le garder confidentiel.
   Cliquez **Create repository**.
3. Sur la page du dépôt vide, cliquez **« uploading an existing file »** (téléverser un fichier existant).
4. Ouvrez le dossier `nis-strategy-app` sur votre Mac, **sélectionnez tout son contenu**
   (sauf le fichier `.env` s’il existe) et **glissez‑déposez** dans la page GitHub.
   - ⚠️ Ne déposez **jamais** le fichier `.env` (il contient votre clé secrète).
   - Le fichier `.gitignore` fourni l’empêche déjà d’être envoyé.
5. En bas, cliquez **Commit changes** (valider).

## Étape 3 — Connecter Streamlit Community Cloud
1. Allez sur https://share.streamlit.io → **Sign in with GitHub** (se connecter avec GitHub),
   et autorisez l’accès.
2. Cliquez **Create app** → **Deploy a public app from GitHub** (ou « from existing repo »).
3. Renseignez :
   - **Repository** : `votre-nom/nis-strategy-app`
   - **Branch** : `main`
   - **Main file path** : `app.py`
4. Cliquez **Deploy**. La première installation prend quelques minutes.

## Étape 4 — Ajouter votre clé API Anthropic (Secrets)
1. Sur la page de votre app Streamlit, cliquez **⋮ → Settings → Secrets**.
2. Collez ceci (remplacez par votre vraie clé) :
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ANTHROPIC_MODEL = "claude-opus-4-8"
   ```
3. **Save**. L’app redémarre automatiquement.
   - Sans clé, l’app fonctionne quand même en **mode manuel** (saisie sans IA).

## Étape 5 — C’est en ligne 🎉
Vous obtenez une adresse du type `https://nis-strategy-app-xxxx.streamlit.app`
que vous pouvez partager avec les équipes pays.

---

## Mettre à jour l’application plus tard
Modifiez/ajoutez les fichiers sur GitHub (bouton **Add file → Upload files**) puis **Commit**.
Streamlit redéploie automatiquement à chaque changement.

## Notes importantes
- **Confidentialité** : sur le cloud, les fichiers téléversés et la base locale `data/nis.db`
  sont **temporaires** (effacés au redémarrage). Utilisez le bouton **💾 Enregistrer** et
  l’**export JSON** pour conserver votre travail.
- **Coûts** : Streamlit Cloud est gratuit ; l’usage de l’IA Claude est facturé par Anthropic
  selon votre clé API.
- Si une bibliothèque manque au démarrage, vérifiez que `requirements.txt` a bien été déposé.

## Alternative serveur (si besoin d’un hébergement privé)
Un `Dockerfile` d’exemple est fourni dans le `README.md` : il fonctionne sur Render,
Hugging Face Spaces, Railway, Fly.io ou tout serveur Docker.
