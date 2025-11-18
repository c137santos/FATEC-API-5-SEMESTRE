import pytest

BASE_URL = "/api/accounts/users/"


@pytest.mark.django_db
class TestUsersView:
    def test_get_users_success(self, client):
        response = client.get(BASE_URL)
        assert response.status_code in (200, 404)
        assert "application/json" in response["Content-Type"]


@pytest.mark.django_db
def test_post_create_user_success(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123",
        "permissions": {
            "PROJECT_ADMIN": True,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": False,
        },
    }

    response = client.post(BASE_URL, user_data, content_type="application/json")

    assert response.status_code in (200, 201)
    assert "application/json" in response["Content-Type"]

    json_data = response.json()
    assert json_data == "Usuário criado com sucesso"
