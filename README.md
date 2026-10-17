# TP1 : Authentification Sécurisée (OWASP ASVS)

Application Web d'authentification sécurisée développée dans le cadre du module « Sécurité des applications et des services » - IRISI 3, FST Marrakech.

## 📋 Présentation du Projet

Cette application Web démontre l'implémentation d'un système d'authentification conforme aux exigences du **niveau 1 de l'OWASP ASVS 5.0.0** (Application Security Verification Standard), particulièrement le chapitre V6 sur l'authentification.

L'application permet aux utilisateurs de :
- Créer un compte avec des règles de mot de passe sécurisées
- Se connecter avec protection contre la force brute
- Accéder à une page protégée (tableau de bord)
- Modifier leur mot de passe de manière sécurisée
- Se déconnecter avec invalidation complète de la session

## 🛠 Technologies Utilisées

- **Backend** : Python 3.x avec Flask 3.0.0
- **Base de données** : SQLite 3
- **Hachage de mots de passe** : Argon2id (via argon2-cffi)
- **Frontend** : HTML5, CSS3 (sans framework JavaScript)
- **Gestion des sessions** : Flask-Session intégré
- **Tests** : Pytest

## 📦 Installation et Lancement

### Prérequis

- Python 3.8 ou supérieur installé
- pip (gestionnaire de packages Python)

### Installation sur Windows avec VS Code

1. **Cloner ou télécharger le projet**
   ```bash
   cd TP1_OWASP
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement virtuel**
   ```bash
   # Sur Windows avec bash
   source venv/Scripts/activate
   
   # Sur Windows avec PowerShell
   venv\Scripts\Activate.ps1
   
   # Sur Windows avec CMD
   venv\Scripts\activate.bat
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurer les variables d'environnement**
   ```bash
   # Copier le fichier exemple
   cp .env.example .env
   
   # Générer une clé secrète
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   
   Copiez la clé générée et remplacez `votre_cle_secrete_aleatoire_ici` dans le fichier `.env`

6. **Lancer l'application**
   ```bash
   python app.py
   ```

7. **Accéder à l'application**
   
   Ouvrez votre navigateur et allez à : `http://127.0.0.1:5000`

### Exécution des Tests

```bash
# S'assurer d'être dans le dossier TP1_OWASP avec l'environnement activé
pytest tests/test_app.py -v
```

## 🔐 Fonctionnement de l'Application

### Architecture

L'application suit une architecture simple :
```
TP1_OWASP/
├── app.py                    # Application Flask principale
├── templates/                # Templates HTML
│   ├── login.html           # Page de connexion
│   ├── register.html        # Page d'inscription
│   ├── dashboard.html       # Tableau de bord (protégé)
│   └── change_password.html # Modification du mot de passe
├── static/
│   └── style.css            # Styles CSS
├── tests/
│   └── test_app.py          # Tests automatisés
├── common_passwords.txt      # Liste de mots de passe interdits
├── users.db                 # Base de données (créée automatiquement)
└── requirements.txt         # Dépendances Python
```

### Flux d'Authentification

1. **Inscription** :
   - L'utilisateur soumet un nom d'utilisateur et un mot de passe
   - Le mot de passe est validé (longueur ≥ 8, pas dans la liste des mots de passe courants)
   - Le mot de passe est haché avec Argon2id
   - L'utilisateur est enregistré dans la base de données

2. **Connexion** :
   - L'utilisateur soumet ses identifiants
   - Vérification de la limitation des tentatives (max 5 en 5 minutes)
   - Vérification sécurisée du mot de passe haché
   - Création d'une session sécurisée

3. **Accès aux pages protégées** :
   - Vérification de la présence d'une session valide
   - Redirection vers la connexion si non authentifié

4. **Modification du mot de passe** :
   - Vérification du mot de passe actuel
   - Validation du nouveau mot de passe (mêmes règles)
   - Mise à jour du hash dans la base de données

5. **Déconnexion** :
   - Invalidation complète de la session
   - Redirection vers la page de connexion

### Sécurité Implémentée

#### Protection contre les Injections SQL
- Toutes les requêtes utilisent des **requêtes paramétrées**
- Exemple : `db.execute('SELECT * FROM users WHERE username = ?', (username,))`

#### Hachage Sécurisé des Mots de Passe
- Utilisation d'**Argon2id**, recommandé par l'OWASP
- Hachage automatique avant stockage
- Rehashing automatique si les paramètres changent

#### Protection contre la Force Brute
- Limitation à **5 tentatives de connexion par période de 5 minutes**
- Suivi par nom d'utilisateur ET par adresse IP
- Empêche le blocage définitif du compte d'une victime

#### Configuration Sécurisée des Sessions
- `HttpOnly=True` : Protection contre le vol de session par XSS
- `SameSite=Lax` : Protection contre CSRF
- `Secure=False` : À mettre à True en HTTPS
- Durée de session limitée à 1 heure

#### Protection CSRF
- Protection intégrée de Flask pour les formulaires POST
- Validation automatique des tokens

## 📊 Conformité OWASP ASVS 5.0.0 Niveau 1

### Chapitre V6 : Authentification

| ID ASVS | Exigence | Implémentation | Vérification |
|---------|----------|----------------|--------------|
| **6.1.1** | Protection contre les attaques par force brute | Limitation à 5 tentatives en 5 minutes par compte et par IP (`check_rate_limit()` dans `app.py`) | Test : `test_rate_limiting()` - Faire 6 tentatives échouées |
| **6.1.2** | Utilisation d'une bibliothèque de session standard | Flask-Session intégré avec configuration sécurisée (lignes 23-26 dans `app.py`) | Vérifier `app.config['SESSION_COOKIE_*']` |
| **6.2.1** | Mots de passe d'au moins 8 caractères + hachage adapté (Argon2id) | Validation dans `validate_password()` + `PasswordHasher` (lignes 70-85, 30 dans `app.py`) | Test : `test_register_password_too_short()` et `test_password_not_stored_plaintext()` |
| **6.2.2** | Demander le mot de passe actuel pour le modifier | Vérification dans `/change-password` (lignes 258-276 dans `app.py`) | Test : `test_change_password_requires_current()` |
| **6.2.3** | Validation du nouveau mot de passe | Même fonction `validate_password()` pour inscription et modification (ligne 234 dans `app.py`) | Test : `test_change_password_validates_new()` |
| **6.2.4** | Rejeter les 3000+ mots de passe les plus courants | Liste de 3000+ mots de passe dans `common_passwords.txt`, vérification dans `is_password_common()` (lignes 62-67 dans `app.py`) | Test : `test_register_common_password_rejected()` |
| **6.2.5** | Ne pas imposer obligatoirement des caractères spéciaux | Pas de validation de complexité forcée, seulement longueur minimale (ligne 74-78 dans `app.py`) | Tester avec un mot de passe comme "monmotdepasse2024" (sans caractères spéciaux) |
| **6.2.6** | Masquer le mot de passe à l'écran | `type="password"` dans tous les formulaires HTML | Inspecter `login.html`, `register.html`, `change_password.html` (ligne 33, 34, 15) |
| **6.2.7** | Autoriser le collage et les gestionnaires de mots de passe | Pas de `oncopy="return false"` ni de JavaScript bloquant, attribut `autocomplete` présent | Tester le collage dans les champs de mot de passe |
| **6.3.1** | Limitation intelligente sans permettre de bloquer le compte d'une victime | Limitation par IP ET par compte, timeout de 5 minutes (pas de blocage permanent) (lignes 95-117 dans `app.py`) | Test : `test_rate_limiting()` + attendre 5 minutes pour vérifier le déblocage |

### Autres Exigences de Sécurité Implémentées

| Domaine | Pratique Implémentée | Localisation |
|---------|---------------------|--------------|
| **Injections SQL** | Requêtes paramétrées uniquement | Toutes les requêtes SQL dans `app.py` utilisent `?` |
| **Gestion des sessions** | Invalidation complète à la déconnexion | `session.clear()` dans `/logout` (ligne 288) |
| **Messages d'erreur** | Messages génériques sans fuite d'information | Même message "incorrect" pour utilisateur inexistant et mauvais mot de passe (ligne 232) |
| **Protection XSS** | `HttpOnly=True` pour les cookies | Configuration Flask ligne 24 |
| **Protection CSRF** | `SameSite=Lax` pour les cookies | Configuration Flask ligne 25 |
| **Stockage sécurisé** | Aucun mot de passe en clair | Hachage Argon2id avant insertion (ligne 167) |
| **Configuration sécurisée** | Clé secrète depuis variable d'environnement | `.env` chargé ligne 18, vérification ligne 21 |

### Limitations et Hors Scope pour Niveau 1

Les fonctionnalités suivantes ne sont **pas** requises pour le niveau 1 de l'OWASP ASVS et n'ont donc **pas été implémentées** :

- ❌ Authentification multi-facteurs (MFA) - Requis au niveau 2
- ❌ Récupération de compte par email - Requis au niveau 2
- ❌ Historique des mots de passe - Requis au niveau 2
- ❌ Notification des changements de mot de passe - Requis au niveau 2
- ❌ Authentification biométrique - Requis au niveau 3
- ❌ Jetons de session cryptographiquement forts - Niveau 2
- ❌ Gestion avancée des sessions (détection de sessions multiples) - Niveau 2

## 🧪 Description des Tests

| Test | Objectif | Exigence ASVS |
|------|----------|---------------|
| `test_register_password_too_short` | Vérifier que les mots de passe < 8 caractères sont rejetés | 6.2.1 |
| `test_register_common_password_rejected` | Vérifier que les mots de passe courants sont rejetés | 6.2.4 |
| `test_register_success` | Vérifier qu'un mot de passe valide permet l'inscription | - |
| `test_password_not_stored_plaintext` | Vérifier que les mots de passe sont hachés | 6.2.1 |
| `test_login_with_correct_credentials` | Vérifier qu'une connexion valide fonctionne | - |
| `test_login_with_wrong_password` | Vérifier qu'un mauvais mot de passe échoue | - |
| `test_rate_limiting` | Vérifier la limitation à 5 tentatives | 6.1.1, 6.3.1 |
| `test_dashboard_requires_authentication` | Vérifier que les pages protégées nécessitent une authentification | - |
| `test_change_password_requires_current` | Vérifier qu'on doit fournir l'ancien mot de passe | 6.2.2 |
| `test_change_password_validates_new` | Vérifier que les mêmes règles s'appliquent au nouveau mot de passe | 6.2.3 |
| `test_logout_invalidates_session` | Vérifier que la déconnexion invalide la session | - |
| `test_passwords_must_match` | Vérifier que mot de passe et confirmation doivent correspondre | - |
| `test_username_unique` | Vérifier que les noms d'utilisateur sont uniques | - |

## 📝 Règles de Limitation des Tentatives

**Configuration actuelle** :
- **Limite** : 5 tentatives de connexion échouées
- **Période** : 5 minutes
- **Suivi** : Par nom d'utilisateur ET par adresse IP
- **Comportement** : Blocage temporaire (pas de blocage permanent du compte)

**Justification** :
- Empêche les attaques par force brute
- Ne permet pas à un attaquant de bloquer définitivement le compte d'une victime
- Balance entre sécurité et utilisabilité

**Documentation dans le code** : Voir constantes `MAX_LOGIN_ATTEMPTS` et `LOCKOUT_DURATION` (lignes 28-29 dans `app.py`)

## 🔒 Bonnes Pratiques de Sécurité

### Pour le Développement
1. **Ne jamais** utiliser `debug=True` en production
2. **Toujours** générer une clé secrète forte et aléatoire
3. **Toujours** utiliser HTTPS en production (mettre `SESSION_COOKIE_SECURE=True`)
4. **Ne jamais** commiter le fichier `.env` (déjà dans `.gitignore`)

### Pour le Déploiement
1. Utiliser un serveur WSGI (Gunicorn, uWSGI) au lieu du serveur de développement Flask
2. Activer HTTPS avec un certificat valide
3. Configurer les en-têtes de sécurité (CSP, HSTS, X-Frame-Options)
4. Utiliser une base de données plus robuste (PostgreSQL, MySQL)
5. Mettre en place une surveillance des logs

## 📚 Références

- [OWASP ASVS 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Flask Security Documentation](https://flask.palletsprojects.com/en/3.0.x/security/)
- [Argon2 Documentation](https://argon2-cffi.readthedocs.io/)

## 👨‍🎓 Auteur

Projet réalisé dans le cadre du TP1 du module « Sécurité des applications et des services »  
IRISI 3 - FST Marrakech

## 📄 Licence

Projet éducatif - Usage académique uniquement
