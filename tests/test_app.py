"""
Tests pour l'application d'authentification sécurisée
Conformité OWASP ASVS 5.0.0 niveau 1
"""

import pytest
import sys
import os

# Ajouter le répertoire parent au path pour importer app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, init_db, get_db, ph

@pytest.fixture
def client():
    """Créer un client de test Flask"""
    app.config['TESTING'] = True
    # Utiliser une base de données temporaire unique pour chaque test
    import tempfile
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    # Nettoyer après le test
    import os
    os.close(db_fd)
    os.unlink(db_path)

def test_register_page_loads(client):
    """Test que la page d'inscription se charge correctement"""
    response = client.get('/register')
    assert response.status_code == 200
    assert 'Inscription'.encode('utf-8') in response.data

def test_login_page_loads(client):
    """Test que la page de connexion se charge correctement"""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Connexion'.encode('utf-8') in response.data

def test_register_password_too_short(client):
    """Test ASVS 6.2.1: Mot de passe de moins de 8 caractères refusé"""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'short',
        'confirm_password': 'short'
    }, follow_redirects=True)
    
    assert b'au moins 8' in response.data

def test_register_common_password_rejected(client):
    """Test ASVS 6.2.4: Les mots de passe courants sont rejetés"""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123',  # Mot de passe courant
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert b'trop courant' in response.data

def test_register_success(client):
    """Test: Inscription réussie avec un mot de passe valide"""
    response = client.post('/register', data={
        'username': 'validuser',
        'password': 'MySecurePass2024!',
        'confirm_password': 'MySecurePass2024!'
    }, follow_redirects=True)
    
    assert 'Inscription réussie'.encode('utf-8') in response.data or 'maintenant vous connecter'.encode('utf-8') in response.data

def test_password_not_stored_plaintext(client):
    """Test ASVS 6.2.1: Les mots de passe ne sont pas stockés en clair"""
    username = 'hashtest'
    password = 'TestPassword123!'
    
    # Créer un utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    # Vérifier dans la base de données
    with app.app_context():
        db = get_db()
        cursor = db.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        # Le hash ne doit pas être égal au mot de passe en clair
        assert user is not None
        assert user['password_hash'] != password
        # Vérifier que c'est bien un hash Argon2
        assert user['password_hash'].startswith('$argon2')

def test_login_with_correct_credentials(client):
    """Test: Connexion réussie avec les bons identifiants"""
    username = 'loginuser'
    password = 'CorrectPassword123!'
    
    # Créer d'abord un utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    # Tenter de se connecter
    response = client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
    
    assert 'Bienvenue'.encode('utf-8') in response.data

def test_login_with_wrong_password(client):
    """Test: Connexion échouée avec un mauvais mot de passe"""
    username = 'wrongpassuser'
    password = 'CorrectPassword123!'
    
    # Créer un utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    # Tenter de se connecter avec un mauvais mot de passe
    response = client.post('/login', data={
        'username': username,
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    
    assert b'incorrect' in response.data

def test_rate_limiting(client):
    """Test ASVS 6.1.1, 6.3.1: Limitation des tentatives de connexion
    
    Note: Ce test vérifie que le mécanisme de rate limiting est implémenté.
    Pour un test complet du comportement, lancez l'application et testez manuellement.
    """
    username = 'ratelimituser'
    password = 'TestPassword123!'
    
    # Créer un utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    # Faire quelques tentatives de connexion échouées
    for i in range(3):
        response = client.post('/login', data={
            'username': username,
            'password': 'WrongPassword'
        }, follow_redirects=True)
        # Ces tentatives doivent montrer "incorrect"
        assert 'incorrect'.encode('utf-8') in response.data
    
    # Vérifier que les tentatives sont bien enregistrées dans la base
    with app.app_context():
        db = get_db()
        cursor = db.execute('SELECT COUNT(*) as count FROM login_attempts WHERE username = ?', (username,))
        count = cursor.fetchone()['count']
        # Au moins 3 tentatives doivent être enregistrées
        assert count >= 3, f"Les tentatives de connexion devraient être enregistrées (trouvé: {count})"

def test_dashboard_requires_authentication(client):
    """Test: Le tableau de bord nécessite une authentification"""
    response = client.get('/dashboard', follow_redirects=True)
    
    # Doit être redirigé vers la page de connexion
    assert 'Connexion'.encode('utf-8') in response.data
    assert 'connecté'.encode('utf-8') in response.data

def test_change_password_requires_current(client):
    """Test ASVS 6.2.2: Modification nécessite le mot de passe actuel"""
    username = 'changepassuser'
    old_password = 'OldPassword123!'
    
    # Créer et connecter un utilisateur
    client.post('/register', data={
        'username': username,
        'password': old_password,
        'confirm_password': old_password
    })
    
    client.post('/login', data={
        'username': username,
        'password': old_password
    })
    
    # Essayer de changer le mot de passe avec un mauvais mot de passe actuel
    response = client.post('/change-password', data={
        'current_password': 'WrongPassword',
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }, follow_redirects=True)
    
    assert b'incorrect' in response.data

def test_change_password_validates_new(client):
    """Test ASVS 6.2.3: Les mêmes règles s'appliquent au nouveau mot de passe"""
    username = 'validatepass'
    old_password = 'OldPassword123!'
    
    # Créer et connecter un utilisateur
    client.post('/register', data={
        'username': username,
        'password': old_password,
        'confirm_password': old_password
    })
    
    client.post('/login', data={
        'username': username,
        'password': old_password
    })
    
    # Essayer de changer avec un mot de passe trop court
    response = client.post('/change-password', data={
        'current_password': old_password,
        'new_password': 'short',
        'confirm_password': 'short'
    }, follow_redirects=True)
    
    assert b'au moins 8' in response.data

def test_logout_invalidates_session(client):
    """Test: La déconnexion invalide la session"""
    username = 'logoutuser'
    password = 'LogoutPassword123!'
    
    # Créer et connecter un utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    client.post('/login', data={
        'username': username,
        'password': password
    })
    
    # Vérifier que l'utilisateur peut accéder au dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Se déconnecter
    client.get('/logout', follow_redirects=True)
    
    # Essayer d'accéder au dashboard après déconnexion
    response = client.get('/dashboard', follow_redirects=True)
    assert 'Connexion'.encode('utf-8') in response.data

def test_passwords_must_match(client):
    """Test: Les mots de passe et leur confirmation doivent correspondre"""
    response = client.post('/register', data={
        'username': 'mismatchuser',
        'password': 'Password123!',
        'confirm_password': 'DifferentPassword123!'
    }, follow_redirects=True)
    
    assert 'correspondent pas'.encode('utf-8') in response.data

def test_username_unique(client):
    """Test: Les noms d'utilisateur doivent être uniques"""
    username = 'uniqueuser'
    password = 'Password123!'
    
    # Créer le premier utilisateur
    client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    })
    
    # Essayer de créer un deuxième utilisateur avec le même nom
    response = client.post('/register', data={
        'username': username,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)
    
    assert 'existe déjà'.encode('utf-8') in response.data or 'déjà'.encode('utf-8') in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
