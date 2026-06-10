# Définition des Entités — IFRI_MentorLink (Version 3)
## Modèle Conceptuel de Données (MCD) — Architecture unifiée

---

## 📋 Table des matières

1. [Entité users](#entité-users)
2. [Entité skills](#entité-skills)
3. [Entité user_skills](#entité-user_skills)
4. [Entité user_availabilities](#entité-user_availabilities)
5. [Entité mentorship_posts](#entité-mentorship_posts)
6. [Entité post_availabilities](#entité-post_availabilities)
7. [Entité matches](#entité-matches)
8. [Entité conversations](#entité-conversations)
9. [Entité messages](#entité-messages)
10. [Diagramme des relations](#diagramme-des-relations-mcd)

---

## Entité : users

**Description** : Représente chaque utilisateur de la plateforme (étudiants IFRI).

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique de l'utilisateur |
| `first_name` | VARCHAR(50) | NOT NULL | Prénom de l'utilisateur |
| `last_name` | VARCHAR(50) | NOT NULL | Nom de famille de l'utilisateur |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Adresse e-mail unique de l'utilisateur |
| `phone_number` | VARCHAR(20) | UNIQUE, NOT NULL | Numéro de téléphone unique |
| `password_hash` | VARCHAR(255) | NOT NULL | Hash du mot de passe |
| `profile_photo` | VARCHAR(255) | NULL | URL vers la photo de profil |
| `field_of_study` | VARCHAR(50) | NOT NULL | Filière : 'IA', 'IM', 'GL', 'SE&IoT', 'SI' |
| `level` | VARCHAR(20) | NOT NULL | Niveau d'étude : 'L1', 'L2', 'L3', 'M1', 'M2' |
| `bio` | TEXT | NULL | Courte biographie / présentation personnelle |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date/heure de création du compte |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Date/heure de dernière modification |

---

## Entité : skills

**Description** : Représente les matières ou compétences disponibles dans le système.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique de la compétence |
| `name` | VARCHAR(255) | UNIQUE, NOT NULL | Nom de la compétence (ex: 'Python', 'Mathématiques') |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date d'ajout de la compétence |

---

## Entité : user_skills

**Description** : Représente les compétences maîtrisées (points forts) ou les lacunes (points faibles) d'un utilisateur.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `user_id` | INT | FOREIGN KEY, PK | Lien vers l'utilisateur |
| `skill_id` | INT | FOREIGN KEY, PK | Lien vers la compétence |
| `proficiency` | VARCHAR(10) | NOT NULL | Niveau de maîtrise : 'strong' (peut enseigner) ou 'weak' (a besoin d'aide) |

### Contraintes supplémentaires
- **PRIMARY KEY** : `(user_id, skill_id)`
- **ON DELETE CASCADE** : Supprimé si l'utilisateur ou la compétence est supprimé.

---

## Entité : user_availabilities

**Description** : Représente les disponibilités horaires habituelles de l'utilisateur.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique |
| `user_id` | INT | FOREIGN KEY, NOT NULL | Lien vers l'utilisateur |
| `day_of_week` | VARCHAR(10) | NOT NULL | Jour de la semaine (ex: 'Monday', etc.) |
| `start_time` | TIME | NOT NULL | Heure de début |
| `end_time` | TIME | NOT NULL | Heure de fin |

### Contraintes supplémentaires
- **CHECK** : `start_time < end_time`
- **ON DELETE CASCADE** : Lié à `users`.

---

## Entité : mentorship_posts

**Description** : Représente les offres (je peux aider) et demandes (j'ai besoin d'aide) de mentorat publiées.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique du post |
| `user_id` | INT | FOREIGN KEY, NOT NULL | Lien vers l'utilisateur |
| `type` | VARCHAR(10) | NOT NULL | 'offer' (offre) ou 'request' (demande) |
| `skill_id` | INT | FOREIGN KEY, NOT NULL | Lien vers la compétence concernée |
| `mode` | VARCHAR(10) | NOT NULL | Format : 'online', 'offline', ou 'both' |
| `description` | TEXT | NULL | Description détaillée |
| `is_active` | BOOLEAN | DEFAULT TRUE | TRUE si actif, FALSE si archivé |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Dernière modification |

---

## Entité : post_availabilities

**Description** : Représente les disponibilités horaires spécifiques à un post de mentorat.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique |
| `post_id` | INT | FOREIGN KEY, NOT NULL | Lien vers le post |
| `day_of_week` | VARCHAR(10) | NOT NULL | Jour de la semaine |
| `start_time` | TIME | NOT NULL | Heure de début |
| `end_time` | TIME | NOT NULL | Heure de fin |

### Contraintes supplémentaires
- **CHECK** : `start_time < end_time`
- **ON DELETE CASCADE** : Lié à `mentorship_posts`.

---

## Entité : matches

**Description** : Représente les correspondances mentor ↔ mentoré calculées par l'algorithme.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique du match |
| `mentor_id` | INT | FOREIGN KEY, NOT NULL | ID de l'utilisateur mentor |
| `mentee_id` | INT | FOREIGN KEY, NOT NULL | ID de l'utilisateur mentoré |
| `offer_post_id`| INT | FOREIGN KEY, NULL | Lien vers le post d'offre |
| `request_post_id`| INT | FOREIGN KEY, NULL | Lien vers le post de demande |
| `skill_id` | INT | FOREIGN KEY, NULL | Compétence concernée |
| `score` | DECIMAL(5,2)| DEFAULT 0 | Score de compatibilité |
| `status` | VARCHAR(20) | DEFAULT 'pending' | 'pending', 'accepted', 'rejected' |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création |

### Contraintes supplémentaires
- **CHECK** : `mentor_id != mentee_id`

---

## Entité : conversations

**Description** : Représente une conversation de messagerie créée après l'acceptation d'un match.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique |
| `match_id` | INT | FOREIGN KEY, UNIQUE, NOT NULL | Lien vers le match associé |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date de création |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Dernière modification |

### Contraintes supplémentaires
- **ON DELETE CASCADE** : Lié à `matches`.

---

## Entité : messages

**Description** : Représente les messages échangés dans une conversation.

### Attributs

| Attribut | Type | Contrainte | Description |
|----------|------|-----------|-------------|
| `id` | SERIAL | PRIMARY KEY | Identifiant unique du message |
| `conversation_id`| INT | FOREIGN KEY, NOT NULL | Lien vers la conversation |
| `sender_id` | INT | FOREIGN KEY, NOT NULL | Lien vers l'expéditeur (users) |
| `content` | TEXT | NOT NULL | Contenu du message |
| `is_read` | BOOLEAN | DEFAULT FALSE | Statut de lecture |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Date d'envoi |

---

## Diagramme des relations (MCD)

Le diagramme d'architecture mis à jour est disponible dans `MCD_RELATIONS.mermaid`.

```
users (1) ──┬──→ (N) user_skills 
            ├──→ (N) user_availabilities
            ├──→ (N) mentorship_posts ────┐
            │                             ├──→ (N) matches ──→ (1) conversations ──→ (N) messages
            └──→ (N) matches (mentor/mentee) 
```

---

**Document créé pour le projet IFRI_MentorLink**

**Version 3.0 — Juin 2026**  
**Mise à jour :** Alignement complet avec le schéma réel de la base de données (`backend/schema.sql`).
