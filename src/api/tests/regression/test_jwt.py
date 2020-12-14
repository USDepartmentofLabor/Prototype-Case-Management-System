"""Regression tests involving JWT generation/authentication"""

import pytest

from app import models
from tests import test_helpers


def test_change_email_jwt(test_client, test_db):
    """Regression test for EPS-306

    Scenario: Client generates a JWT via login
    Client submits a valid request to change their account email

    Expected: JWT remains valid
    """
    access_token = test_helpers.get_access_token(test_client)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}"
    }
    response = test_client.get('/users/1', headers=headers)
    assert response.status_code == 200

    # Update account with new email
    user = response.json
    user['email'] = 'new-email@example.com'

    response = test_client.put('/users/1', json=user, headers=headers)
    assert response.status_code == 200

    # JWT remains valid
    response = test_client.get('/users/1', headers=headers)
    assert response.status_code == 200
