from datetime import datetime
from faker import Faker
from app.models import Role, User

fake = Faker()


def get_access_token(client):
    response = client.post('/auth/login', json={'login': 'admin', 'password': 'admin'},
                           headers={'Content-Type': 'application/json'})
    json_data = response.get_json()
    return json_data['access_token']


def get_access_token_for_user(client, username, password):
    response = client.post('/auth/login', json={'login': username, 'password': password},
                           headers={'Content-Type': 'application/json'})
    json_data = response.get_json()
    return json_data['access_token']


def setup_user_with_no_permissions(db):
    role_with_no_permissions = Role(name=fake.job(), permissions=0)
    db.session.add(role_with_no_permissions)
    db.session.commit()
    user_with_no_permissions = User(email=fake.email(), username=fake.user_name(), password=fake.password(),
                                    name=fake.name(), role=role_with_no_permissions)
    db.session.add(user_with_no_permissions)
    db.session.commit()

    return user_with_no_permissions
