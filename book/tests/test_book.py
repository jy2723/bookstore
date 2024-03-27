import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_create_book_success(client,login_super_fixture):
    data = {
        "title": "Test Book",
        "author": "Test Author",
        "price": 1099,
        "quantity": 5
    }

    url = reverse('book_api')
    response = client.post(url, data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_super_fixture}")
    print(response.data)

    assert response.status_code == 201
    
import pytest
from rest_framework.reverse import reverse

    
# Create Book - Failed (Unauthorized)
@pytest.mark.django_db
def test_create_book_should_return_failed_unauthorized(client, login_super_fixture):
    book_data = {
        "title": "Interstellar",
        "author": "Abhishek",
        "price": 20,
        "quantity": 15
    }
    url = reverse("book_api")
    response = client.post(url, book_data, content_type="application/json")
    assert response.status_code == 401
    
# Create Book - Failed (Title not provided)
@pytest.mark.django_db
def test_create_book_should_return_failed_title_not_provided(client, login_super_fixture):
    book_data = {
        "author": "Abhishek",
        "price": 20,
        "quantity": 15
    }
    url = reverse("book_api")
    response = client.post(url, book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_super_fixture}")
    assert response.status_code == 400
    
# Get Books
@pytest.mark.django_db
def test_get_books_should_return_success(client, login_super_fixture):
    url = reverse("book_api")
    response = client.get(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {login_super_fixture}")
    assert response.status_code == 200
    
# Get Books - Failed (Unauthorized)
@pytest.mark.django_db
def test_get_books_should_return_failed_unauthorized(client, login_super_fixture):
    url = reverse("book_api")
    response = client.get(url, content_type="application/json")
    assert response.status_code == 401
    
# Update Book
@pytest.mark.django_db
def test_update_book_should_return_success(client, create_book_fixture):
    book = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    updated_book_data = {
        "book_id": book,
        "title": "Interstellar",
        "author": "Abhishek",
        "price": 20,
        "quantity": 20
    }
    url = reverse("book_api")
    response = client.put(url, updated_book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    print(response.data)
    assert response.status_code == 200
    
# # Update Book - Failed (Unauthorized)
@pytest.mark.django_db
def test_update_book_should_return_failed_unauthorized(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    updated_book_data = {
        "id": book_id,
        "title": "Interstellar",
        "author": "Abhishek",
        "price": 20,
        "quantity": 20
    }
    url = reverse("book_api")
    response = client.put(url, updated_book_data, content_type="application/json")
    assert response.status_code == 401
    
# # Update Book - Failed (Book ID not provided)
@pytest.mark.django_db
def test_update_book_should_return_failed_book_id_not_provided(client, create_book_fixture):
    book = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    updated_book_data = {
        "title": "Interstellar",
        "author": "Abhishek",
        "price": 20,
        "quantity": 20
    }
    url = reverse("book_api")
    response = client.put(url, updated_book_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400
    
# # Delete Book
@pytest.mark.django_db
def test_delete_book_should_return_success(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    url = reverse("book_api")
    url_with_query = f"{url}?id={book_id}"
    response = client.delete(url_with_query, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 200
    
# # Delete Book - Failed (Unauthorized)
@pytest.mark.django_db
def test_delete_book_should_return_failed_unauthorized(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture["token"]
    url = reverse("book_api")
    url_with_query = f"{url}?id={book_id}"
    response = client.delete(url_with_query, content_type="application/json")
    assert response.status_code == 401
    
# # Delete Book - Failed (Book ID not provided)
@pytest.mark.django_db
def test_delete_book_should_return_failed_book_id_not_provided(client, create_book_fixture):
    token = create_book_fixture["token"]
    url = reverse("book_api")
    response = client.delete(url, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 400