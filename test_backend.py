# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from app import app, db, User, New_Event
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_registration(client):
    response = client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

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

def test_logout(client):
    response = client.post('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

def test_add_event(client):
    client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    client.post('/login', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    response = client.post('/add_event', data=dict(
        title='Test Event',
        start_time='2024-02-29T12:00',
        end_time='2024-02-29T13:00'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Calendar' in response.data

def test_register(client):
    response = client.post('/register', data=dict(
        username='test_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Splash Page' in response.data

    response = client.post('/register', data=dict(
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 400
    assert b'Username and password are required' in response.data

    response = client.post('/register', data=dict(
        username='test_user'
    ), follow_redirects=True)
    assert response.status_code == 400
    assert b'Username and password are required' in response.data

    # Ensure registering with existing username fails
    existing_user = User(username='existing_user')
    existing_user.set_password('existing_password')
    db.session.add(existing_user)
    db.session.commit()
    response = client.post('/register', data=dict(
        username='existing_user',
        password='test_password'
    ), follow_redirects=True)
    assert response.status_code == 500
    assert b'An error occurred' in response.data
    db.session.delete(existing_user)
    db.session.commit()

def test_unauthorized_access_to_calendar(client):
    response = client.get('/calendar', follow_redirects=True)
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_edit_event(client):
    with app.app_context():
        test_user = User(username='test_user')
        test_user.set_password('test_password')
        db.session.add(test_user)
        db.session.commit()

        client.post('/login', data=dict(
            username='test_user',
            password='test_password'
        ), follow_redirects=True)

        test_event = New_Event(
            title='Test Event',
            start_time=datetime(2024, 2, 29, 12, 0),
            end_time=datetime(2024, 2, 29, 13, 0),
            user_id=test_user.id
        )
        db.session.add(test_event)
        db.session.commit()

        response = client.post(f'/edit_event/{test_event.id}', data=dict(
            title='Updated Event',
            start_time='2024-02-29T12:00',
            end_time='2024-02-29T14:00'
        ), follow_redirects=True)

        assert response.status_code == 200
        assert b'Calendar' in response.data

        updated_event = New_Event.query.filter_by(id=test_event.id).first()
        assert updated_event.title == 'Updated Event'
        assert updated_event.start_time == datetime(2024, 2, 29, 12, 0)
        assert updated_event.end_time == datetime(2024, 2, 29, 14, 0)

def test_delete_event(client):
    with app.app_context():
        test_user = User(username='test_user')
        test_user.set_password('test_password')
        db.session.add(test_user)
        db.session.commit()

        client.post('/login', data=dict(
            username='test_user',
            password='test_password'
        ), follow_redirects=True)

        test_event = New_Event(
            title='Test Event',
            start_time=datetime(2024, 2, 29, 12, 0),
            end_time=datetime(2024, 2, 29, 13, 0),
            user_id=test_user.id
        )
        db.session.add(test_event)
        db.session.commit()

        response = client.post(f'/delete_event/{test_event.id}', follow_redirects=True)

        assert response.status_code == 200
        assert b'Calendar' in response.data

        deleted_event = New_Event.query.filter_by(id=test_event.id).first()
        assert deleted_event is None
