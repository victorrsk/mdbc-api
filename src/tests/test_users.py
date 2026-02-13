from fastapi import status


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'testemail@email.com',
            'password': 'password123',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'testemail@email.com',
    }
    assert response.status_code == status.HTTP_201_CREATED


def test_create_user_username_in_use(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'otheremail@email.com',
            'password': 'password123',
        },
    )

    assert response.json() == {'detail': 'username or email already in use'}


def test_create_user_email_in_use(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'other_test',
            'email': 'testemail@email.com',
            'password': 'password123',
        },
    )

    assert response.json() == {'detail': 'username or email already in use'}


def test_read_user(client, user):
    response = client.get(f'/users/{user.id}')
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_non_existent_user(client):
    response = client.get('/users/1')

    assert response.json() == {'detail': 'user not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_no_users(client):
    response = client.get('/users')

    assert response.json() == {'users': []}
    assert response.status_code == status.HTTP_200_OK


def test_read_users(client, user):
    response = client.get('/users')

    assert response.json() == {
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_update_user(client, user):
    # updates the existent user created from the fixture
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'newname',
            'email': 'newemail@email.com',
            'password': 'newpwd123',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'newname',
        'email': 'newemail@email.com',
    }
    assert response.status_code == status.HTTP_200_OK


def test_update_user_username_in_use(client, user):
    client.post(
        '/users',
        json={
            'username': 'othertest',
            'email': 'otheremail@email.com',
            'password': 'password123',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'othertest',
            'email': 'testemail@email.com',
            'password': 'star-the-repo-if-you-read-me',
        },
    )

    assert response.json() == {'detail': 'username or email already in use'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_user_email_in_use(client, user):
    client.post(
        '/users',
        json={
            'username': 'test1',
            'email': 'email@email.com',
            'password': 'password123',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'othertest',
            'email': 'email@email.com',
            'password': 'star-the-repo-if-you-read-me',
        },
    )

    assert response.json() == {'detail': 'username or email already in use'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.json() == {'message': 'user deleted'}
    assert response.status_code == status.HTTP_200_OK


def test_delete_non_existent_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'detail': 'user not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND
