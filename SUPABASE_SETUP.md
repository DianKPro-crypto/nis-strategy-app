# Stockage durable — Supabase (guide pas à pas)

Objectif : sauvegarder vos projets **en ligne** pour qu'ils **survivent aux redémarrages** de l'app
(et que chaque pays retrouve son travail). Gratuit. ~10 minutes, une seule fois.

> Sans cette configuration, l'app fonctionne quand même (stockage local **temporaire**). Avec elle,
> les projets sont **sauvegardés automatiquement** après chaque génération IA.

---

## Étape 1 — Créer un compte et un projet Supabase
1. Allez sur **https://supabase.com** → **Start your project** → connectez-vous (avec GitHub, c'est plus simple).
2. Cliquez **New project**.
   - **Name** : `nis-strategy`
   - **Database Password** : choisissez-en un (notez-le, mais l'app n'en a pas besoin).
   - **Region** : la plus proche (ex. *Europe (Paris/Frankfurt)*).
3. Cliquez **Create new project** et patientez ~2 minutes (le temps que la base se crée).

## Étape 2 — Créer la table (copier-coller)
1. Dans le menu de gauche, cliquez **SQL Editor** → **New query**.
2. Collez ceci, puis cliquez **Run** :
   ```sql
   create table if not exists nis_projects (
       name text primary key,
       country text,
       language text,
       updated_at timestamptz default now(),
       payload jsonb
   );
   alter table nis_projects enable row level security;
   create policy "nis_all" on nis_projects for all using (true) with check (true);
   ```
3. Vous devez voir **« Success. No rows returned »**.

## Étape 3 — Récupérer l'URL et la clé
1. Menu de gauche → **Project Settings** (l'icône ⚙️) → **API**.
2. Notez deux valeurs :
   - **Project URL** : `https://xxxxxxxx.supabase.co`
   - **Project API keys → `anon` `public`** : une longue clé qui commence par `eyJ...`

## Étape 4 — Ajouter les secrets dans Streamlit
1. Sur **https://share.streamlit.io** → votre app → **⋮ → Settings → Secrets**.
2. Ajoutez (en plus de votre clé Anthropic) :
   ```toml
   SUPABASE_URL = "https://xxxxxxxx.supabase.co"
   SUPABASE_KEY = "eyJ...la clé anon public..."
   ```
3. **Save**. L'app redémarre.

## Étape 5 — Vérifier
- Dans la barre latérale, vous verrez **« ☁️ Stockage cloud (durable) »**.
- Donnez un **Nom du projet** (ex. `Djibouti-2027`), travaillez, générez : c'est **sauvegardé automatiquement**.
- Après un redémarrage : choisissez votre projet dans **« Projets enregistrés »** → **Ouvrir ce projet**.

---

## Notes
- **Confidentialité** : la clé `anon` + une politique RLS permissive rendent la table accessible à qui
  possède l'URL et la clé. C'est suffisant pour un MVP partagé. Pour une vraie confidentialité par pays,
  ajoutez l'authentification Supabase (version production).
- **Sauvegarde manuelle** reste disponible (bouton 💾) ; l'export **.json** (étape 10) demeure une copie hors-ligne.
- Le plan gratuit Supabase suffit largement (la table ne stocke que du texte JSON).
