# Guide de contribution

Merci de contribuer à ce projet ! Ce guide vous aidera à comprendre comment proposer des changements de façon efficace et homogène.

## Table des matières
- [Convention des messages de commit](#convention-des-messages-de-commit)
  - [Format](#format)
  - [Types autorisés](#types-autorisés)
  - [Règles détaillées](#règles-détaillées)
  - [Exemples valides / invalides](#exemples-valides--invalides)
- [Processus de contribution](#processus-de-contribution)
  - [Branches](#branches)
  - [Pull Requests](#pull-requests)

---

## Convention des messages de commit

Ce projet suvra la spécification **Conventional Commits**. Tous les messages de commit doivent respecter le format décrit ci-dessous.  

### Format
```
type(scope): description courte
```

Ou avec un corps plus long :
```
type(scope): description courte

Footer
```

Corps détaillé expliquant le "quoi" et le "pourquoi".
Footer référençant les issues éventuelles (ex : Fixes #123)


### Types autorisés

| Type      | Usage                                           |
|-----------|-------------------------------------------------|
| `feat`    | Nouvelle fonctionnalité (déclenche une version mineure) |
| `fix`     | Correction de bug (déclenche une version de correctif) |
| `docs`    | Modification de la documentation                |
| `style`   | Formatage, espaces, point-virgules, *aucun changement fonctionnel* |
| `refactor`| Refactorisation du code (ni correction, ni nouvelle fonctionnalité) |
| `perf`    | Amélioration de performance                     |
| `test`    | Ajout ou correction de tests                    |
| `chore`   | Mise à jour de dépendances, configuration, build |
| `ci`      | Modification des scripts d’intégration continue |
| `revert`  | Annulation d’un commit précédent                |


### Règles détaillées

- **Type** : obligatoire, doit être dans la liste ci-dessus.
- **Scope** : optionnel mais recommandé (ex: `api`, `auth`, `ui`, `db`). Entre parenthèses, juste après le type.
- **Sujet (description courte)** :
  - Maximum **50 caractères**.
  - Impératif présent (ex: "ajouter", "corriger", "mettre à jour").
  - Pas de majuscule en début de phrase.
  - Pas de point final.
- **Corps (body)** (si nécessaire) :
  - Séparé du sujet par une ligne vide.
  - Explique **ce qui** change et **pourquoi**.
  - Maximum 72 caractères par ligne.
- **Footer** (si nécessaire) :
  - Utilisé pour référencer des issues (ex: `Fixes #123`, `Closes #456, #789`).
  - Séparé du corps par une ligne vide.

### Exemples valides / invalides

#### ✅ Accepté
```
feat(api): ajouter endpoint de recherche
```

```
fix(auth): corriger le rafraîchissement du token JWT
```

```
docs: mettre à jour le README sur l'installation
```

```
feat(ui): ajouter thème sombre
```

```
Ajoute un switch dans les préférences

Persiste le choix dans localStorage

Closes #234
```

#### ❌ Refusé
```bash
Added new search feature # type manquant, majuscule, passé composé
```
```bash
fix(ui): corrected button style # anglais, passé composé, non impératif
```
```bash
WIP # pas de type, pas de description utile
```




## Processus de contribution

### Branches

- **`main`** : branche de production. Interdiction de committer directement.
- **`develop`** : branche d’intégration.
- **Branches de fonctionnalité** : nommez-les selon le type et le scope, ex : `feat/auth`, `fix/auth-token`, `docs/readme`.

### Pull Requests

1. **Créez une branche** à partir de `main` (ou `develop`).
2. **Faites vos commits** en respectant la convention.
3. **Ouvrez une Pull Request** (PR) sur GitHub.
   - Le titre de la PR doit suivre le même format qu’un commit (ex: `feat(api): ajouter recherche full-text`).
   - Décrivez les changements, ajoutez des captures d’écran si nécessaire.
4. **Vérifiez que la CI passe** (lint, tests, validation des commits).
