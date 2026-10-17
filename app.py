"""
Application Web d'authentification sécurisée
Conforme aux exigences OWASP ASVS 5.0.0 niveau 1
"""

import os
import sqlite3
import time
from functools import wraps
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

if not app.secret_key:
    raise ValueError("SECRET_KEY doit être définie dans le fichier .env")

# Configuration sécurisée des sessions (ASVS 6.1.2)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Protection contre XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protection contre CSRF
app.config['SESSION_COOKIE_SECURE'] = False  # Mettre à True en HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Initialisation du hasher Argon2id (ASVS 6.2.1)
ph = PasswordHasher()

# Constantes pour la limitation des tentatives (ASVS 6.1.1, 6.3.1)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes en secondes

# Base de données SQLite
DATABASE = 'users.db'

def get_db():
    """Obtenir la connexion à la base de données"""
    from flask import current_app
    db = getattr(g, '_database', None)
    if db is None:
        # Utiliser la base de données configurée ou la valeur par défaut
        database_path = current_app.config.get('DATABASE', DATABASE)
        db = g._database = sqlite3.connect(database_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Fermer la connexion à la base de données"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialiser la base de données avec les tables nécessaires"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour le suivi des tentatives de connexion (ASVS 6.3.1)
        db.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 0
            )
        ''')
        db.commit()

def load_common_passwords():
    """Charger la liste des mots de passe courants (ASVS 6.2.4)"""
    try:
        with open('common_passwords.txt', 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print("ATTENTION: Fichier common_passwords.txt non trouvé")
        return set()

COMMON_PASSWORDS = load_common_passwords()

def is_password_common(password):
    """Vérifier si le mot de passe est dans la liste des mots de passe courants"""
    return password.lower() in COMMON_PASSWORDS

def validate_password(password):
    """
    Valider le mot de passe selon les exigences OWASP ASVS
    - ASVS 6.2.1: Minimum 8 caractères
    - ASVS 6.2.4: Rejeter les mots de passe courants
    - ASVS 6.2.5: Ne pas imposer de caractères spéciaux obligatoires
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if is_password_common(password):
        errors.append("Ce mot de passe est trop courant. Veuillez en choisir un autre")
    
    return errors

def get_client_ip():
    """Obtenir l'adresse IP du client"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def check_rate_limit(username):
    """
    Vérifier la limitation des tentatives de connexion (ASVS 6.1.1, 6.3.1)
    Retourne True si la limite est atteinte, False sinon
    """
    from flask import current_app
    db = get_db()
    ip_address = get_client_ip()
    cutoff_time = datetime.now() - timedelta(seconds=LOCKOUT_DURATION)
    
    # Compter les tentatives échouées récentes pour ce compte
    cursor = db.execute('''
        SELECT COUNT(*) as count FROM login_attempts
        WHERE username = ? AND success = 0 AND attempt_time > ?
    ''', (username, cutoff_time))
    
    account_attempts = cursor.fetchone()['count']
    
    # Compter les tentatives échouées récentes pour cette IP
    cursor = db.execute('''
        SELECT COUNT(*) as count FROM login_attempts
        WHERE ip_address = ? AND success = 0 AND attempt_time > ?
    ''', (ip_address, cutoff_time))
    
    ip_attempts = cursor.fetchone()['count']
    
    return account_attempts >= MAX_LOGIN_ATTEMPTS or ip_attempts >= MAX_LOGIN_ATTEMPTS

def record_login_attempt(username, success):
    """Enregistrer une tentative de connexion"""
    db = get_db()
    ip_address = get_client_ip()
    db.execute('''
        INSERT INTO login_attempts (username, ip_address, success)
        VALUES (?, ?, ?)
    ''', (username, ip_address, 1 if success else 0))
    db.commit()

def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Page d'accueil - redirection vers le tableau de bord ou la connexion"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation des entrées
        if not username or not password:
            flash('Le nom d\'utilisateur et le mot de passe sont requis', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('register.html')
        
        # Validation du mot de passe (ASVS 6.2.1, 6.2.4, 6.2.5)
        errors = validate_password(password)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Vérifier si l'utilisateur existe déjà
        db = get_db()
        cursor = db.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Ce nom d\'utilisateur existe déjà', 'error')
            return render_template('register.html')
        
        # Hacher le mot de passe avec Argon2id (ASVS 6.2.1)
        password_hash = ph.hash(password)
        
        # Insérer le nouvel utilisateur (requête paramétrée contre les injections SQL)
        try:
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                      (username, password_hash))
            db.commit()
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Une erreur est survenue lors de l\'inscription', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Le nom d\'utilisateur et le mot de passe sont requis', 'error')
            return render_template('login.html')
        
        # Vérifier la limitation des tentatives AVANT de traiter la connexion (ASVS 6.1.1, 6.3.1)
        if check_rate_limit(username):
            flash(f'Trop de tentatives de connexion. Veuillez réessayer dans {LOCKOUT_DURATION // 60} minutes', 'error')
            return render_template('login.html')
        
        # Rechercher l'utilisateur dans la base de données
        db = get_db()
        cursor = db.execute('SELECT id, username, password_hash FROM users WHERE username = ?',
                          (username,))
        user = cursor.fetchone()
        
        # Vérifier le mot de passe de manière sécurisée
        login_success = False
        if user:
            try:
                ph.verify(user['password_hash'], password)
                login_success = True
                
                # Vérifier si le hash doit être mis à jour (rehashing automatique)
                if ph.check_needs_rehash(user['password_hash']):
                    new_hash = ph.hash(password)
                    db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                             (new_hash, user['id']))
                    db.commit()
                
                # Connexion réussie
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session.permanent = True
                
                record_login_attempt(username, success=True)
                
                flash(f'Bienvenue, {user["username"]} !', 'success')
                return redirect(url_for('dashboard'))
                
            except VerifyMismatchError:
                login_success = False
        
        # Échec de connexion (utilisateur non trouvé ou mot de passe incorrect)
        if not login_success:
            record_login_attempt(username, success=False)
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord - page protégée"""
    return render_template('dashboard.html', username=session['username'])

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Page de modification du mot de passe (ASVS 6.2.2, 6.2.3)"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_password or not new_password or not confirm_password:
            flash('Tous les champs sont requis', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'error')
            return render_template('change_password.html')
        
        # Validation du nouveau mot de passe
        errors = validate_password(new_password)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('change_password.html')
        
        # Vérifier le mot de passe actuel
        db = get_db()
        cursor = db.execute('SELECT password_hash FROM users WHERE id = ?',
                          (session['user_id'],))
        user = cursor.fetchone()
        
        try:
            ph.verify(user['password_hash'], current_password)
            
            # Vérifier que le nouveau mot de passe est différent
            try:
                ph.verify(user['password_hash'], new_password)
                flash('Le nouveau mot de passe doit être différent de l\'ancien', 'error')
                return render_template('change_password.html')
            except VerifyMismatchError:
                pass  # C'est bon, le nouveau mot de passe est différent
            
            # Hacher et enregistrer le nouveau mot de passe
            new_hash = ph.hash(new_password)
            db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                      (new_hash, session['user_id']))
            db.commit()
            
            flash('Mot de passe modifié avec succès', 'success')
            return redirect(url_for('dashboard'))
            
        except VerifyMismatchError:
            flash('Le mot de passe actuel est incorrect', 'error')
    
    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    """Déconnexion - invalider la session"""
    username = session.get('username', 'utilisateur')
    session.clear()  # Invalider complètement la session
    flash(f'Au revoir, {username} !', 'success')
    return redirect(url_for('login'))

# Gestionnaire d'erreur 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html'), 404

if __name__ == '__main__':
    # Initialiser la base de données au démarrage
    init_db()
    
    # Vérifier que nous avons bien la liste des mots de passe courants
    if len(COMMON_PASSWORDS) < 3000:
        print(f"ATTENTION: Seulement {len(COMMON_PASSWORDS)} mots de passe courants chargés")
        print("L'exigence ASVS 6.2.4 recommande au moins 3000 mots de passe")
    
    # NE PAS utiliser debug=True en production (risque de sécurité)
    # Pour le développement local uniquement
    app.run(debug=False, host='127.0.0.1', port=5000)
