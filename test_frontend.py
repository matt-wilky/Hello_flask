import pytest
from app import app, db, User

# Fixture to create a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.drop_all()

# Test for the splash page route
def test_splash_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Splash Page' in response.data  # Assuming 'Splash Page' is present in the template

# Test for the calendar route
def test_calendar(client):
    response = client.get('/calendar')
    assert response.status_code == 200

def test_register_page_loads(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'<h2>Register</h2>' in response.data

def test_register_valid_data(client):
    response = client.post('/register', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

def test_register_missing_data(client):
    response = client.post('/register', data={}, follow_redirects=True)
    assert response.status_code == 400
    assert b'Username and password are required' in response.data

def test_register_existing_username(client):
    # Create a user with the same username
    existing_user = User(username='test_user')
    existing_user.set_password('test_password')
    db.session.add(existing_user)
    
def test_login_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<form action="/login" method="post">' in response.data

def test_login_valid_credentials(client):
    # Register a user first
    client.post('/register', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)

    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Calendar' in response.data

def test_login_invalid_credentials(client):
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'wrong_password'
    }, follow_redirects=True)
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

def test_calendar_page_loads(client):
    response = client.get('/calendar')
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_add_event_page_unauthorized_access(client):
    response = client.get('/add_event', follow_redirects=True)
    assert response.status_code == 401

def test_login_missing_credentials(client):
    response = client.post('/login', data={}, follow_redirects=True)
    assert response.status_code == 401

def test_logout_redirect(client):
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/'
