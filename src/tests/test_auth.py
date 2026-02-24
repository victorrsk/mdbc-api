import jwt
from fastapi import status
from freezegun import freeze_time

from src.security import create_access_token
from src.settings import Settings

# there will be 2 types of tests here
# 1 - the tests where the token is literally created by sending a post request
# with all the necessary data to /auth/token

# 2 - the tests where the token are manipulated to ensure the raising of some errors
# that's why there are similar tests but with different contexts


def test_token_creation():
    data = {'sub': 'example@email.com'}
    token = create_access_token(data=data)
    decoded = jwt.decode(
        jwt=token, key=Settings().SECRET_KEY, algorithms=Settings().TOKEN_ALGORITHM
    )

    assert 'exp' in decoded.keys()
    assert 'sub' in decoded.keys()
    assert decoded['sub'] == data['sub']


# tests to create the token


def test_get_token(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': user.clean_pwd}
    )
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()
    assert response.json()['token_type'] == 'bearer'
    assert response.status_code == status.HTTP_200_OK


# this test will send an invalid/non-existent email to /token
def test_invalid_email_for_token(client, user):
    response = client.post(
        '/auth/token', data={'username': 'invalid@email.com', 'password': '123'}
    )

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# here the email is valid, but the given password will not match the hash
def test_incorrect_pwd_for_token(client, user):
    response = client.post(
        '/auth/token', data={'username': user.email, 'password': 'invalid'}
    )

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ----------------------------------

# tests manipulating the created_token


# this will send a get request to an protected endpoint
# the 'token' in the header is invalid, so at some moment it generates an Decode error
def test_token_decode_error(client):
    response = client.get('/users/', headers={'Authorization': 'Bearer invalid_token'})

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# this one will actually generate an valid token but without the expected 'sub' claim
def test_no_sub_in_token(client):
    data = {'invalid': 'invalid'}
    token = create_access_token(data=data)

    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# this one actually receive sub in the token, but theres nothing as its value
def test_no_content_in_sub_token(client):
    data = {'sub': ''}
    token = create_access_token(data=data)

    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# this test will freeze the time to get the token and then freeze again
# but 12 hours and 30 minutes later, when the token expired
def test_expired_token(client, user):
    with freeze_time('2026-01-01 00:00:00'):
        response = client.post(
            '/auth/token', data={'username': user.email, 'password': user.clean_pwd}
        )

    token = response.json()['access_token']

    with freeze_time('2026-01-01 12:30:00'):
        response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_nonexistent_email_in_token(client):
    data = {'sub': 'invalid@email.com'}
    token = create_access_token(data=data)

    response = client.get('/users/', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'could not validate credentials'}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# --------------------------------------
