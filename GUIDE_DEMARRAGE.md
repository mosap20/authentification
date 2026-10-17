# Guide de Démarrage Rapide

## Installation (À faire une seule fois)

### 1. Créer l'environnement virtuel
```bash
python -m venv venv
```

### 2. Activer l'environnement virtuel

**Sur Windows avec Git Bash ou WSL:**
```bash
source venv/Scripts/activate
```

**Sur Windows avec PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Sur Windows avec CMD:**
```cmd
venv\Scripts\activate.bat
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la clé secrète

Copier le fichier d'exemple :
```bash
cp .env.example .env
```

Générer une clé secrète :
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Ouvrir le fichier `.env` et remplacer `votre_cle_secrete_aleatoire_ici` par la clé générée.

## Lancer l'Application

### Méthode 1 : Double-clic sur run.bat (Windows)
Double-cliquez sur le fichier `run.bat` dans l'explorateur Windows.

### Méthode 2 : Ligne de commande
```bash
# Activer l'environnement virtuel d'abord
source venv/Scripts/activate

# Lancer l'application
python app.py
```

### Accéder à l'application
Ouvrez votre navigateur et allez à : **http://127.0.0.1:5000**

## Tester l'Application

### Tests Automatisés
```bash
pytest tests/test_app.py -v
```

### Test Manuel du Rate Limiting

1. Lancez l'application
2. Créez un compte utilisateur
3. Déconnectez-vous
4. Essayez de vous connecter avec un **mauvais mot de passe** 5 fois
5. À la 6ème tentative, vous devriez voir le message :  
   **"Trop de tentatives de connexion. Veuillez réessayer dans 5 minutes"**
6. Attendez 5 minutes ou redémarrez l'application pour débloquer

## Structure du Projet

```
TP1_OWASP/
├── app.py                      # Application Flask principale
├── templates/                  # Pages HTML
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── change_password.html
├── static/
│   └── style.css              # Styles CSS
├── tests/
│   └── test_app.py            # Tests automatisés
├── common_passwords.txt        # Liste de 3000+ mots de passe interdits
├── users.db                   # Base de données (créée automatiquement)
├── .env                       # Variables d'environnement (à créer)
├── requirements.txt           # Dépendances Python
├── run.bat                    # Script de lancement Windows
└── README.md                  # Documentation complète
```

## Fonctionnalités

✅ Inscription avec validation de mot de passe (8+ caractères)  
✅ Rejet des 3000+ mots de passe les plus courants  
✅ Hachage sécurisé avec Argon2id  
✅ Connexion sécurisée  
✅ Protection contre la force brute (5 tentatives / 5 minutes)  
✅ Tableau de bord protégé  
✅ Modification du mot de passe  
✅ Déconnexion sécurisée  
✅ Conforme OWASP ASVS 5.0.0 Niveau 1  

## Arrêter l'Application

Appuyez sur `Ctrl+C` dans le terminal où l'application est lancée.

## Aide

Pour plus d'informations, consultez le fichier `README.md` complet.
