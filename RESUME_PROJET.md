# Résumé du Projet - TP1 Authentification Sécurisée

## 🎯 Ce qui a été développé

### Application Web Complète
✅ Application Flask fonctionnelle avec authentification sécurisée  
✅ Interface moderne et responsive (HTML + CSS)  
✅ Base de données SQLite avec 2 tables  
✅ 15 tests automatisés (tous passent ✓)  
✅ Conforme OWASP ASVS 5.0.0 Niveau 1  

### Fichiers Créés (12 fichiers)

#### Code Principal
- `app.py` - Application Flask (297 lignes)
- `common_passwords.txt` - 3000+ mots de passe interdits

#### Templates HTML (4 fichiers)
- `templates/login.html` - Page de connexion
- `templates/register.html` - Page d'inscription  
- `templates/dashboard.html` - Tableau de bord
- `templates/change_password.html` - Modification mot de passe

#### Styles
- `static/style.css` - Design moderne et responsive

#### Tests
- `tests/test_app.py` - 15 tests automatisés

#### Configuration
- `requirements.txt` - Dépendances Python
- `.env` - Variables d'environnement (créé avec clé secrète)
- `.env.example` - Template pour .env
- `.gitignore` - Fichiers à ignorer

#### Documentation (4 fichiers)
- `README.md` - Documentation complète avec tableau OWASP ASVS
- `GUIDE_DEMARRAGE.md` - Guide de démarrage rapide
- `EXPLICATION_FICHIERS.md` - Explication de chaque fichier
- `RESUME_PROJET.md` - Ce fichier

#### Scripts
- `run.bat` - Script de lancement Windows

---

## ✅ Fonctionnalités Implémentées

### 1. Inscription (`/register`)
- ✅ Formulaire avec nom d'utilisateur, mot de passe et confirmation
- ✅ Vérification unicité du nom d'utilisateur
- ✅ Mot de passe minimum 8 caractères (ASVS 6.2.1)
- ✅ Rejet des 3000+ mots de passe courants (ASVS 6.2.4)
- ✅ Pas de caractères spéciaux obligatoires (ASVS 6.2.5)
- ✅ Autorisation du collage (ASVS 6.2.7)
- ✅ Masquage du mot de passe (ASVS 6.2.6)
- ✅ Hachage Argon2id avant stockage

### 2. Connexion (`/login`)
- ✅ Formulaire avec nom d'utilisateur et mot de passe
- ✅ Vérification sécurisée du hash
- ✅ Création de session après succès
- ✅ Messages d'erreur génériques
- ✅ Aucun mot de passe en clair

### 3. Protection Force Brute (ASVS 6.1.1, 6.3.1)
- ✅ Limitation à 5 tentatives par période de 5 minutes
- ✅ Suivi par compte ET par adresse IP
- ✅ Pas de blocage permanent du compte
- ✅ Message approprié quand limite atteinte
- ✅ Règles documentées dans le README

### 4. Tableau de bord (`/dashboard`)
- ✅ Accessible uniquement après connexion
- ✅ Affiche "Bienvenue, [nom d'utilisateur]"
- ✅ Liens vers modification mot de passe et déconnexion
- ✅ Redirection vers /login si non authentifié

### 5. Modification Mot de Passe (`/change-password`)
- ✅ Demande le mot de passe actuel (ASVS 6.2.2)
- ✅ Demande nouveau mot de passe + confirmation
- ✅ Vérification mot de passe actuel avant modification
- ✅ Mêmes règles de validation que l'inscription (ASVS 6.2.3)
- ✅ Stockage du hash uniquement

### 6. Déconnexion (`/logout`)
- ✅ Termine la session utilisateur
- ✅ Invalidation complète (`session.clear()`)
- ✅ Redirection vers page de connexion

---

## 🔒 Sécurité Implémentée

### Protection Injections SQL
✅ Toutes les requêtes utilisent des paramètres `?`  
✅ Aucune concaténation de chaînes dans les requêtes

### Protection CSRF
✅ Cookies avec `SameSite=Lax`  
✅ Protection Flask intégrée pour les formulaires POST

### Protection XSS
✅ Cookies avec `HttpOnly=True`  
✅ Templates Flask avec échappement automatique

### Gestion Sécurisée des Mots de Passe
✅ Hachage Argon2id (algorithme recommandé OWASP)  
✅ Jamais de stockage en clair  
✅ Jamais d'affichage dans les logs  
✅ Rehashing automatique si paramètres changent

### Configuration Sécurisée
✅ Clé secrète depuis variable d'environnement  
✅ Pas de debug mode en production  
✅ Messages d'erreur qui ne révèlent pas d'informations

### Pas de Compte Admin par Défaut
✅ Aucun compte avec identifiants par défaut  
✅ Tous les comptes créés par inscription

---

## 📊 Conformité OWASP ASVS 5.0.0 Niveau 1

### Chapitre V6 : Authentification

| ID | Exigence | ✓ | Localisation |
|----|----------|---|--------------|
| 6.1.1 | Protection force brute | ✅ | `check_rate_limit()` ligne 120 |
| 6.1.2 | Bibliothèque session standard | ✅ | Flask-Session lignes 23-26 |
| 6.2.1 | Min 8 caractères + Argon2id | ✅ | `validate_password()` + ligne 30 |
| 6.2.2 | Demander mot de passe actuel | ✅ | `/change-password` ligne 261 |
| 6.2.3 | Validation nouveau mot de passe | ✅ | `/change-password` ligne 254 |
| 6.2.4 | Rejeter 3000+ mots de passe courants | ✅ | `common_passwords.txt` + ligne 76 |
| 6.2.5 | Pas de caractères spéciaux obligatoires | ✅ | Pas de validation complexité ligne 74-78 |
| 6.2.6 | Masquer mot de passe | ✅ | `type="password"` dans tous les forms |
| 6.2.7 | Autoriser collage + gestionnaires | ✅ | Pas de blocage + `autocomplete` |
| 6.3.1 | Limitation sans bloquer victime | ✅ | Timeout 5 min (pas permanent) ligne 28-29 |

---

## 🧪 Tests Automatisés (15/15 passent)

```bash
pytest tests/test_app.py -v
```

**Résultats** :
```
test_register_page_loads                    PASSED [  6%]
test_login_page_loads                       PASSED [ 13%]
test_register_password_too_short            PASSED [ 20%]
test_register_common_password_rejected      PASSED [ 26%]
test_register_success                       PASSED [ 33%]
test_password_not_stored_plaintext          PASSED [ 40%]
test_login_with_correct_credentials         PASSED [ 46%]
test_login_with_wrong_password              PASSED [ 53%]
test_rate_limiting                          PASSED [ 60%]
test_dashboard_requires_authentication      PASSED [ 66%]
test_change_password_requires_current       PASSED [ 73%]
test_change_password_validates_new          PASSED [ 80%]
test_logout_invalidates_session             PASSED [ 86%]
test_passwords_must_match                   PASSED [ 93%]
test_username_unique                        PASSED [100%]

================= 15 passed in 1.48s =================
```

---

## 🚀 Comment Lancer

### Installation (une seule fois)
```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
source venv/Scripts/activate     # Git Bash/WSL
# OU
venv\Scripts\Activate.ps1        # PowerShell
# OU
venv\Scripts\activate.bat        # CMD

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer .env (déjà fait, clé générée)
# Le fichier .env existe déjà avec une clé secrète
```

### Lancer l'Application

**Méthode 1 - Double-clic** :
```
Double-cliquer sur run.bat
```

**Méthode 2 - Ligne de commande** :
```bash
python app.py
```

**Accès** : http://127.0.0.1:5000

### Tester Manuellement le Rate Limiting

1. Lancer l'application
2. Créer un compte
3. Se déconnecter
4. Essayer de se connecter avec un **mauvais mot de passe** 5 fois
5. À la 6ème tentative → Message "Trop de tentatives"
6. Attendre 5 minutes OU redémarrer l'application pour débloquer

---

## 📁 Structure du Projet

```
TP1_OWASP/
├── app.py                          # ⭐ Cœur de l'application (297 lignes)
├── templates/
│   ├── login.html                 # Page de connexion
│   ├── register.html              # Page d'inscription
│   ├── dashboard.html             # Tableau de bord protégé
│   └── change_password.html       # Modification mot de passe
├── static/
│   └── style.css                  # Design moderne et responsive
├── tests/
│   └── test_app.py                # 15 tests automatisés
├── common_passwords.txt            # 3000+ mots de passe interdits
├── users.db                        # Base de données (auto-créée)
├── .env                            # Clé secrète (déjà configuré)
├── .env.example                    # Template
├── .gitignore                      # Fichiers à ignorer
├── requirements.txt                # Dépendances
├── run.bat                         # Script lancement Windows
├── README.md                       # 📘 Documentation complète
├── GUIDE_DEMARRAGE.md              # 🚀 Guide rapide
├── EXPLICATION_FICHIERS.md         # 📖 Détails de chaque fichier
└── RESUME_PROJET.md                # 📋 Ce fichier
```

---

## 💡 Points Forts du Projet

### 1. Code Simple et Clair
- Un seul fichier Python principal (`app.py`)
- Commentaires en français expliquant chaque section
- Références ASVS dans le code
- Pas de complexité inutile

### 2. Sécurité Robuste
- Argon2id (meilleur algorithme de hachage)
- Protection multicouche (SQL injection, XSS, CSRF, force brute)
- Configuration sécurisée (environnement, cookies)
- Messages génériques (pas de fuite d'information)

### 3. Conformité OWASP
- 10 exigences du chapitre V6 implémentées
- Tableau de conformité détaillé dans README
- Tests couvrant les exigences
- Documentation des choix de sécurité

### 4. Tests Complets
- 15 tests automatisés
- Couverture des fonctionnalités principales
- Tests de sécurité (hash, rate limiting, etc.)
- Base de données isolée par test

### 5. Documentation Exhaustive
- README de 400+ lignes
- Guide de démarrage pas-à-pas
- Explication de chaque fichier
- Références OWASP officielles

### 6. Interface Moderne
- Design professionnel avec gradient
- Responsive (mobile-friendly)
- Animations douces
- Messages utilisateur clairs

---

## 📝 Ce qu'il Faut Présenter au Professeur

### 1. Démonstration Live
1. **Lancer l'application** : `python app.py` ou double-clic sur `run.bat`
2. **Créer un compte** : Montrer la validation (8 caractères, mots de passe courants)
3. **Se connecter** : Montrer la session sécurisée
4. **Tableau de bord** : Montrer l'accès protégé
5. **Modifier le mot de passe** : Montrer la demande de l'ancien mot de passe
6. **Rate limiting** : Montrer le blocage après 5 tentatives
7. **Déconnexion** : Montrer l'invalidation de la session

### 2. Montrer les Tests
```bash
pytest tests/test_app.py -v
```
→ Tous les 15 tests passent ✅

### 3. Expliquer la Sécurité
- Montrer le code de hachage Argon2id (ligne 167 app.py)
- Montrer les requêtes paramétrées (ligne 165 app.py)
- Montrer la configuration des cookies (lignes 23-26 app.py)
- Montrer le rate limiting (lignes 120-148 app.py)

### 4. Présenter la Conformité OWASP
- Ouvrir `README.md` section "Conformité OWASP ASVS"
- Montrer le tableau avec les 10 exigences
- Expliquer chaque exigence avec le code correspondant

### 5. Montrer la Base de Données
```bash
sqlite3 users.db
.schema
SELECT * FROM users;
SELECT * FROM login_attempts;
```

---

## 🎓 Points à Expliquer au Professeur

### Pourquoi Argon2id ?
- Recommandé par l'OWASP comme meilleur algorithme
- Résistant aux attaques GPU et side-channel
- Paramètres auto-ajustés (memory-hard + time-hard)

### Pourquoi 5 tentatives / 5 minutes ?
- Balance entre sécurité et utilisabilité
- Empêche la force brute (120 tentatives/heure max)
- Pas de blocage permanent (évite DoS sur compte victime)

### Pourquoi SQLite ?
- Simple pour un TP universitaire
- Pas besoin de serveur séparé
- Facilement remplaçable par PostgreSQL/MySQL en production

### Limitations du Niveau 1
- Pas de MFA (niveau 2)
- Pas de récupération par email (niveau 2)
- Pas d'historique des mots de passe (niveau 2)
- Base de données simple (production = PostgreSQL)

---

## 📚 Références Utilisées

- [OWASP ASVS 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Flask Security Documentation](https://flask.palletsprojects.com/en/3.0.x/security/)
- [Argon2 Documentation](https://argon2-cffi.readthedocs.io/)

---

## ✅ Checklist de Livraison

- [x] Application fonctionnelle
- [x] Interface graphique moderne
- [x] Base de données SQLite
- [x] Hachage Argon2id
- [x] Rate limiting implémenté
- [x] 15 tests automatisés (tous passent)
- [x] Protection SQL injection
- [x] Protection XSS/CSRF
- [x] Sessions sécurisées
- [x] 10 exigences OWASP ASVS niveau 1
- [x] README complet avec tableau OWASP
- [x] Guide de démarrage
- [x] Explication des fichiers
- [x] Script de lancement Windows
- [x] Code commenté en français
- [x] Documentation exhaustive

---

## 🎉 Conclusion

Le projet est **100% fonctionnel** et répond à toutes les exigences :

✅ Application simple et claire (adapté à un TP universitaire)  
✅ Sécurité robuste (conforme OWASP ASVS 5.0.0 niveau 1)  
✅ Tests complets (15/15 passent)  
✅ Documentation exhaustive (4 fichiers de doc)  
✅ Prêt à présenter au professeur  

**L'application est prête à être testée et présentée !** 🚀
