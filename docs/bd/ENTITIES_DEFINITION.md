# Définition des Entités — IFRI_MentorLink (Version 2)
## Modèle Conceptuel de Données (MCD) — Architecture dissociée

---

## 📋 Table des matières

1. [Entité Utilisateurs](#entité-utilisateurs)
2. [Entité Compétences](#entité-compétences)
3. [Entité Lacunes](#entité-lacunes)
4. [Entité Disponibilités](#entité-disponibilités)
5. [Entité Offres](#entité-offres)
6. [Entité Demandes](#entité-demandes)
7. [Entité Matchs](#entité-matchs)
8. [Entité Conversations](#entité-conversations)
9. [Entité Messages](#entité-messages)
10. [Relations entre entités](#relations-entre-entités)

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

**Description** : Représente les matières/domaines que l'utilisateur maîtrise (points forts).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la compétence |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur propriétaire |
| `matiere` | VARCHAR(100) | NOT NULL | Nom de la matière maîtrisée (ex: 'Python', 'Maths', 'Algorithmique') |
| `niveau_maitrise` | ENUM | DEFAULT 'intermediaire' | Niveau de maîtrise : 'debutant', 'intermediaire', 'avance', 'expert' |
| `experience_annees` | INT | NULL | Nombre d'années d'expérience (optionnel) |
| `certification` | VARCHAR(255) | NULL | Certification ou qualification possédée (optionnel) |
| `date_acquisition` | DATE | NULL | Date d'acquisition de la compétence |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure d'ajout de la compétence au profil |

### Contraintes supplémentaires

- **UNIQUE KEY** : `(user_id, matiere)` — Un utilisateur ne peut avoir qu'une seule entrée par matière
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses compétences sont supprimées
- **INDEX** : `(user_id)` pour optimiser les recherches par utilisateur

### Exemple d'enregistrements

```
id: 1, user_id: 1, matiere: 'Python', niveau_maitrise: 'expert', experience_annees: 3, certification: NULL, date_acquisition: 2023-06-15, created_at: 2026-06-02 14:30:00

id: 2, user_id: 1, matiere: 'JavaScript', niveau_maitrise: 'avance', experience_annees: 2, certification: NULL, date_acquisition: 2024-01-10, created_at: 2026-06-02 14:30:00

id: 3, user_id: 1, matiere: 'Algorithmique', niveau_maitrise: 'intermediaire', experience_annees: 1, certification: NULL, date_acquisition: 2025-09-01, created_at: 2026-06-02 14:30:00
```

---

## Entité : LACUNES

**Description** : Représente les matières/domaines où l'utilisateur a besoin d'aide (points faibles).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la lacune |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur concerné |
| `matiere` | VARCHAR(100) | NOT NULL | Nom de la matière à améliorer (ex: 'Mathématiques', 'Physique') |
| `severite` | ENUM | NOT NULL | Sévérité de la lacune : 'legere', 'moderee', 'severe' |
| `raison` | TEXT | NULL | Raison/contexte de la lacune (ex: "J'ai manqué des cours", "C'est ma première fois en ML") |
| `objectif` | VARCHAR(255) | NULL | Objectif souhaité (ex: "Passer le prochain contrôle", "Comprendre les bases") |
| `priorite` | ENUM | DEFAULT 'normal' | Priorité : 'basse', 'normal', 'haute' |
| `date_identification` | DATE | NOT NULL | Date où la lacune a été identifiée |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure d'ajout au profil |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Dernière modification |

### Contraintes supplémentaires

- **UNIQUE KEY** : `(user_id, matiere)` — Un utilisateur ne peut avoir qu'une seule entrée par matière
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses lacunes sont supprimées
- **INDEX** : `(user_id, priorite)` pour les recherches par urgence

### Exemple d'enregistrements

```
id: 1, user_id: 2, matiere: 'Mathématiques', severite: 'moderee', raison: 'Difficultés avec les dérivées', objectif: 'Réussir le prochain DS', priorite: 'haute', date_identification: 2026-04-15, created_at: 2026-06-02 15:00:00, updated_at: 2026-06-02 15:00:00

id: 2, user_id: 2, matiere: 'Physique', severite: 'legere', raison: 'Besoin de consolider les bases', objectif: 'Comprendre la mécanique', priorite: 'normal', date_identification: 2026-05-01, created_at: 2026-06-02 15:05:00, updated_at: 2026-06-02 15:05:00

id: 3, user_id: 2, matiere: 'Base de données SQL', severite: 'severe', raison: 'Première approche de SQL', objectif: 'Maîtriser les jointures et les requêtes complexes', priorite: 'haute', date_identification: 2026-05-20, created_at: 2026-06-02 15:10:00, updated_at: 2026-06-02 15:10:00
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
| `type` | ENUM | DEFAULT 'regulier' | Type : 'regulier' (récurrent) ou 'ponctuel' (une seule fois) |

### Contraintes supplémentaires

- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses disponibilités sont supprimées
- **Validation logique** : `heure_fin` > `heure_debut`

### Exemple d'enregistrements

```
id: 1, user_id: 1, jour: 'lundi', heure_debut: 18:00:00, heure_fin: 20:00:00, type: 'regulier'
id: 2, user_id: 1, jour: 'mercredi', heure_debut: 19:00:00, heure_fin: 21:00:00, type: 'regulier'
id: 3, user_id: 1, jour: 'jeudi', heure_debut: 17:00:00, heure_fin: 19:00:00, type: 'regulier'
id: 4, user_id: 2, jour: 'lundi', heure_debut: 15:00:00, heure_fin: 17:00:00, type: 'regulier'
```

---

## Entité : OFFRES

**Description** : Représente les offres de mentorat publiées par un utilisateur (je peux aider).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de l'offre |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur mentor qui propose |
| `matieres` | VARCHAR(500) | NOT NULL | Matières concernées (format JSON ou CSV) |
| `format` | ENUM | NOT NULL | Format proposé : 'presentiel', 'ligne', 'les_deux' |
| `description` | TEXT | NULL | Description détaillée de l'offre (expertise, approche pédagogique, etc.) |
| `niveau_min` | INT | NULL | Niveau minimum des mentorés (ex: 1 pour niveau 1 et 2) |
| `niveau_max` | INT | NULL | Niveau maximum des mentorés (ex: 2 pour niveaux 1 et 2) |
| `taux_horaire` | DECIMAL(8,2) | NULL | Taux horaire proposé (optionnel, 0 si gratuit) |
| `statut` | ENUM | DEFAULT 'active' | Statut : 'active' ou 'inactive' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création de l'offre |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Date/heure de dernière modification |

### Contraintes supplémentaires

- **INDEX** sur `(user_id, statut)` pour les recherches optimisées
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses offres sont supprimées

### Exemple d'enregistrement

```
id: 1
user_id: 1
matieres: '["Python", "Algorithmique"]'
format: 'ligne'
description: 'Je peux vous aider en Python et Algorithmique. Approche basée sur des exercices pratiques. Disponible pour les niveaux 1 et 2.'
niveau_min: 1
niveau_max: 2
taux_horaire: 0.00
statut: 'active'
created_at: 2026-06-03 10:00:00
updated_at: 2026-06-03 10:00:00
```

---

## Entité : DEMANDES

**Description** : Représente les demandes de mentorat publiées par un utilisateur (j'ai besoin d'aide).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la demande |
| `user_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | Lien vers l'utilisateur mentoré qui demande |
| `matieres` | VARCHAR(500) | NOT NULL | Matières pour lesquelles l'aide est demandée (JSON ou CSV) |
| `format` | ENUM | NOT NULL | Format préféré : 'presentiel', 'ligne', 'les_deux' |
| `description` | TEXT | NULL | Description détaillée de la demande (difficultés spécifiques, objectifs, etc.) |
| `urgence` | ENUM | DEFAULT 'normal' | Urgence : 'basse', 'normal', 'haute' |
| `budget_max` | DECIMAL(8,2) | NULL | Budget maximum disposé à payer (optionnel) |
| `statut` | ENUM | DEFAULT 'active' | Statut : 'active' ou 'resolue' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création de la demande |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Date/heure de dernière modification |

### Contraintes supplémentaires

- **INDEX** sur `(user_id, statut, urgence)` pour les recherches optimisées
- **ON DELETE CASCADE** : Si l'utilisateur est supprimé, ses demandes sont supprimées

### Exemple d'enregistrement

```
id: 1
user_id: 2
matieres: '["Mathématiques", "Physique"]'
format: 'presentiel'
description: 'J\'ai besoin d\'aide pour comprendre les dérivées en Maths et la mécanique en Physique. Je suis libre les jeudis et dimanches.'
urgence: 'haute'
budget_max: 50.00
statut: 'active'
created_at: 2026-06-03 11:30:00
updated_at: 2026-06-03 11:30:00
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
| `offre_id` | INT | FOREIGN KEY (offres.id), NOT NULL | Lien vers l'offre du mentor |
| `demande_id` | INT | FOREIGN KEY (demandes.id), NOT NULL | Lien vers la demande du mentoré |
| `score_competences` | DECIMAL(5,2) | NULL | Score de compatibilité des compétences (0-100) |
| `score_horaires` | DECIMAL(5,2) | NULL | Score de compatibilité des horaires (0-100) |
| `score_filiere` | DECIMAL(5,2) | NULL | Score de proximité filière/niveau (0-100) |
| `score_global` | DECIMAL(5,2) | NULL | Score global de compatibilité (0-100) |
| `statut` | ENUM | DEFAULT 'propose' | Statut : 'propose', 'accepte', 'rejete', 'en_cours', 'termine' |
| `raison_rejet` | TEXT | NULL | Raison du rejet (si applicable) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création du match |

### Contraintes supplémentaires

- **UNIQUE KEY** : `(mentor_id, mentore_id)` — Un seul match entre deux utilisateurs
- **INDEX** sur `(mentor_id, statut)`, `(mentore_id, statut)` pour les recherches
- **ON DELETE CASCADE** : Suppression en cascade

### Exemple d'enregistrement

```
id: 1
mentor_id: 1
mentore_id: 2
offre_id: 1
demande_id: 1
score_competences: 90.00
score_horaires: 85.00
score_filiere: 75.00
score_global: 85.33
statut: 'accepte'
raison_rejet: NULL
created_at: 2026-06-03 12:00:00
```

---

## Entité : CONVERSATIONS

**Description** : Représente les conversations de messagerie entre deux utilisateurs matchés.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | Identifiant unique de la conversation |
| `match_id` | INT | FOREIGN KEY (matchs.id), NOT NULL UNIQUE | Lien vers le match associé |
| `user_a_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du premier utilisateur |
| `user_b_id` | INT | FOREIGN KEY (utilisateurs.id), NOT NULL | ID du second utilisateur |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date/heure de création de la conversation |

### Contraintes supplémentaires

- **ON DELETE CASCADE** : Si un utilisateur ou un match est supprimé, la conversation est supprimée
- **UNIQUE KEY** : `match_id` — Une seule conversation par match

### Exemple d'enregistrement

```
id: 1
match_id: 1
user_a_id: 1
user_b_id: 2
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

- **INDEX** sur `(conversation_id, created_at)` pour optimiser les recherches
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
expediteur_id: 2
contenu: 'Salut Alice ! Je suis libre jeudi soir après 19h. Ça te convient ?'
lu: TRUE
created_at: 2026-06-03 13:05:00
```

---

## Diagramme des relations (MCD)

```
UTILISATEURS (1) ──┬──→ (N) COMPÉTENCES 
                    ├──→ (N) LACUNES
                    ├──→ (N) DISPONIBILITÉS
                    ├──→ (N) OFFRES ────┐
                    │                    ├──→ (N) MATCHS ──→ (1) CONVERSATIONS ──→ (N) MESSAGES
                    └──→ (N) DEMANDES ──┘
```

---

## Relations détaillées

| Relation | Type | Clés | Cardinalité |
|----------|------|------|------------|
| UTILISATEURS → COMPÉTENCES | 1-N | `competences.user_id` | 0 à N compétences par user |
| UTILISATEURS → LACUNES  | 1-N | `lacunes.user_id` | 0 à N lacunes par user |
| UTILISATEURS → DISPONIBILITÉS | 1-N | `disponibilites.user_id` | 0 à N créneaux par user |
| UTILISATEURS → OFFRES | 1-N | `offres.user_id` | 0 à N offres par user |
| UTILISATEURS → DEMANDES | 1-N | `demandes.user_id` | 0 à N demandes par user |
| OFFRES → MATCHS | 1-N | `matchs.offre_id` | 0 à N matchs par offre |
| DEMANDES → MATCHS | 1-N | `matchs.demande_id` | 0 à N matchs par demande |
| UTILISATEURS → MATCHS (mentor) | 1-N | `matchs.mentor_id` | 0 à N matchs comme mentor |
| UTILISATEURS → MATCHS (mentoré) | 1-N | `matchs.mentore_id` | 0 à N matchs comme mentoré |
| MATCHS → CONVERSATIONS | 1-1 | `conversations.match_id` UNIQUE | 0 ou 1 conversation par match |
| CONVERSATIONS → MESSAGES | 1-N | `messages.conversation_id` | 0 à N messages par conversation |
| UTILISATEURS → MESSAGES (expediteur) | 1-N | `messages.expediteur_id` | 0 à N messages envoyés |

---

## Résumé final des entités (V3)

```
✅ UTILISATEURS (12 attributs)
✅ COMPÉTENCES (7 attributs) — Points forts
✅ LACUNES (8 attributs) — Points faibles
✅ DISPONIBILITÉS (5 attributs)
✅ OFFRES (11 attributs)
✅ DEMANDES (9 attributs)
✅ MATCHS (11 attributs)
✅ CONVERSATIONS (4 attributs)
✅ MESSAGES (5 attributs)

Total : 10 entités, ~72 attributs
```

---

**Document créé pour le projet IFRI_MentorLink**

**Version 2.0 — Juin 2026**  
**Améliorations :** 
  - Dissociation COMPÉTENCES / LACUNES
  - Dissociation OFFRES / DEMANDES
