import pytest
from app import app, db, User, New_Event
from datetime import datetime
# Fixture to create a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():  # Ensure teardown is within app context
            db.drop_all()

def test_registration(client):
    response = client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

# Test login functionality
def test_login(client):
    client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    response = client.post('/login', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert b'Calendar' in response.data

# Test logout functionality
def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

# Test adding an event
def test_add_event(client):
    # First, register and login a user
    client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    client.post('/login', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)

    # Then, add an event
    response = client.post('/add_event', data=dict(
        title='Test Event',
        start_time='2024-02-29T12:00',
        end_time='2024-02-29T13:00'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Calendar' in response.data

# Updated test for registration
def test_register(client):
    # Test registration with valid username and password
    response = client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data  # Assuming redirection to the splash page after successful registration

    # Test registration with missing username
    response = client.post('/register', data=dict(
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 400
    assert b'Username and password are required' in response.data  # Check for specific error message

    # Test registration with missing password
    response = client.post('/register', data=dict(
        username='test_user'
    ), follow_redirects=True)
    assert response.status_code == 400
    assert b'Username and password are required' in response.data  # Check for specific error message

    # Test registration with existing username (simulating database constraint violation)
    # Assuming you have a unique constraint on the username column in the User table
    existing_user = User(username='existing_user')
    existing_user.set_password('existing_password')
    db.session.add(existing_user)
    db.session.commit()
    response = client.post('/register', data=dict(
        username='existing_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 500  # Assuming the server returns 500 Internal Server Error for database constraint violation
    assert b'An error occurred' in response.data  # Check for generic error message

    # Clean up
    db.session.delete(existing_user)
    db.session.commit()

# New tests to cover missed lines
def test_unauthorized_access_to_calendar(client):
    response = client.get('/calendar', follow_redirects=True)
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_add_event_page(client):
    # Accessing add event page without logging in
    response = client.get('/add_event', follow_redirects=True)
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

# Test login with invalid credentials
def test_login_invalid_credentials(client):
    response = client.post('/login', data=dict(
        username='test_user',
        password='wrong_password'
    ), follow_redirects=True)
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_login_missing_credentials(client):
    # Test login with missing credentials
    response = client.post('/login', data=dict(), follow_redirects=True)
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data

def test_logout_redirect(client):
    # Test logout redirects to splash page
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/'

def test_edit_event(client):
    with app.app_context():
        # Create a test event
        test_event = New_Event(title='Test Event', start_time=datetime(2024, 2, 29, 12, 0), end_time=datetime(2024, 2, 29, 13, 0))
        db.session.add(test_event)
        db.session.commit()

        # Edit the event
        response = client.post(f'/edit_event/{test_event.id}', data=dict(
            title='Edited Event',
            start_time='2024-02-29T13:00',
            end_time='2024-02-29T14:00'
        ), follow_redirects=True)

        # Check if the event has been edited successfully
        assert response.status_code == 200
        assert b'Calendar' in response.data

        edited_event = New_Event.query.filter_by(id=test_event.id).first()
        assert edited_event.title == 'Edited Event'
        assert edited_event.start_time == datetime(2024, 2, 29, 13, 0)
        assert edited_event.end_time == datetime(2024, 2, 29, 14, 0)

def test_delete_event(client):
    with app.app_context():
        # Create a test event
        test_event = New_Event(title='Test Event', start_time=datetime(2024, 2, 29, 12, 0), end_time=datetime(2024, 2, 29, 13, 0))
        db.session.add(test_event)
        db.session.commit()

        # Delete the event
        response = client.post(f'/delete_event/{test_event.id}', follow_redirects=True)

        # Check if the event has been deleted successfully
        assert response.status_code == 200
        assert b'Calendar' in response.data

        deleted_event = New_Event.query.filter_by(id=test_event.id).first()
        assert deleted_event is None