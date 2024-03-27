import pytest
from rest_framework.reverse import reverse

@pytest.mark.django_db
def test_user_registeration_should_return_200_status(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john@1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    print(response.data)
    assert response.status_code == 201

@pytest.mark.django_db
def test_user_registeration_failed_special_character(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    print(response.data)
    assert response.status_code == 400
    
@pytest.mark.django_db
def test_user_registeration_failed_lessthan_three_chracters(client):
    register_data = {
        "username" : "ab",
        "password" : "john1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    print(response.data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_registeration_failed_mail_incorrect(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john1234",
        "email" : "deepakchandu9gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    print(response.data)
    assert response.status_code == 400
    
@pytest.mark.django_db
def test_login_success(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john@1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    login_data = {
        "username" : "abhishek",
        "password" : "john@1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_login_fail_wrong_username_or_password(client):
    register_data = {
        "username" : "abhishek",
        "password" : "john@1234",
        "email" : "deepakchandu9@gmail.com"
    }
    url = reverse("userApi")
    response = client.post(url, register_data, content_type="application/json")
    assert response.status_code == 201
    login_data = {
        "username" : "abhishek",
        "password" : "joh1234"
    }
    url = reverse("login")
    response = client.post(url, login_data, content_type="application/json")
    print(response.data)
    assert response.status_code == 400
    
@pytest.mark.django_db
def test_send_reset_password_link_success(db,client,login_fixture):
    url = reverse('reset')
    email = 'deepakchandu9@gmail.com'
    data = {'email': email}

    response = client.post(url, data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_fixture}")
    print(response.data)

    assert response.status_code == 200

@pytest.mark.django_db
def test_send_reset_password_link_email_not_found(db,client,login_fixture):
    url = reverse('reset')
    email = 'nonexistent@example.com'
    data = {'email': email}

    response = client.post(url, data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_fixture}")

    assert response.status_code == 404

@pytest.mark.django_db
def test_send_reset_password_link_exception(db,client,login_fixture):
    url = reverse('reset')
    data = {}  

    response = client.post(url, data, content_type="application/json", 
                           HTTP_AUTHORIZATION=f"Bearer {login_fixture}")

    assert response.status_code == 400
    
@pytest.mark.django_db
def test_change_password_success(db,client,login_fixture):
    url = reverse('change')
    data = {'new_password': 'john@4321'}
    response = client.post(url + f'?token={login_fixture}', data, content_type="application/json")

    assert response.status_code == 200
    
@pytest.mark.django_db
def test_change_password_invalid_token(db,client,login_fixture):
    url = reverse('change')
    data = {'new_password': 'john@1234'}
    response = client.post(url, data, format='json')

    assert response.status_code == 400

@pytest.mark.django_db
def test_change_password_exception(db,client,login_fixture):
    invalid_token = 'invalid_token'

    url = reverse('change')
    data = {'new_password': 'new_password'}
    response = client.post(url + f'?token={invalid_token}', data, format='json')

    assert response.status_code == 400

