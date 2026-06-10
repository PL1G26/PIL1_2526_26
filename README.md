# IFRI MentorLink — README Technique

> **Projet intégrateur PIL1 — 2025-2026 (PIL1_2526_26)**
> Plateforme de mentorat académique pour les étudiants de l'IFRI

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Stack technologique](#2-stack-technologique)
3. [Architecture du projet](#3-architecture-du-projet)
4. [Base de données](#4-base-de-données)
5. [Backend — API REST](#5-backend--api-rest)
6. [Algorithme de matching](#6-algorithme-de-matching)
7. [Frontend — Vue.js](#7-frontend--vuejs)
8. [Installation & Démarrage](#8-installation--démarrage)
9. [Variables d'environnement](#9-variables-denvironnement)
10. [Tests](#10-tests)
11. [Équipe](#11-équipe)

---

## 1. Vue d'ensemble

**IFRI MentorLink** est une application web de mise en relation entre étudiants-mentors et étudiants-mentorés au sein de l'IFRI (Institut de Formation et de Recherche en Informatique). Elle permet de :

- **Publier des offres et demandes de mentorat** par compétence
- **Être mis en relation automatiquement** via un algorithme de scoring basé sur les compétences, la filière, et les disponibilités
- **Accepter ou refuser des correspondances** (matches)
- **Échanger des messages** dans des conversations liées aux matches acceptés
- **Gérer son profil** : compétences (points forts / lacunes), disponibilités hebdomadaires, bio

---

## 2. Stack technologique

### Backend

| Composant | Technologie | Version |
|-----------|------------|---------|
| Framework API | **FastAPI** | ≥ 0.110.0 |
| Serveur ASGI | **Uvicorn** | ≥ 0.23.0 |
| ORM | **SQLAlchemy** | ≥ 2.0.30 |
| Connecteur PostgreSQL | **psycopg3 (binary)** | ≥ 3.2 |
| Authentification | **JWT (python-jose)** | ≥ 3.3.0 |
| Hachage de mots de passe | **passlib + bcrypt** | ≥ 1.7.0 / 4.0.0 |
| Validation des données | **Pydantic v2** | ≥ 2.6.0 |
| Configuration | **pydantic-settings** | ≥ 2.0.0 |
| Variables d'env | **python-dotenv** | ≥ 1.0.0 |
| Tests | **pytest + pytest-asyncio** | ≥ 7.4.0 / 0.21.0 |

### Frontend

| Composant | Technologie | Version |
|-----------|------------|---------|
| Framework JS | **Vue.js 3** | ^3.5.34 |
| Routing | **Vue Router 4** | ^4.6.4 |
| Bundler | **Vite** | ^8.0.12 |
| Client HTTP | **Axios** | ^1.17.0 |
| Plugin Vite | **@vitejs/plugin-vue** | ^6.0.6 |

### Base de données

- **PostgreSQL** (compatible **Supabase**)

---

## 3. Architecture du projet

```
PIL1_2526_26/
│
├── backend/                    # API REST FastAPI
│   ├── main.py                 # Point d'entrée, configuration CORS, routeurs
│   ├── config.py               # Paramètres via pydantic-settings (.env)
│   ├── database.py             # Moteur SQLAlchemy, session factory, get_db()
│   ├── schema.sql              # Script SQL de création de la BDD
│   ├── init_db.py              # Script d'initialisation de la BDD
│   ├── requirements.txt        # Dépendances Python
│   ├── .env / .env.example     # Variables d'environnement
│   │
│   ├── routers/                # Couche contrôleur (endpoints FastAPI)
│   │   ├── auth.py             # POST /register, /login, GET /me
│   │   ├── users.py            # GET/PUT /users/me, skills, availabilities
│   │   ├── posts.py            # CRUD /posts
│   │   ├── matches.py          # GET /matches, PUT /matches/{id}/accept|reject
│   │   ├── chat.py             # GET/POST /conversations, /messages
│   │   └── skills.py           # GET /skills
│   │
│   ├── models/                 # Modèles SQLAlchemy (mapping ORM)
│   │   ├── user.py             # User, UserSkill, UserAvailability
│   │   ├── mentorship_post.py  # MentorshipPost, PostAvailability
│   │   ├── match.py            # Match
│   │   ├── conversation.py     # Conversation
│   │   ├── message.py          # Message
│   │   └── skill.py            # Skill
│   │
│   ├── schemas/                # Schémas Pydantic (validation I/O)
│   │   ├── auth_schema.py      # LoginRequest, RegisterRequest, TokenResponse
│   │   ├── user_schema.py      # UserResponse, UpdateProfileRequest
│   │   ├── post_schema.py      # PostCreate, PostResponse
│   │   ├── match_schema.py     # MatchResponse, AcceptMatchResponse
│   │   └── message_schema.py   # MessageCreate, ConversationResponse
│   │
│   ├── services/               # Couche service (logique métier)
│   │   ├── auth_service.py     # JWT, hachage password
│   │   ├── matching_service.py # Algorithme de scoring mentor/mentoré
│   │   └── chat_service.py     # Logique conversations & messages
│   │
│   └── test/                   # Suite de tests pytest
│       ├── test_models.py
│       ├── test_routes.py
│       ├── test_schemas.py
│       └── test_services.py
│
├── frontend/                   # SPA Vue.js 3 + Vite
│   ├── index.html              # Point d'entrée HTML
│   ├── vite.config.js          # Configuration Vite
│   ├── package.json            # Dépendances Node.js
│   │
│   └── src/
│       ├── main.js             # Bootstrap Vue + Router
│       ├── App.vue             # Composant racine
│       ├── style.css           # Styles globaux
│       │
│       ├── router/
│       │   └── index.js        # Vue Router (routes + guards d'auth)
│       │
│       ├── store/
│       │   └── index.js        # State management (reactive store + localStorage)
│       │
│       ├── services/
│       │   └── api.js          # Instance Axios configurée
│       │
│       ├── assets/
│       │   └── main.css        # Styles spécifiques aux composants
│       │
│       └── views/
│           ├── LandingView.vue   # Page d'accueil publique
│           ├── LoginView.vue     # Formulaire de connexion
│           ├── RegisterView.vue  # Formulaire d'inscription
│           └── DashboardView.vue # Dashboard principal (multi-onglets)
│
└── docs/                       # Documentation du projet
```

---

## 4. Base de données

### Schéma entité-relation (simplifié)

```
users ──────────< user_skills >────────── skills
  │                                          │
  ├─────────< user_availabilities            │
  │                                          │
  ├─────────< mentorship_posts >─────────────┘
  │               │
  │               └──< post_availabilities
  │
  ├─────────< matches (mentor_id / mentee_id)
                  │
                  └──> conversations
                            │
                            └──< messages
```

### Tables principales

#### `users`
| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | SERIAL | PK |
| `first_name` | VARCHAR(50) | NOT NULL |
| `last_name` | VARCHAR(50) | NOT NULL |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL |
| `phone_number` | VARCHAR(20) | UNIQUE, NOT NULL |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `profile_photo` | VARCHAR(255) | nullable (URL) |
| `field_of_study` | VARCHAR(50) | `IA`, `IM`, `GL`, `SE&IoT`, `SI` |
| `level` | VARCHAR(20) | `L1`, `L2`, `L3`, `M1`, `M2` |
| `bio` | TEXT | nullable |

#### `user_skills`
Relation many-to-many entre `users` et `skills` avec attribut `proficiency` :
- `'strong'` → point fort (peut enseigner)
- `'weak'` → lacune (cherche de l'aide)

#### `mentorship_posts`
| Colonne | Type | Valeurs |
|---------|------|---------|
| `type` | VARCHAR(10) | `offer` / `request` |
| `mode` | VARCHAR(10) | `online` / `offline` / `both` |
| `is_active` | BOOLEAN | permet l'archivage sans suppression |

#### `matches`
| Colonne | Type | Description |
|---------|------|-------------|
| `mentor_id` | INT → users | Toujours `mentor_id > mentee_id` (contrainte DB) |
| `mentee_id` | INT → users | — |
| `score` | DECIMAL(5,2) | Score de compatibilité (0–100) |
| `status` | VARCHAR(20) | `pending` / `accepted` / `rejected` |

#### `conversations` & `messages`
- Une conversation est liée à **exactement un match accepté** (`UNIQUE` sur `match_id`)
- Les messages contiennent un flag `is_read` pour le compteur de non-lus

### Indexes de performance
```sql
idx_user_skills_user, idx_user_skills_skill
idx_avail_user
idx_posts_user, idx_posts_skill, idx_posts_active
idx_matches_mentor, idx_matches_mentee, idx_matches_status
idx_messages_conv, idx_messages_sender, idx_messages_created
```

---

## 5. Backend — API REST

### Configuration générale

- **Base URL** : `http://localhost:8000`
- **Documentation interactive** : `http://localhost:8000/docs` (Swagger UI, dev only)
- **Documentation alternative** : `http://localhost:8000/redoc` (dev only)
- **Authentification** : JWT Bearer Token (`Authorization: Bearer <token>`)
- **CORS** : configuré via `ALLOWED_ORIGINS` dans `.env`

### Endpoints

#### Auth — `/api/auth`

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `POST` | `/api/auth/register` | ✗ | Inscription + retourne token JWT |
| `POST` | `/api/auth/login` | ✗ | Connexion + retourne token JWT |
| `POST` | `/api/auth/reset-password` | ✗ | Demande de reset mot de passe |
| `GET` | `/api/auth/me` | ✓ | Profil de l'utilisateur connecté |

**Payload `/register`** :
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean@example.com",
  "phone_number": "+22901XXXXXXXX",
  "password": "motdepasse",
  "field_of_study": "GL",
  "level": "L3",
  "bio": "Passionné de développement"
}
```

> **Validation phone** : format strict `+22901XXXXXXXX` (8 chiffres après `+22901`)

**Réponse token** :
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": 1, "first_name": "Jean", "last_name": "Dupont", ... }
}
```

---

#### Users — `/api/users`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/users/me` | Profil complet (skills, availabilities) |
| `PUT` | `/api/users/me` | Mise à jour du profil |
| `GET` | `/api/users/{id}` | Profil public d'un autre utilisateur |
| `POST` | `/api/users/me/skills` | Ajouter/mettre à jour une compétence |
| `DELETE` | `/api/users/me/skills/{skill_id}` | Supprimer une compétence |
| `POST` | `/api/users/me/availabilities` | Ajouter un créneau de disponibilité |
| `DELETE` | `/api/users/me/availabilities/{id}` | Supprimer un créneau |

---

#### Posts — `/api/posts`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/posts/` | Lister les posts (filtrés par type/compétence) |
| `POST` | `/api/posts/` | Créer un post (offre ou demande) |
| `GET` | `/api/posts/{id}` | Détail d'un post |
| `PUT` | `/api/posts/{id}` | Modifier un post |
| `DELETE` | `/api/posts/{id}` | Supprimer un post |

**Payload création post** :
```json
{
  "type": "offer",
  "skill_id": 3,
  "mode": "both",
  "description": "Je propose des sessions en Python",
  "availabilities": [
    { "day_of_week": "Monday", "start_time": "09:00", "end_time": "11:00" }
  ]
}
```

---

#### Matches — `/api/matches`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/matches/` | Calcule et retourne les matches de l'utilisateur |
| `PUT` | `/api/matches/{id}/accept` | Accepter un match (crée une conversation) |
| `PUT` | `/api/matches/{id}/reject` | Refuser un match |

L'endpoint `GET /api/matches/` :
1. Lance l'algorithme de scoring pour l'utilisateur connecté
2. Insère les nouveaux matches calculés en base
3. Retourne tous les matches de l'utilisateur (mentor ou mentoré), triés par score décroissant

---

#### Chat — `/api`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/conversations` | Lister ses conversations |
| `GET` | `/api/conversations/{id}/messages` | Messages d'une conversation |
| `POST` | `/api/conversations/{id}/messages` | Envoyer un message |
| `POST` | `/api/conversations/direct` | Créer une conv. directe (sans match préalable) |

---

#### Skills — `/api/skills`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/skills/` | Lister toutes les compétences disponibles |

---

#### Health

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Statut de l'API (timestamp + env) |
| `GET` | `/` | Message de bienvenue + version |

---

## 6. Algorithme de matching

Le scoring est implémenté dans `backend/services/matching_service.py`.

### Critères de score (total max : 100 pts)

| Critère | Points |
|---------|--------|
| Compétence cible : mentor a `strong`, mentoré a `weak` sur la même skill | **+40** |
| Créneaux de disponibilité communs (au moins 1 slot) | **+30** (plafonné) |
| Même filière d'études | **+30** |
| Filière connexe (ex: IA ↔ IM) | **+15** |

### Filiaires connexes définies

```python
RELATED_FIELDS = {
    "IA":     ["IM", "GL"],
    "IM":     ["IA", "GL"],
    "GL":     ["IA", "IM", "SI"],
    "SI":     ["GL"],
    "SE&IoT": ["IA"],
}
```

### Seuil de match
Un match n'est retenu que si `score >= 40.0`. Cela garantit **au minimum** la compatibilité sur la compétence demandée.

### Flux de calcul
```
1. Charger l'utilisateur courant et tous les autres utilisateurs
2. Charger en lot (ANY(:user_ids)) toutes les compétences et disponibilités
3. Pour chaque autre utilisateur :
   a. Identifier les compétences où l'autre est fort ET l'utilisateur est faible
   b. Pour chaque compétence éligible → calculer le score
   c. Si score >= 40 → ajouter à la liste des matches
4. Trier par score décroissant
5. Dédupliquer contre les matches déjà en base avant insertion
```

---

## 7. Frontend — Vue.js

### Architecture

Le frontend est une **SPA (Single Page Application)** Vue.js 3 avec Vite.

#### Routing (Vue Router 4)

| Route | Composant | Authentification requise |
|-------|-----------|--------------------------|
| `/` | `LandingView.vue` | Non |
| `/login` | `LoginView.vue` | Non |
| `/register` | `RegisterView.vue` | Non |
| `/dashboard` | `DashboardView.vue` | Oui (guard JWT) |

Le guard de navigation vérifie la présence du token dans `localStorage` avant d'accéder aux routes protégées.

#### State Management (Store réactif)

Le store (`src/store/index.js`) est un **store réactif** Vue 3 (`reactive()`), sans Vuex ni Pinia, avec :

- **Persistance localStorage** : les données `user`, `posts`, `matches`, `conversations`, `skills` sont synchronisées via `watch()` pour survivre aux rechargements de page
- **Pattern Optimistic UI** : les actions utilisateur (création de post, envoi de message, ajout de compétence) mettent à jour l'UI **immédiatement** avant confirmation serveur, avec revert automatique en cas d'erreur
- **Chargement parallèle** : `fetchDashboardData()` déclenche 4 requêtes simultanées via `Promise.all()`

**Données du store :**

| Propriété | Description |
|-----------|-------------|
| `user` | Profil complet de l'utilisateur connecté |
| `token` | JWT stocké en localStorage |
| `posts` | Liste des posts de mentorat |
| `matches` | Liste des correspondances calculées |
| `conversations` | Liste des conversations avec messages |
| `skills` | Référentiel des compétences disponibles |
| `activeTab` | Onglet actif du dashboard |
| `theme` | Thème UI (`light` / `dark`) |

#### Vues

##### `DashboardView.vue`
Vue principale post-connexion, organisée en **5 onglets** :

| Onglet | Fonctionnalités |
|--------|----------------|
| **Accueil** | Résumé de l'activité (posts, matches, messages non-lus) |
| **Rechercher** | Exploration des posts publics, filtres type/compétence, messagerie directe |
| **Mes Posts** | CRUD des offres et demandes personnelles |
| **Correspondances** | Matches calculés, acceptation/refus, disponibilités du mentor |
| **Messages** | Interface de messagerie en temps réel par conversation |

##### `LandingView.vue`
Page d'accueil publique avec présentation de la plateforme, CTA vers inscription/connexion.

##### `LoginView.vue` / `RegisterView.vue`
Formulaires d'authentification avec validation côté client :
- Format e-mail valide
- Format téléphone strict : `+22901XXXXXXXX`
- Confirmation de mot de passe

#### Communication API (`src/services/api.js`)

Instance Axios configurée avec :
- `baseURL` pointant vers l'API FastAPI
- Intercepteur automatique pour injecter le JWT (`Authorization: Bearer <token>`) sur toutes les requêtes

---

## 8. Installation & Démarrage

### Prérequis

- Python ≥ 3.11
- Node.js ≥ 18
- PostgreSQL ≥ 14 (ou compte Supabase)
- Git

### 1. Cloner le dépôt

```bash
git clone https://github.com/PL1G26/PIL1_2526_26.git
cd PIL1_2526_26
```

### 2. Backend

```bash
cd backend

# Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# → Éditer .env avec vos paramètres (DATABASE_URL, SECRET_KEY, etc.)

# Initialiser la base de données
python init_db.py

# Lancer le serveur de développement
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> L'API sera accessible sur `http://localhost:8000`
> Swagger UI : `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend

# Installer les dépendances Node.js
npm install

# Lancer le serveur de développement
npm run dev
```

> L'application sera accessible sur `http://localhost:5173`

### 4. Build de production

```bash
# Frontend
cd frontend
npm run build
# → Génère les assets dans dist/

# Backend (production avec Gunicorn)
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 9. Variables d'environnement

Copier `.env.example` vers `.env` dans le dossier `backend/` :

```bash
cp backend/.env.example backend/.env
```

### Variables obligatoires

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Clé secrète pour signer les JWT | Générer avec : `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `TOKEN_EXPIRE_HOURS` | `24` | Durée de validité du JWT en heures |
| `ALGORITHM` | `HS256` | Algorithme JWT |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Origines CORS autorisées |
| `ENV` | `development` | Environnement (`development` / `production`) |
| `HOST` | `0.0.0.0` | Hôte du serveur uvicorn |
| `PORT` | `8000` | Port du serveur uvicorn |
| `LOG_LEVEL` | `INFO` | Niveau de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SUPABASE_URL` | — | URL du projet Supabase |
| `SUPABASE_ANON_KEY` | — | Clé publique Supabase |

> **Important** : Le fichier `.env` est ignoré par Git (`.gitignore`). Ne jamais committer vos secrets.

---

## 10. Tests

### Lancer la suite de tests

```bash
cd backend
source .venv/bin/activate

# Tous les tests
pytest test/ -v

# Un fichier spécifique
pytest test/test_routes.py -v

# Avec couverture de code
pytest test/ --cov=. --cov-report=html
```

### Fichiers de tests

| Fichier | Contenu |
|---------|---------|
| `test/test_models.py` | Tests unitaires des modèles SQLAlchemy |
| `test/test_schemas.py` | Tests de validation des schémas Pydantic |
| `test/test_services.py` | Tests de la logique métier (matching, auth, chat) |
| `test/test_routes.py` | Tests d'intégration des endpoints FastAPI |

---

## 11. Équipe

| Nom | Rôle | Contact |
|-----|------|---------|
| KPENONHOUN E. H. Adorée | Chef de projet & QA | hermionekpenonhoun@gmail.com |
| DHEHOUGA E. Estébania | Développeur Frontend | estebaniadjehouga@gmail.com |
| DINLA Marcel | Développeur Backend & Tech lead | delsdenlamarcel@gmail.com |
| AKOTONOU J-D B. Exauce | Développeur Backend | jeandedieuakotonou@gmail.com |
| AGO Mona | Développeur Frontend | agom601@gmail.com |
| HESSA I. D. Jody | Développeur Frontend | jodyhessa@gmail.com |
| BABAGBETO Ronald Orence | - | - |

---

## Conventions de développement

### Git Flow
```bash
# Nouvelle fonctionnalité
git checkout -b feature/nom-de-la-feature

# Correction de bug
git checkout -b fix/description-du-bug

# Commits conventionnels
git commit -m "feat: description"
git commit -m "fix: description"
git commit -m "docs: description"
git commit -m "refactor: description"
git commit -m "test: description"
```

### Code Python
- Formatage : **Black**
- Linting : **Flake8**
- Types : annotations de type Python systématiques
- Docstrings sur toutes les fonctions publiques

### Code Vue.js
- Composition API avec `<script setup>`
- Props typées
- Store centralisé pour l'état global
- Pas de mutation directe hors du store

---

## Outils IA utilisés

Ce projet a été développé avec l'assistance de modèles de langage de la famille **Claude** (Anthropic) :

| Modèle | Intégration | Usage principal |
|--------|-------------|-----------------|
| **Claude Haiku 4.5** | Extension **GitHub Copilot / Claude** dans **VS Code** | Complétion de code, suggestions inline, refactoring rapide |
| **Claude Sonnet 4.6** | **Antigravity** (assistant IA agentic) | Architecture, débogage, génération de documentation, revue de code |

---

**© 2026 — Projet Intégrateur PIL1_2526_26 — IFRI**
