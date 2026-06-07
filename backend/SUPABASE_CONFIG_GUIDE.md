# 🚀 Configuration Supabase — Guide Complet

## Objectif
Ce guide explique comment configurer le backend avec Supabase PostgreSQL et les variables d'environnement attendues par `config.py`.

## 1. Récupérer vos identifiants Supabase

1. Ouvrez votre projet sur le dashboard Supabase.
2. Allez dans **Settings → Database → Connection strings**.
3. Copiez la connection string PostgreSQL :

```text
postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

4. Si vous utilisez le client Supabase côté frontend ou les fonctions Realtime, récupérez aussi :
   - **SUPABASE_URL**
   - **SUPABASE_ANON_KEY**
   - **SUPABASE_SERVICE_KEY**
   depuis **Settings → API**.

## 2. Mettre à jour `.env`

Copiez `.env.example` vers `.env` et remplacez les valeurs par vos identifiants :

```env
DATABASE_URL=postgresql://postgres:your_password@db.your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
ENV=development
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Notes importantes
- `DATABASE_URL` est la variable utilisée par `database.py` pour créer la connexion SQLAlchemy.
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` et `SUPABASE_SERVICE_KEY` sont optionnels côté backend, mais utiles si vous utilisez des services Supabase additionnels.
- `SUPABASE_SERVICE_KEY` est un secret : **ne le commitez jamais**.
- `SECRET_KEY` doit être une chaîne forte et unique en production.

## 3. Tester la connexion à la base de données

Exécutez :

```bash
python -c "from database import test_connection; test_connection()"
```

Si la connexion fonctionne, vous verrez :

```text
✓ Database connection successful
```

## 4. Initialiser la base de données

Ensuite :

```bash
python init_db.py
```

Cela :
- teste la connexion
- crée les tables SQLAlchemy
- initialise les données de base si le script le fait

## 5. Sécurité et bonnes pratiques

- `.env` doit rester local et ne doit pas être poussé dans Git.
- `.gitignore` doit contenir au minimum :

```text
.env
.env.local
.env.*.local
```

- Utilisez `.env.example` comme modèle public pour les autres développeurs.
- Renouvelez vos clés Supabase si elles ont été exposées.

## 6. Rappels Supabase vs PostgreSQL local

| Aspect | Supabase | PostgreSQL local |
|--------|----------|------------------|
| Installation | Aucun serveur local à installer | Installation + configuration | 
| Accès à distance | ✅ Oui | ❌ Non par défaut |
| Backups | ✅ Automatiques | ❌ Manuel |
| Realtime | ✅ Inclus | ❌ À configurer |
| Auth intégrée | ✅ Oui | ❌ Non |
| Data API | ✅ Inclus | ❌ À implémenter |
| Coût | 💰 Freemium | 💰 Gratuit |

Supabase est recommandé pour ce projet, car le backend FastAPI peut se connecter directement via `DATABASE_URL`.

## 7. Commandes utiles

```bash
cp .env.example .env
python -c "from database import test_connection; test_connection()"
python init_db.py
uvicorn main:app --reload
```

## 8. Ressources

- Supabase Connection strings : https://supabase.com/docs/guides/database/connecting-to-postgres
- Supabase API : https://supabase.com/docs/guides/api
- Supabase Auth & RLS : https://supabase.com/docs/guides/auth
