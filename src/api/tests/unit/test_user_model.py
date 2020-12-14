import time
from datetime import datetime
import pytest
from app.models import User, Role, Permission
from tests import test_helpers


def test_password_setter(test_client):
    u = User(password='1234567890')
    assert u.password_hash is not None


def test_no_password_getter(test_client):
    u = User(password='cat')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification(test_client):
    u = User(password='cat')
    assert u.verify_password('cat')
    assert not u.verify_password('dog')


def test_password_salts_are_random(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    u2 = User(email='user2@example.com', username='user2', password='cat')
    assert u.password_hash != u2.password_hash


def test_valid_reset_token(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    test_db.session.add(u)
    test_db.session.commit()
    token = u.generate_reset_token()
    assert User.reset_password(token, 'dog')
    assert u.verify_password('dog')


def test_invalid_reset_token(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    test_db.session.add(u)
    test_db.session.commit()
    token = u.generate_reset_token()
    assert not (User.reset_password(token + 'a', 'horse'))
    assert u.verify_password('cat')


def test_valid_email_change_token(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    test_db.session.add(u)
    test_db.session.commit()
    token = u.generate_email_change_token('susan@example.org')
    assert u.change_email(token)
    assert u.email == 'susan@example.org'


def test_invalid_email_change_token(test_client, test_db):
    u1 = User(email='user1@example.com', username='user1', password='cat')
    u2 = User(email='user2@example.com', username='user2', password='cat')
    test_db.session.add(u1)
    test_db.session.add(u2)
    test_db.session.commit()
    token = u1.generate_email_change_token('david@example.net')
    assert not u2.change_email(token)
    assert u2.email == 'user2@example.com'


def test_duplicate_email_change_token(test_client, test_db):
    u1 = User(email='user1@example.com', username='user1', password='cat')
    u2 = User(email='user2@example.com', username='user2', password='cat')
    test_db.session.add(u1)
    test_db.session.add(u2)
    test_db.session.commit()
    token = u2.generate_email_change_token('user1@example.com')
    assert not u2.change_email(token)
    assert u2.email == 'user2@example.com'


def test_timestamps(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    test_db.session.add(u)
    test_db.session.commit()
    assert (datetime.utcnow() - u.created_at).total_seconds() < 3
    assert (datetime.utcnow() - u.last_seen_at).total_seconds() < 3


def test_ping(test_client, test_db):
    u = User(email='user1@example.com', username='user1', password='cat')
    test_db.session.add(u)
    test_db.session.commit()
    time.sleep(2)
    last_seen_before = u.last_seen_at
    updated_before = u.updated_at
    u.ping()
    test_db.session.commit()
    assert u.last_seen_at > last_seen_before
    assert u.updated_at == updated_before


def test_endpoint_no_update_ts(test_client, test_db):
    user = User.query.filter_by(username='admin').first()
    last_seen_before = user.last_seen_at
    updated_before = user.updated_at

    access_token = test_helpers.get_access_token(test_client)
    response = test_client.get('/secure', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200

    assert user.last_seen_at > last_seen_before
    assert user.updated_at == updated_before
