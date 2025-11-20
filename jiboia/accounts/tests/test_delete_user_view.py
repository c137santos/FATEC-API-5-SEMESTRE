import pytest
from django.test import Client

from jiboia.accounts.models import User


@pytest.mark.django_db
def test_delete_user_view_success(client):
    user = User.objects.create(username="testuser", email="test@example.com")

    url = f"/api/accounts/users/{user.id}"

    response = client.delete(url)

    assert response.status_code == 200
    assert User.objects.filter(id=user.id).count() == 0


@pytest.mark.django_db
def test_delete_user_view_user_not_found():
    client = Client()

    url = "/api/accounts/users/9999"

    response = client.delete(url)

    assert response.status_code == 404
    assert response.json() == {"message": "Usuário não encontrado"}
