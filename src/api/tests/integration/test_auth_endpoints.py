import json
import pytest
from ..test_helpers import get_access_token, fake
from app.models import User


def test_can_login_with_username(test_client, test_db):

    response = test_client.post('/auth/login',
                                json={'login': 'admin', 'password': 'admin'},
                                headers={'Content-Type': 'application/json'})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['access_token']


def test_logging_in_with_gps(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'login': 'admin', 'password': 'admin',
                                      "latitude": 18.423566, "longitude": -30.628923},
                                headers={'Content-Type': 'application/json'})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['access_token']
    assert json_data['profile']['last_login_location']
    assert json_data['profile']['last_login_location']['latitude'] == 18.423566
    assert json_data['profile']['last_login_location']['longitude'] == -30.628923
    assert json_data['profile']['last_login_location']['location_recorded_dt']


def test_can_login_with_email(test_client, test_db):

    response = test_client.post('/auth/login',
                                json={'login': 'ilabtoolkit@gmail.com', 'password': 'admin'},
                                headers={'Content-Type': 'application/json'})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['access_token']


def test_login_fails_without_login(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'password': 'admin'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Missing login parameter'


def test_login_fails_without_password(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'login': 'admin'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Missing password parameter'


def test_login_fails_with_bad_password(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'login': 'admin', 'password': 'badpassword'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == 'Bad login or password'


def test_login_fails_unknown_username(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'login': 'unknownuser', 'password': 'admin'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == 'unknown user'


def test_login_fails_unknown_email(test_client, test_db):
    response = test_client.post('/auth/login',
                                json={'login': 'unknownuser@example.com', 'password': 'admin'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == 'unknown user'


def test_login_fails_for_inactive_user(test_client, test_db):
    user = User.query.filter_by(username='datareader').first()
    user.is_active = False
    test_db.session.commit()

    response = test_client.post('/auth/login',
                                json={'login': 'datareader', 'password': 'datareader'},
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == 'User is inactive'


def test_can_logout(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.post('/auth/logout', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Successfully logged out'


def test_cannot_access_secure_after_logout(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.post('/auth/logout', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200
    response = test_client.get('/secure', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message']
    assert json_data['message'] == "Token has been revoked"


# /auth/request-password-reset
reset_password_request_test_cases = [
    {
        'id': 'good-request',
        'email': 'ilabtoolkit@gmail.com',
        'response_status': 200,
        'response_message': 'An email with instructions to reset your password has been sent to you.'
    }, {
        'id': 'invalid-email',
        'email': 'noone@nowhere.com',
        'response_status': 200,
        'response_message': 'An email with instructions to reset your password has been sent to you.'
    }, {
        'id': 'missing-email',
        'email': None,
        'response_status': 400,
        'response_message': "User's email addresses cannot be null or empty."
    }
]

reset_password_request_test_case_ids = [case['id'] for case in reset_password_request_test_cases]


@pytest.mark.parametrize('test_case', reset_password_request_test_cases, ids=reset_password_request_test_case_ids)
def test_request_reset_password(test_client, test_db, test_case):
    """
    Covers

    Scenario: Client requests password reset with valid email address
      Given a Client submits a request to reset a password
      When the Client submits the request with a valid email address
      Then the API generates a reset password token
      And sends the user a reset password email
      And the email contains a link to the web applications reset password page
      And the link in the email contains the reset password token
      And the API responds to the Client with status 200 and the message "An email with instructions to reset your password has been sent to you."

    Scenario: Client requests password reset with invalid email address
      Given a Client submits a request to reset a password
      When the Client submits the request with an invalid email address
      Then the API drops the request
      And responds to the Client with status 200 and the message "An email with instructions to reset your password has been sent to you."

    Scenario: Client requests password reset without an email address
      Given a Client submits a request to reset a password
      When the Client submits the request without an email address
      Then the API responds to the client with status 400 and message "User's email addresses cannot be null or empty."
    """

    response = test_client.post('/auth/request-password-reset', data=json.dumps({'email': test_case['email']}),
                                headers={'Content-Type': 'application/json'})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


# /auth/reset-password/<reset_password_token>

def test_reset_password(test_client, test_db):
    """
    Scenario: Client submits password reset with valid token
      Given a Client submits a reset password
      When they submit a valid password reset token and new password
      Then the API sets the user's password
      And responds to the Client with status 200 and message "Your password was successfully reset."
    """
    user = User.query.filter_by(username='datacollector').first()
    new_password = fake.password(length=15)
    response = test_client.post(f"/auth/reset-password/{user.generate_reset_token()}",
                                data=json.dumps({'new_password': new_password, 'confirm_password': new_password}),
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Your password was successfully reset."
    assert user.verify_password(new_password)


def test_reset_password_with_invalid_token(test_client, test_db):
    """
    Scenario: Client submits password reset with invalid token
      Given a Client submits a reset password
      When they submit an invalid password reset token and new password
      Then responds to the Client with status 400 and message "Your password was not successfully reset."
    """
    user = User.query.filter_by(username='datacollector').first()
    new_password = fake.password(length=15)
    response = test_client.post(f"/auth/reset-password/{user.generate_reset_token()}AA",
                                data=json.dumps({'new_password': new_password, 'confirm_password': new_password}),
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "Your password was not successfully reset."
    assert user.verify_password("datacollector")


reset_password_test_cases = [
    {
        'id': 'missing-new-password',
        'new_password': None,
        'confirm_password': '+PmvVhOp(6NZDIT',
        'response_status': 400,
        'response_message': 'New password is missing.'
    }, {
        'id': 'missing-confirm-password',
        'new_password': '+PmvVhOp(6NZDIT',
        'confirm_password': None,
        'response_status': 400,
        'response_message': 'Confirmation password is missing.'
    }, {
        'id': 'passwords-dont-match',
        'new_password': '+PmvVhOp(6NZDIT',
        'confirm_password': 'i$IsTXki*x93SNn',
        'response_status': 400,
        'response_message': 'Passwords must match.'
    }, {
        'id': 'passwords-too-short',
        'new_password': '*5QNt',
        'confirm_password': '*5QNt',
        'response_status': 400,
        'response_message': 'Password must be at least 10 characters long.'
    }, {
        'id': 'passwords-too-long',
        'new_password': 'w5u^3QOYI8_88!dssMHLt4X%OBAAXtt#7xg5aQypODGGxSK%IAsz5JJVQ$j9Ag_A5TFx@8',
        'confirm_password': 'w5u^3QOYI8_88!dssMHLt4X%OBAAXtt#7xg5aQypODGGxSK%IAsz5JJVQ$j9Ag_A5TFx@8',
        'response_status': 400,
        'response_message': 'Password must be less than 64 characters long.'
    }
]

reset_password_test_case_ids = [case['id'] for case in reset_password_test_cases]


@pytest.mark.parametrize('test_case', reset_password_test_cases, ids=reset_password_test_case_ids)
def test_reset_password_with_bad_data(test_client, test_db, test_case):
    """
    Scenario: Client submits password reset without passwords
      Given a Client submits a password reset
      When the Client does not send the new password
      Then the API responds with status 400 and message "New password is missing."

    Scenario: Client submits password reset where passwords don't match
      Given a Client submits a password reset
      When the Client sends new and confirm passwords that don't match
      Then the API responds with status 400 and message "Passwords must match."

    Scenario: Client submits password reset where passwords are too short
      Given a Client submits a password reset
      When the Client sends passwords that are less than 10 characters long
      Then the API responds with status 400 and message "Password must be at least 10 characters long."

    Scenario: Client submits password reset passwords are too long
      Given a Client submits a password reset
      When the Client sends passwords that are longer than 64 characters long
      Then the API responds with status 400 and message "Password must be less than 64 characters long."
    """
    user = User.query.filter_by(username='datacollector').first()
    response = test_client.post(f"/auth/reset-password/{user.generate_reset_token()}",
                                data=json.dumps({'new_password': test_case['new_password'],
                                                 'confirm_password': test_case['confirm_password']}),
                                headers={'Content-Type': 'application/json'})
    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']
    assert user.verify_password("datacollector")
