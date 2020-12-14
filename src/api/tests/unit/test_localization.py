from tests import test_helpers


def test_default_endpoint(test_client, test_db):
    access_token = test_helpers.get_access_token(test_client)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}"
    }

    resp = test_client.get('/secure', headers=headers)
    assert resp.status_code == 200
    assert resp.json['message'] == 'Hi ilabtoolkit@gmail.com'

    headers['Accept-Language'] = 'es'
    resp = test_client.get('/secure', headers=headers)
    assert resp.status_code == 200
    assert resp.json['message'] == 'Hola ilabtoolkit@gmail.com'

    headers['Accept-Language'] = 'fr'
    resp = test_client.get('/secure', headers=headers)
    assert resp.status_code == 200
    assert resp.json['message'] == 'Salut ilabtoolkit@gmail.com'
