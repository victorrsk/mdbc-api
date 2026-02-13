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
