import json
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
@patch("jiboia.accounts.views.create_user_service")
def test_create_user_success(mock_service):
    client = Client()

    mock_service.return_value = {
        "id": 1,
        "username": "Pedro Maia",
        "email": "testando2@gmail.com",
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": True,
        },
    }

    payload = {
        "username": "Pedro Maia",
        "email": "testando2@gmail.com",
        "password": "MinhaSenhaSegura123",
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": True,
        },
    }

    response = client.post(
        reverse("users_create"),
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json() == "Usuário criado com sucesso"
    mock_service.assert_called_once_with(
        "Pedro Maia",
        "MinhaSenhaSegura123",
        "testando2@gmail.com",
        payload["permissions"],
    )


@pytest.mark.django_db
@patch("jiboia.accounts.views.create_user_service")
def test_create_user_no_true_permission(mock_service):
    client = Client()

    payload = {
        "username": "Pedro Maia",
        "email": "testando2@gmail.com",
        "password": "MinhaSenhaSegura123",
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": False,
        },
    }

    response = client.post(
        reverse("users_create"),
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 400 or response.status_code == 500
    mock_service.assert_not_called()


@pytest.mark.django_db
@patch("jiboia.accounts.views.create_user_service")
def test_create_user_service_value_error(mock_service):
    client = Client()

    mock_service.side_effect = ValueError("A user with this email already exists.")

    payload = {
        "username": "Pedro Maia",
        "email": "testando2@gmail.com",
        "password": "MinhaSenhaSegura123",
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": True,
        },
    }

    response = client.post(
        reverse("users_create"),
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {"message": "A user with this email already exists."}
    mock_service.assert_called_once_with(
        "Pedro Maia",
        "MinhaSenhaSegura123",
        "testando2@gmail.com",
        payload["permissions"],
    )


@pytest.mark.django_db
def test_create_user_invalid_json():
    client = Client()

    response = client.post(
        reverse("users_create"),
        data="username=Pedro",
        content_type="application/json",
    )

    assert response.status_code in [400, 500]
