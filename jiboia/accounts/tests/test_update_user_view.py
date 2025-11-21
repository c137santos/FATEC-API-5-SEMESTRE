import json

import pytest
from django.urls import reverse

from jiboia.accounts.models import User


@pytest.mark.django_db
def test_update_user_view_success(client):
    user = User.objects.create(username="usuario", email="email@example.com", is_active=True, project_admin=True)

    url = reverse("update_user", kwargs={"user_id": user.id})
    payload = {
        "username": "NovoNome",
        "email": "novoemail@example.com",
        "permissions": {
            "PROJECT_ADMIN": True,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": False,
        },
    }

    response = client.patch(
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Usuário atualizado com sucesso"}

    user.refresh_from_db()
    assert user.username == "NovoNome"
    assert user.email == "novoemail@example.com"


@pytest.mark.django_db
def test_update_user_view_user_not_found(client):
    url = reverse("update_user", kwargs={"user_id": 9999})

    payload = {"username": "ABC"}

    response = client.patch(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 404
    assert response.json() == {"message": "Usuário não encontrado"}


@pytest.mark.django_db
def test_update_user_view_invalid_json(client):
    user = User.objects.create(
        username="usuario",
        email="email@example.com",
        is_active=True,
    )

    url = reverse("update_user", kwargs={"user_id": user.id})

    response = client.patch(
        url,
        data="{invalid_json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"message": "JSON inválido"}


@pytest.mark.django_db
def test_update_user_view_email_already_exists(client):
    user1 = User.objects.create(
        username="user1",
        email="email1@example.com",
        is_active=True,
        project_admin=True,
        project_manager=False,
        team_leader=False,
        team_member=False,
    )
    User.objects.create(
        username="user2",
        email="duplicado@example.com",
        is_active=True,
        project_admin=True,
        project_manager=False,
        team_leader=False,
        team_member=False,
    )

    url = reverse("update_user", kwargs={"user_id": user1.id})
    payload = {"email": "duplicado@example.com"}

    response = client.patch(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {"message": "Já existe um usuário com esse email."}


@pytest.mark.django_db
def test_update_user_view_remove_all_permissions_should_fail(client):
    user = User.objects.create(
        username="usuario",
        email="email@example.com",
        is_active=True,
        project_admin=True,
    )

    url = reverse("update_user", kwargs={"user_id": user.id})

    payload = {
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": False,
        }
    }

    response = client.patch(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {"message": "O usuário deve ter pelo menos uma permissão ativa."}


@pytest.mark.django_db
def test_update_user_view_inactive_user(client):
    user = User.objects.create(
        username="usuario",
        email="email@example.com",
        is_active=False,
        project_admin=True,
    )

    url = reverse("update_user", kwargs={"user_id": user.id})

    payload = {"username": "Novo"}

    response = client.patch(url, data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 400
    assert response.json() == {"message": "Usuário não encontrado."}
