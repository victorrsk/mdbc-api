from fastapi import status

# TODO
# 9. test delete author
# 10. teste delete author out of user authors list range (403 forbidden)


def test_create_author(user, client, token):
    response = client.post(
        '/authors', json={'name': 'test'}, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'name': 'test', 'id': 1, 'created_by_id': user.id}
    assert response.status_code == status.HTTP_201_CREATED


def test_create_author_already_exists(client, token, author):
    response = client.post(
        '/authors',
        json={'name': author.name},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'author already exists'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_read_author(client, author, token):
    response = client.get(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {
        'name': author.name,
        'id': author.id,
        'created_by_id': author.created_by_id,
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_non_existent_author(client, token):
    response = client.get('/authors/1', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'author not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_authors(client, token, author):
    response = client.get('/authors', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {
        'authors': [
            {
                'name': author.name,
                'id': author.id,
                'created_by_id': author.created_by_id,
            }
        ]
    }

    assert response.status_code == status.HTTP_200_OK


def test_update_author(client, author, token):
    response = client.put(
        f'/authors/{author.id}',
        json={'name': 'new_name'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {
        'name': author.name,
        'id': author.id,
        'created_by_id': author.created_by_id,
    }

    assert response.status_code == status.HTTP_200_OK


def test_update_author_already_exists(client, token, author, user):
    client.post(
        '/authors',
        json={'name': 'new_name'},
        headers={'Authorization': f'Bearer {token}'},
    )

    response = client.put(
        f'/authors/{author.id}',
        json={'name': 'new_name'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'author already exists'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_author_out_of_user_authors_list_range(client, token):
    response = client.put(
        '/authors/1',
        json={'name': 'test'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_other_user_author(client, author, token, user):
    client.post(
        '/users',
        json={'username': 'test2', 'email': 'test2@email.com', 'password': 'test2pwd'},
    )
    response2 = client.post(
        '/auth/token', data={'username': 'test2@email.com', 'password': 'test2pwd'}
    )
    token2 = response2.json()['access_token']

    client.post(
        '/authors',
        json={'name': 'other_author'},
        headers={'Authorization': f'Bearer {token2}'},
    )

    response = client.put(
        '/authors/2',
        json={'name': 'bleehhh'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_author(token, author, client):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'author deleted'}
    assert response.status_code == status.HTTP_200_OK


def test_delete_non_existent_author(token, client):
    response = client.delete('/authors/1', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_other_user_author(client, author, token, user):
    client.post(
        '/users',
        json={'username': 'test2', 'email': 'test2@email.com', 'password': 'test2pwd'},
    )
    response2 = client.post(
        '/auth/token', data={'username': 'test2@email.com', 'password': 'test2pwd'}
    )
    token2 = response2.json()['access_token']

    client.post(
        '/authors',
        json={'name': 'other_author'},
        headers={'Authorization': f'Bearer {token2}'},
    )

    response = client.delete(
        '/authors/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN
