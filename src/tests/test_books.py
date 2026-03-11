from fastapi import status

"""
In order to have a great undestanding of the tests, you probaly will need some pytest
knowledge about fixtures and related things.

Some tests are really confusing and the mocked data for the entities fixtures like
authors, book and reviews is hard coded.
- Probally will solve this later
"""


def test_create_book(client, user, token, author):
    response = client.post(
        '/books',
        json={
            'title': 'some book',
            'year': 2000,
            'author_id': author.id,
            'genre': 'fantasy',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {
        'title': 'some-book',
        'year': 2000,
        'id': 1,
        'author_id': author.id,
        'creator_id': user.id,
        'creator_name': user.username,
        'genre': 'fantasy',
    }
    assert response.status_code == status.HTTP_201_CREATED


def test_create_existent_book_title(client, user, token, author, book):
    response = client.post(
        '/books',
        json={
            'title': book.title,
            'year': book.year,
            'author_id': book.author_id,
            'genre': book.genre,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'book already exists'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_book_non_existent_author(client, user, token):
    response = client.post(
        '/books',
        json={
            'title': 'some book',
            'year': 2000,
            'author_id': 1,
            'genre': 'fantasy',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'author not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_book(client, token, user, author, book):
    response = client.get(f'/books/{book.id}')

    assert response.json() == {
        'title': book.title,
        'year': book.year,
        'id': book.id,
        'author_id': book.author_id,
        'creator_id': book.creator_id,
        'creator_name': book.creator_name,
        'genre': book.genre.value,
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_books(client, token, user, author, book):
    response = client.get('/books')

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'year': book.year,
                'id': book.id,
                'author_id': book.author_id,
                'creator_id': book.creator_id,
                'creator_name': book.creator_name,
                'genre': book.genre.value,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_non_existent_book(client, token, user, author):
    response = client.get('/books/1')

    assert response.json() == {'detail': 'book not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_book(client, token, user, author, book):
    response = client.patch(
        f'/books/{book.id}',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {
        'title': book.title,
        'year': book.year,
        'id': book.id,
        'author_id': book.author_id,
        'creator_id': book.creator_id,
        'creator_name': book.creator_name,
        'genre': book.genre.value,
    }
    assert response.status_code == status.HTTP_200_OK


def test_update_book_title_in_use(client, token, user, author, book):
    client.post(
        '/books',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token}'},
    )

    response = client.patch(
        f'/books/{book.id}',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'book already exists'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_other_user_book(client, token, user, author):
    # creating other user, getting a token and posting a book
    client.post(
        '/users',
        json={'username': 'test2', 'email': 'test2@email.com', 'password': 'test2pwd'},
    )
    response2 = client.post(
        '/auth/token', data={'username': 'test2@email.com', 'password': 'test2pwd'}
    )
    token2 = response2.json()['access_token']
    client.post(
        '/books',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token2}'},
    )
    # just trying to update the book created by the user above
    response = client.patch(
        '/books/1',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_non_existent_book(client, token, user, author):
    response = client.patch(
        '/books/1',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'book not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_book_non_existent_author(client, token, user, book):
    response = client.patch(
        '/books/1',
        json={
            'title': book.title,
            'year': book.year,
            'genre': book.genre,
            'author_id': 2,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'author not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_book(client, book, token, user, author):
    response = client.delete(
        f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'book deleted'}
    assert response.status_code == status.HTTP_200_OK


def test_delete_non_existent_book(client, token):
    response = client.delete('/books/1', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == {'detail': 'book not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_other_user_book(client, token, user, author):
    # just creating other user, getting a token and posting a book in this user id
    client.post(
        '/users',
        json={'username': 'test2', 'email': 'test2@email.com', 'password': 'test2pwd'},
    )
    response2 = client.post(
        '/auth/token', data={'username': 'test2@email.com', 'password': 'test2pwd'}
    )
    token2 = response2.json()['access_token']
    client.post(
        '/books',
        json={'title': 'new title', 'genre': 'poetry', 'year': 2000, 'author_id': 1},
        headers={'Authorization': f'Bearer {token2}'},
    )
    # trying to delete the book created above by other user
    response = client.delete(
        '/books/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_read_books_by_genre(client, token, book):
    response = client.get(f'/books?genre={book.genre.value}')

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'id': book.id,
                'creator_name': book.creator_name,
                'creator_id': book.creator_id,
                'author_id': book.author_id,
                'genre': book.genre.value,
                'year': book.year,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_books_by_title(client, token, book):
    response = client.get(f'/books?title={book.title}')

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'id': book.id,
                'creator_name': book.creator_name,
                'creator_id': book.creator_id,
                'author_id': book.author_id,
                'genre': book.genre.value,
                'year': book.year,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_books_by_creator_name(client, token, book):
    response = client.get(f'/books?creator_name={book.creator_name}')

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'id': book.id,
                'creator_name': book.creator_name,
                'creator_id': book.creator_id,
                'author_id': book.author_id,
                'genre': book.genre.value,
                'year': book.year,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_books_by_author_id(client, token, book):
    response = client.get(f'/books?author_id={book.author_id}')

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'id': book.id,
                'creator_name': book.creator_name,
                'creator_id': book.creator_id,
                'author_id': book.author_id,
                'genre': book.genre.value,
                'year': book.year,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_books_all_filters(client, token, book):
    response = client.get(
        f'/books?title={book.title}&author_id={book.author_id}&creator_name={book.creator_name}'
    )

    assert response.json() == {
        'books': [
            {
                'title': book.title,
                'id': book.id,
                'creator_name': book.creator_name,
                'creator_id': book.creator_id,
                'author_id': book.author_id,
                'genre': book.genre.value,
                'year': book.year,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_create_book_review(client, token, book, user):
    response = client.post(
        f'/books/{book.id}/reviews',
        json={'comment': 'test comment haha'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {
        'id': 1,
        'book_id': book.id,
        'user_id': user.id,
        'comment': 'test comment haha',
        'book_title': book.title,
    }
    assert response.status_code == status.HTTP_201_CREATED


def test_read_book_review(client, token, book, user):
    client.post(
        f'/books/{book.id}/reviews',
        json={'comment': 'test comment haha'},
        headers={'Authorization': f'Bearer {token}'},
    )
    response = client.get(f'/books/{book.id}/reviews')

    assert response.json() == {
        'reviews': [
            {
                'id': 1,
                'book_id': book.id,
                'user_id': user.id,
                'comment': 'test comment haha',
                'book_title': book.title,
            }
        ]
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_review_by_id(client, review):
    response = client.get(f'/books/reviews/{review.id}')

    assert response.json() == {
        'id': review.id,
        'book_title': review.book_title,
        'book_id': review.book_id,
        'user_id': review.user_id,
        'comment': review.comment,
    }
    assert response.status_code == status.HTTP_200_OK


def test_read_non_existent_book_review(client):
    response = client.get('/books/1/reviews')

    assert response.json() == {'detail': 'book not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_review(client, review, token):
    response = client.delete(
        f'/books/reviews/{review.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'review deleted'}
    assert response.status_code == status.HTTP_200_OK


def test_delete_other_user_review(client, token, review, book):
    # just creating another user, getting a token and posting a book review
    client.post(
        '/users',
        json={
            'username': 'testing',
            'email': 'testing@email.com',
            'password': 'pwd123456',
        },
    )
    token_response = client.post(
        '/auth/token/', data={'username': 'testing@email.com', 'password': 'pwd123456'}
    )
    token2 = token_response.json()['access_token']

    client.post(
        f'/books/{review.book_id}/reviews',
        json={'comment': 'horrible book, bleh'},
        headers={'Authorization': f'Bearer {token2}'},
    )
    # this block is the only thing that matters
    response = client.delete(
        '/books/reviews/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'not enough permission'}
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_two_reviews_same_book(client, book, review, token):
    # the review fixture is created in the DB with the same user_id of the next
    # post request for the same book
    # it will raise an error cause a user can only review a book one time
    response = client.post(
        f'/books/{review.book_id}/reviews',
        json={'comment': 'another review, same user'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'review already exists'}
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_non_existent_book_review(client, token):
    response = client.post(
        '/books/1/reviews',
        json={'comment': 'this will raise an error'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'book not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_no_book_reviews(client, book):
    response = client.get(f'/books/{book.id}/reviews')

    assert response.json() == {'detail': 'review not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_non_existent_review(client, book, token):
    response = client.delete(
        '/books/reviews/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'detail': 'review not found'}
    assert response.status_code == status.HTTP_404_NOT_FOUND
