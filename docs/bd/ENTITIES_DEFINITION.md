# Définition des Entités — IFRI_MentorLink
## Modèle Conceptuel de Données (MCD)

---

## 📋 Table des matières

1. [Entité Utilisateurs](#entité-utilisateurs)
2. [Entité Compétences](#entité-compétences)
3. [Entité Disponibilités](#entité-disponibilités)
4. [Entité Offres/Demandes](#entité-offresdemandes)
5. [Entité Matchs](#entité-matchs)
6. [Entité Conversations](#entité-conversations)
7. [Entité Messages](#entité-messages)
8. [Relations entre entités](#relations-entre-entités)

---

## Entité : UTILISATEURS

**Description** : Représente chaque utilisateur de la plateforme (étudiants IFRI).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de l'utilisateur |
| `nom` | VARCHAR(100) | NOT NULL | Nom de famille de l'utilisateur |
| `prenom` | VARCHAR(100) | NOT NULL | Prénom de l'utilisateur |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Adresse e-mail unique de l'utilisateur |
| `telephone` | VARCHAR(20) | UNIQUE, NOT NULL | Numéro de téléphone unique |
| `mot_de_passe` | VARCHAR(255) | NOT NULL | Hash bcrypt du mot de passe (jamais en clair) |
| `filiere` | ENUM | NOT NULL | Filière : 'IA', 'IM', 'GL', 'SE&IoT', 'SI' |
| `niveau` | INT | NOT NULL | Année d'étude : 1, 2, 3, etc. |
| `bio` | TEXT | NULL | Courte biographie / présentation personnelle |
| `photo_url` | VARCHAR(255) | NULL | Chemin vers la photo de profil |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création du compte |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de dernière modification |

### Exemple d'enregistrement

```
id: 1
nom: Martin
prenom: Alice
email: alice.martin@ifri.edu
telephone: +229 12345678
mot_de_passe: $2y$10$abcdef... (bcrypt hash)
filiere: IA
niveau: 2
bio: Passionnée par l'intelligence artificielle
photo_url: /uploads/alice_martin.jpg
created_at: 2026-06-02 14:30:00
updated_at: 2026-06-02 14:30:00
```

---

## Entité : COMPÉTENCES

**Description** : Représente les points forts et les lacunes de chaque utilisateur (matières maîtrisées ou à améliorer).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la compétence |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur propriétaire |
| `matiere` | VARCHAR(100) | NOT NULL | Nom de la matière/compétence (ex: 'Python', 'Maths', 'Algorithmique') |
| `type` | ENUM | NOT NULL | Type de compétence : 'fort' (maîtrisée) ou 'faible' (à améliorer) |

### Contraintes supplémentaires

- **UNIQUE KEY** : `(user_id, matiere, type)` — Un utilisateur ne peut avoir qu'une seule entrée par matière et type
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses compétences sont supprimées

### Exemple d'enregistrements

```
id: 1, user_id: 1, matiere: 'Python', type: 'fort'
id: 2, user_id: 1, matiere: 'JavaScript', type: 'fort'
id: 3, user_id: 1, matiere: 'Mathématiques', type: 'faible'
id: 4, user_id: 1, matiere: 'Algorithmique', type: 'faible'
```

---

## Entité : DISPONIBILITÉS

**Description** : Représente les créneaux horaires disponibles pour le mentorat de chaque utilisateur.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la disponibilité |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur |
| `jour` | VARCHAR(20) | NOT NULL | Jour de la semaine : 'lundi', 'mardi', ..., 'dimanche' |
| `heure_debut` | TIME | NOT NULL | Heure de début du créneau (format HH:MM:SS) |
| `heure_fin` | TIME | NOT NULL | Heure de fin du créneau (format HH:MM:SS) |

### Contraintes supplémentaires

- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses disponibilités sont supprimées
- **Validation logique** : `heure_fin` > `heure_debut`

### Exemple d'enregistrements

```
id: 1, user_id: 1, jour: 'lundi', heure_debut: 18:00:00, heure_fin: 20:00:00
id: 2, user_id: 1, jour: 'mercredi', heure_debut: 19:00:00, heure_fin: 21:00:00
id: 3, user_id: 1, jour: 'jeudi', heure_debut: 17:00:00, heure_fin: 19:00:00
id: 4, user_id: 2, jour: 'lundi', heure_debut: 15:00:00, heure_fin: 17:00:00
```

---

## Entité : OFFRES_DEMANDES

**Description** : Représente les offres de mentorat (je peux aider) ou les demandes de mentorat (j'ai besoin d'aide).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de l'offre/demande |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur qui publie |
| `type` | ENUM | NOT NULL | Type : 'offre' (je propose) ou 'demande' (je cherche) |
| `matieres` | VARCHAR(500) | NOT NULL | Matières concernées (format JSON ou CSV) |
| `format` | ENUM | NOT NULL | Format proposé : 'presentiel', 'ligne', 'les_deux' |
| `description` | TEXT | NULL | Description détaillée de l'offre/demande |
| `statut` | ENUM | DEFAULT 'active' | Statut : 'active' ou 'inactive' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création |

### Contraintes supplémentaires

- **INDEX** sur `type`, `user_id` pour les recherches optimisées
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses offres sont supprimées

### Exemple d'enregistrements

```
id: 1
user_id: 1
type: 'offre'
matieres: '["Python", "Algorithmique"]'
format: 'ligne'
description: 'Je peux vous aider en Python et Algorithmique pour le niveau 1. Je suis disponible les lundis et jeudis.'
statut: 'active'
created_at: 2026-06-03 10:00:00

---

id: 2
user_id: 2
type: 'demande'
matieres: '["Mathématiques", "Physique"]'
format: 'presentiel'
description: 'Je cherche un mentor pour progresser en Maths et Physique'
statut: 'active'
created_at: 2026-06-03 11:30:00
```

---

## Entité : MATCHS

**Description** : Représente les appairements mentor-mentoré proposés par l'algorithme.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du match |
| `mentor_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du mentor (celui qui aide) |
| `mentore_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du mentoré (celui qui reçoit l'aide) |
| `score` | DECIMAL(5,2) | NULL | Score de compatibilité (0.00 à 100.00) |
| `statut` | ENUM | DEFAULT 'propose' | Statut : 'propose', 'accepte', 'rejete', 'en_cours' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création du match |

### Contraintes supplémentaires

- **UNIQUE KEY** : `(mentor_id, mentore_id)` — Un seul match entre deux utilisateurs
- **INDEX** sur `mentor_id`, `mentore_id` pour les recherches
- **ON DELETE CASCADE** : Si un utilisateur est supprimé, ses matches sont supprimés

### Exemple d'enregistrements

```
id: 1
mentor_id: 1
mentore_id: 2
score: 87.50
statut: 'propose'
created_at: 2026-06-03 12:00:00

---

id: 2
mentor_id: 1
mentore_id: 3
score: 75.25
statut: 'accepte'
created_at: 2026-06-03 12:05:00
```

---

## Entité : CONVERSATIONS

**Description** : Représente les conversations de messagerie entre deux utilisateurs matchés.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la conversation |
| `match_id` | INT | FOREIGN KEY (matchs.id), NOT NULL | Lien vers le match associé |
| `user_a_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du premier utilisateur |
| `user_b_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du second utilisateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création de la conversation |

### Contraintes supplémentaires

- **ON DELETE CASCADE** : Si un utilisateur ou un match est supprimé, la conversation est supprimée
- **Unicité logique** : Une conversation existe pour chaque match accepté

### Exemple d'enregistrement

```
id: 1
match_id: 2
user_a_id: 1
user_b_id: 3
created_at: 2026-06-03 12:30:00
```

---

## Entité : MESSAGES

**Description** : Représente les messages échangés dans une conversation.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique du message |
| `conversation_id` | INT | FOREIGN KEY (conversations.id), NOT NULL | Lien vers la conversation |
| `expediteur_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID de l'utilisateur qui envoie |
| `contenu` | TEXT | NOT NULL | Contenu du message (texte) |
| `lu` | BOOLEAN | DEFAULT FALSE | Statut : FALSE (non lu) ou TRUE (lu) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure d'envoi du message |

### Contraintes supplémentaires

- **INDEX** sur `conversation_id`, `created_at` pour optimiser les recherches
- **ON DELETE CASCADE** : Si la conversation est supprimée, ses messages sont supprimés

### Exemple d'enregistrements

```
id: 1
conversation_id: 1
expediteur_id: 1
contenu: 'Bonjour ! Je peux t'aider en Python. Quand es-tu disponible ?'
lu: TRUE
created_at: 2026-06-03 13:00:00

---

id: 2
conversation_id: 1
expediteur_id: 3
contenu: 'Salut Alice ! Je suis libre jeudi soir après 19h. Ça te convient ?'
lu: TRUE
created_at: 2026-06-03 13:05:00

---

id: 3
conversation_id: 1
expediteur_id: 1
contenu: 'Parfait ! On se voit jeudi à 19h30 en ligne ?'
lu: FALSE
created_at: 2026-06-03 13:10:00
```

---

## Relations entre entités

### Diagramme des relations

```
UTILISATEURS (1) ←→ (N) COMPÉTENCES
     ↓
     ├─→ (1) ←→ (N) DISPONIBILITÉS
     │
     ├─→ (1) ←→ (N) OFFRES_DEMANDES
     │
     └─→ (N) ←→ (N) MATCHS
           ↓
           (1) ←→ (N) CONVERSATIONS
                ↓
                (1) ←→ (N) MESSAGES
```

### Descriptions des relations

#### 1. UTILISATEURS → COMPÉTENCES
- **Type** : 1 à N (Un utilisateur a plusieurs compétences)
- **Clé étrangère** : `compétences.user_id` → `utilisateurs.id`
- **Cardinalité** : Un utilisateur peut avoir 0 à N compétences

#### 2. UTILISATEURS → DISPONIBILITÉS
- **Type** : 1 à N (Un utilisateur a plusieurs créneaux de disponibilité)
- **Clé étrangère** : `disponibilités.user_id` → `utilisateurs.id`
- **Cardinalité** : Un utilisateur peut avoir 0 à N créneaux

#### 3. UTILISATEURS → OFFRES_DEMANDES
- **Type** : 1 à N (Un utilisateur peut publier plusieurs offres/demandes)
- **Clé étrangère** : `offres_demandes.user_id` → `utilisateurs.id`
- **Cardinalité** : Un utilisateur peut avoir 0 à N offres/demandes

#### 4. UTILISATEURS → MATCHS
- **Type** : N à N (Un utilisateur peut être mentor ou mentoré dans plusieurs matchs)
- **Clés étrangères** : 
  - `matchs.mentor_id` → `utilisateurs.id`
  - `matchs.mentore_id` → `utilisateurs.id`
- **Cardinalité** : Un utilisateur peut participer à N matchs

#### 5. MATCHS → CONVERSATIONS
- **Type** : 1 à N (Un match génère 1 conversation)
- **Clé étrangère** : `conversations.match_id` → `matchs.id`
- **Cardinalité** : Un match peut avoir 0 ou 1 conversation

#### 6. CONVERSATIONS → MESSAGES
- **Type** : 1 à N (Une conversation contient plusieurs messages)
- **Clé étrangère** : `messages.conversation_id` → `conversations.id`
- **Cardinalité** : Une conversation peut avoir 0 à N messages

#### 7. UTILISATEURS → MESSAGES
- **Type** : 1 à N (Un utilisateur envoie plusieurs messages)
- **Clé étrangère** : `messages.expediteur_id` → `utilisateurs.id`
- **Cardinalité** : Un utilisateur peut envoyer N messages

---

## Règles métier et contraintes

### Intégrité des données

1. **Unicité des comptes** : Chaque email et téléphone sont uniques
2. **Sécurité des mots de passe** : Toujours hashés en bcrypt, jamais en clair
3. **Cascades de suppression** : Si un utilisateur est supprimé, toutes ses données dépendantes le sont aussi
4. **Validation des horaires** : `heure_fin` > `heure_debut`

### Règles applicatives

1. **Matching** : Un utilisateur ne peut matcher qu'avec des utilisateurs d'un niveau proche (±1)
2. **Conversations** : Ne peuvent être créées que si le match est accepté
3. **Messages** : Seuls les participants d'une conversation peuvent envoyer des messages
4. **Offres/Demandes** : Chaque utilisateur peut avoir plusieurs offres actives

---

## Notes d'implémentation

### Formats de données

- **Matieres (JSON)** : 
  ```json
  ["Python", "Algorithmique", "Web"]
  ```

- **Dates/Heures** :
  - Format DATE : YYYY-MM-DD
  - Format TIME : HH:MM:SS
  - Format TIMESTAMP : YYYY-MM-DD HH:MM:SS

### Sécurité

- Les mots de passe doivent être hashés côté serveur avec **bcrypt** (min. salt rounds = 10)
- Les tokens JWT doivent expirer après **24 heures**
- Validation et assainissement de toutes les entrées côté serveur

### Performance

- INDEX sur les clés étrangères pour optimiser les JOINs
- INDEX sur `offres_demandes.type` et `offres_demandes.user_id` pour les recherches
- INDEX sur `messages.created_at` pour l'historique

---

**Document créé pour le projet IFRI_MentorLink**  
**Version 1.0 — Juin 2026**
