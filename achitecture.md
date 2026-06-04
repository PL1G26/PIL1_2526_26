```md
PIL1_2526_26/
│
├── backend/
│   ├── app.py                          # Point d'entrée Flask/Django
│   ├── config.py                       # Configuration (BDD, JWT, env)
│   ├── requirements.txt                # Dépendances Python
│   ├── .env.example                    # Variables d'environnement (modèle)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                     # /register, /login, /logout
│   │   ├── profile.py                  # GET/PUT /profile
│   │   ├── offers.py                   # GET/POST /offers
│   │   ├── matching.py                 # GET /match (algorithme)
│   │   └── messages.py                 # GET/POST /messages, /conversations
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                     # Classe Utilisateur
│   │   ├── offer.py                    # Classe Offre/Demande
│   │   └── message.py                  # Classe Message/Conversation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db.py                       # Fonctions de connexion BDD
│   │   ├── auth.py                     # Hashage password, JWT
│   │   ├── matching.py                 # Algorithme de score
│   │   └── validators.py               # Validation des données
│   │
│   └── tests/
│       ├── test_auth.py
│       └── test_matching.py
│
├── frontend/
│   ├── index.html                      # Page d'accueil / redirection login
│   │
│   ├── pages/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html              # Page d'accueil une fois connecté
│   │   ├── profile.html
│   │   ├── offers.html
│   │   ├── matching.html
│   │   └── messaging.html
│   │
│   ├── assets/
│   │   ├── css/
│   │   │   ├── style.css               # Styles globaux
│   │   │   ├── colors.css              # Palette de couleurs
│   │   │   └── responsive.css
│   │   ├── js/
│   │   │   ├── app.js                  # Logique globale
│   │   │   ├── auth.js                 # Gestion authentification
│   │   │   ├── api.js                  # Appels API (fetch)
│   │   │   ├── messaging.js            # Logique messagerie
│   │   │   └── utils.js                # Fonctions utilitaires
│   │   └── images/
│   │       └── logo.png
│   │
│   └── components/
│       ├── navbar.html
│       ├── footer.html
│       └── modals.html
│
├── docs/
│   ├── index.html                      # Rapport du projet (HTML)
│   ├── MCD.png                         # Modèle conceptuel de données
│   ├── MLD.png                         # Modèle logique de données
│   ├── architecture.md                 # Description architecture
│   └── screenshots/
│       ├── login.png
│       ├── matching.png
│       └── messaging.png
│
├── schema.sql                          # Script SQL création BDD
├── README.md                           # Instructions de lancement
├── .gitignore                          # Ignorer .env, __pycache__, etc.
└── .github/
    └── workflows/
        └── ci.yml                      # Intégration continue optionnelle

```