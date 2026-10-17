# Explication de Chaque Fichier du Projet

## Fichiers Python

### `app.py` - Application Principale (297 lignes)

**Rôle** : C'est le cœur de l'application Flask. Il contient toute la logique métier.

**Structure** :
- **Lignes 1-18** : Imports et chargement des variables d'environnement
- **Lignes 20-26** : Configuration de Flask (clé secrète, cookies sécurisés)
- **Lignes 28-32** : Configuration du hachage Argon2id et du rate limiting
- **Lignes 34-60** : Gestion de la base de données SQLite
- **Lignes 62-92** : Validation des mots de passe (ASVS 6.2.1, 6.2.4, 6.2.5)
- **Lignes 94-120** : Limitation des tentatives de connexion (ASVS 6.1.1, 6.3.1)
- **Lignes 122-128** : Décorateur pour protéger les routes
- **Lignes 130-137** : Route `/` - Redirection
- **Lignes 139-177** : Route `/register` - Inscription
- **Lignes 179-233** : Route `/login` - Connexion avec rate limiting
- **Lignes 235-239** : Route `/dashboard` - Page protégée
- **Lignes 241-284** : Route `/change-password` - Modification du mot de passe
- **Lignes 286-292** : Route `/logout` - Déconnexion
- **Lignes 294-306** : Lancement de l'application

**Concepts Clés** :
- **Requêtes paramétrées** : Toutes les requêtes SQL utilisent `?` pour éviter les injections
- **Hachage Argon2id** : `ph.hash(password)` et `ph.verify(hash, password)`
- **Sessions Flask** : `session['user_id']` pour garder l'utilisateur connecté
- **Flash messages** : `flash(message, category)` pour afficher des messages
- **Context g** : Stockage temporaire de la connexion DB pendant la requête

---

## Templates HTML

### `templates/login.html`

**Rôle** : Page de connexion

**Éléments Importants** :
- `<input type="password">` - Masque le mot de passe (ASVS 6.2.6)
- `autocomplete="current-password"` - Permet les gestionnaires de mots de passe (ASVS 6.2.7)
- Pas de `oncopy="return false"` - Autorise le collage (ASVS 6.2.7)
- Messages flash pour afficher les erreurs/succès

### `templates/register.html`

**Rôle** : Page d'inscription

**Éléments Importants** :
- `minlength="8"` - Validation côté client pour 8 caractères minimum
- `autocomplete="new-password"` - Pour les gestionnaires de mots de passe
- Texte d'aide : "Minimum 8 caractères. Évitez les mots de passe courants"
- Validation côté serveur dans `app.py` (ligne 155-162)

### `templates/dashboard.html`

**Rôle** : Tableau de bord (page protégée)

**Éléments Importants** :
- Affiche le nom d'utilisateur : `{{ username }}`
- Liens vers modification du mot de passe et déconnexion
- Accessible uniquement si `session['user_id']` existe

### `templates/change_password.html`

**Rôle** : Page de modification du mot de passe

**Éléments Importants** :
- Demande le mot de passe actuel (ASVS 6.2.2)
- Mêmes règles de validation que l'inscription (ASVS 6.2.3)
- 3 champs : actuel, nouveau, confirmation

---

## Styles

### `static/style.css`

**Rôle** : Styles visuels de l'application

**Sections** :
- Reset CSS et styles de base
- Conteneur et carte (design moderne)
- Animations (slideIn, fadeIn)
- Alertes (succès, erreur, info)
- Formulaires (inputs, labels)
- Boutons (primaire, secondaire, danger)
- Tableau de bord
- Responsive design (media queries)
- Accessibilité (focus-visible)

**Design** :
- Gradient violet/bleu en arrière-plan
- Carte blanche centrée avec ombre
- Transitions douces sur les interactions
- Compatible mobile (max-width: 576px)

---

## Tests

### `tests/test_app.py`

**Rôle** : Tests automatisés pour vérifier la conformité OWASP ASVS

**15 Tests** :
1. **test_register_page_loads** : La page d'inscription se charge
2. **test_login_page_loads** : La page de connexion se charge
3. **test_register_password_too_short** : Rejet des mots de passe < 8 caractères (ASVS 6.2.1)
4. **test_register_common_password_rejected** : Rejet des mots de passe courants (ASVS 6.2.4)
5. **test_register_success** : Inscription valide fonctionne
6. **test_password_not_stored_plaintext** : Les mots de passe sont hachés (ASVS 6.2.1)
7. **test_login_with_correct_credentials** : Connexion valide fonctionne
8. **test_login_with_wrong_password** : Connexion invalide échoue
9. **test_rate_limiting** : Enregistrement des tentatives (ASVS 6.1.1, 6.3.1)
10. **test_dashboard_requires_authentication** : Dashboard protégé
11. **test_change_password_requires_current** : Demande l'ancien mot de passe (ASVS 6.2.2)
12. **test_change_password_validates_new** : Validation du nouveau mot de passe (ASVS 6.2.3)
13. **test_logout_invalidates_session** : Déconnexion invalide la session
14. **test_passwords_must_match** : Mot de passe et confirmation doivent correspondre
15. **test_username_unique** : Les noms d'utilisateur sont uniques

**Fixture** :
- Crée une base de données temporaire unique pour chaque test
- Initialise l'application en mode TEST
- Nettoie automatiquement après chaque test

---

## Données

### `common_passwords.txt`

**Rôle** : Liste de 3000+ mots de passe interdits (ASVS 6.2.4)

**Contenu** :
- Mots de passe les plus courants (password, 123456, qwerty, etc.)
- Mots du dictionnaire
- Noms communs, dates, lieux
- Variations courantes

**Utilisation** :
- Chargé au démarrage dans `COMMON_PASSWORDS` (ligne 60 app.py)
- Vérifié dans `is_password_common()` (ligne 93 app.py)
- Comparaison insensible à la casse

---

## Configuration

### `.env`

**Rôle** : Variables d'environnement (secrets)

**Contenu** :
```
SECRET_KEY=votre_cle_secrete_aleatoire_ici
```

**Sécurité** :
- **NE JAMAIS** commiter ce fichier
- Déjà dans `.gitignore`
- Générer avec : `python -c "import secrets; print(secrets.token_hex(32))"`

### `.env.example`

**Rôle** : Template pour créer `.env`

**Usage** :
```bash
cp .env.example .env
# Puis modifier .env avec une vraie clé
```

### `requirements.txt`

**Rôle** : Liste des dépendances Python

**Contenu** :
- `Flask==3.0.0` - Framework web
- `argon2-cffi==23.1.0` - Hachage de mots de passe
- `python-dotenv==1.0.0` - Chargement des variables d'environnement
- `pytest==7.4.3` - Framework de tests

**Installation** :
```bash
pip install -r requirements.txt
```

### `.gitignore`

**Rôle** : Fichiers à ne pas commiter sur Git

**Contenu** :
- `venv/` - Environnement virtuel
- `*.db` - Base de données
- `.env` - Secrets
- `__pycache__/` - Cache Python
- `.pytest_cache/` - Cache des tests

---

## Base de Données

### `users.db` (créé automatiquement)

**Rôle** : Base de données SQLite

**Tables** :

#### Table `users`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PRIMARY KEY | Identifiant unique |
| username | TEXT UNIQUE | Nom d'utilisateur |
| password_hash | TEXT | Hash Argon2id du mot de passe |
| created_at | TIMESTAMP | Date de création |

#### Table `login_attempts`
| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER PRIMARY KEY | Identifiant unique |
| username | TEXT | Nom d'utilisateur |
| ip_address | TEXT | Adresse IP |
| attempt_time | TIMESTAMP | Date/heure de la tentative |
| success | INTEGER | 1=succès, 0=échec |

**Création** :
- Automatique au premier lancement via `init_db()` (ligne 44 app.py)
- Schéma défini lignes 46-62 de `app.py`

---

## Documentation

### `README.md`

**Rôle** : Documentation complète du projet

**Sections** :
1. Présentation
2. Technologies utilisées
3. Installation et lancement
4. Fonctionnement de l'application
5. Sécurité implémentée
6. Conformité OWASP ASVS (tableau détaillé)
7. Tests
8. Règles de limitation
9. Bonnes pratiques
10. Références

### `GUIDE_DEMARRAGE.md`

**Rôle** : Guide rapide pour démarrer

**Contenu** :
- Commandes d'installation étape par étape
- Différentes méthodes de lancement
- Tests manuels
- Structure du projet
- Aide rapide

### `EXPLICATION_FICHIERS.md` (ce fichier)

**Rôle** : Explication détaillée de chaque fichier

---

## Scripts

### `run.bat`

**Rôle** : Script Windows pour lancer l'application facilement

**Contenu** :
```batch
@echo off
echo Demarrage de l'application...
venv\Scripts\python.exe app.py
pause
```

**Usage** : Double-clic dans l'explorateur Windows

---

## Résumé des Flux

### Flux d'Inscription
1. Utilisateur remplit le formulaire `/register`
2. POST vers `/register` (ligne 139 app.py)
3. Validation du mot de passe (ligne 155)
4. Hachage Argon2id (ligne 167)
5. Insertion dans la BD (ligne 170)
6. Redirection vers `/login`

### Flux de Connexion
1. Utilisateur remplit le formulaire `/login`
2. POST vers `/login` (ligne 179 app.py)
3. Vérification rate limiting (ligne 188)
4. Recherche utilisateur dans la BD (ligne 193)
5. Vérification du hash (ligne 200)
6. Création de session (ligne 211)
7. Enregistrement de la tentative (ligne 216)
8. Redirection vers `/dashboard`

### Flux de Modification de Mot de Passe
1. Utilisateur (connecté) va sur `/change-password`
2. POST vers `/change-password` (ligne 241 app.py)
3. Vérification du mot de passe actuel (ligne 261)
4. Validation du nouveau mot de passe (ligne 254)
5. Vérification que nouveau ≠ ancien (ligne 267)
6. Hachage et mise à jour (ligne 275)
7. Redirection vers `/dashboard`

---

## Points Clés pour le Professeur

### Sécurité
✅ **Aucun mot de passe en clair** - Toujours haché avec Argon2id  
✅ **Requêtes paramétrées** - Protection contre injection SQL  
✅ **Cookies HttpOnly/SameSite** - Protection XSS/CSRF  
✅ **Rate limiting** - Protection force brute  
✅ **Messages génériques** - Pas de fuite d'information  
✅ **Session invalidation** - Déconnexion propre  

### Conformité OWASP ASVS 5.0.0 Niveau 1
- **Chapitre V6 : Authentification** - 9 exigences implémentées
- **Code documenté** - Références ASVS dans les commentaires
- **Tests automatisés** - 15 tests couvrant les exigences
- **README détaillé** - Tableau de conformité complet

### Simplicité
- **Pas de complexité inutile** - Code clair et lisible
- **Architecture simple** - Un seul fichier Python principal
- **Commentaires en français** - Facile à comprendre
- **Fonctionnalités essentielles** - Niveau 1 seulement
