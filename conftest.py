import pytest
from rest_framework.reverse import reverse

@pytest.fixture
@pytest.mark.django_db
def login_fixture(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john@1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    
    login_data = {
        "username" : "abhishek",
        "password" : "john@1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    # note_id = response_note.data["data"]["id"]
    # print(response_note.data)
    return response.data['token']

@pytest.fixture
@pytest.mark.django_db
def login_super_fixture(client):
    register_data = {
        "username" : "admin1234",
        "password" : "admin@1234",
        "email" : "deepakchandu9@gmail.com",
        "superkey":"hf12345678"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    login_data = {
        "username": "admin1234",
        "password": "admin@1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    return response.data['token']

@pytest.fixture
@pytest.mark.django_db
def create_book_fixture(client,login_super_fixture):
    data = {
        "title": "Test Book",
        "author": "Test Author",
        "price": 1099,
        "quantity": 5
    }

    url = reverse('book_api')
    response = client.post(url, data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_super_fixture}")

    assert response.status_code == 201
    return {'token': login_super_fixture, 'book_id': response.data["data"]["id"]}

@pytest.fixture
@pytest.mark.django_db
def create_cart_items_fixture(client, create_book_fixture):
    book_id = create_book_fixture["book_id"]
    token = create_book_fixture['token']
    cart_data = {
        "book": book_id,
        "quantity": 2
    }
    url = reverse("cart-api")
    response = client.post(url, cart_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    return {'token': token, 'cart_id': response.data["data"]["id"]}

@pytest.fixture
@pytest.mark.django_db
def place_order_fixture(client, create_cart_items_fixture):
    cart_id = create_cart_items_fixture["cart_id"]
    token = create_cart_items_fixture['token']
    cart_data = {
        "id": cart_id
    }
    url = reverse("order-api")
    response = client.post(url, cart_data, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}")
    return {'token': token, 'cart_id': cart_id}