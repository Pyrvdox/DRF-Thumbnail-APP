import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from tbnr.models import Image
from tbnr.serializers import ListSerializer

User = get_user_model()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username='testuser',
        password='testpassword',
    )
    return user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_user_login(api_client, test_user):
    url = reverse('login')
    data = {
        'username': 'testuser',
        'password': 'testpassword',
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == 302

@pytest.mark.django_db
def test_user_logout(api_client, test_user):
    api_client.login(username='testuser', password='testpassword')

    url = reverse('logout')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'Wylogowano pomyślnie' in response.data['message']


@pytest.mark.django_db
def test_list_view(api_client, test_user):
    Image.objects.create(name='Image1', uploaded_by=test_user)
    Image.objects.create(name='Image2', uploaded_by=test_user)
    Image.objects.create(name='Image3', uploaded_by=test_user)

    api_client.login(username='testuser', password='testpassword')

    url = reverse('list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    record_count = Image.objects.filter(uploaded_by=test_user).count()
    assert len(response.data) == record_count
    assert all('name' in item for item in response.data)
    assert all('uploaded_by' in item for item in response.data)


@pytest.mark.django_db
def test_detail_view(api_client, test_user):
    image = Image.objects.create(name='Image1', uploaded_by=test_user)
    api_client.login(username='testuser', password='testpassword')

    url = reverse('details', args=[image.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert 'id' in response.data
    assert 'name' in response.data
    assert 'height' in response.data
    assert 'width' in response.data
    assert 'plan_name' in response.data
    assert 'plan_heights' in response.data

@pytest.mark.django_db
def test_add_view(api_client, test_user):
    api_client.login(username='testuser', password='testpassword')

    url = reverse('add')
    data = {
        'name': 'NewImage',
        'file': open('/Users/macbookair/Documents/legion.jpeg', 'rb')
    }
    response = api_client.post(url, data, format='multipart')

    assert response.status_code == status.HTTP_201_CREATED
    assert Image.objects.filter(name='NewImage').exists()