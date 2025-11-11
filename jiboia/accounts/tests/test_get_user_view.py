import pytest

from jiboia.accounts.models import User


@pytest.mark.django_db
class TestGetAllUsersView:
    def test_get_all_users_success(self, client):
        User.objects.create_user(
            username="john",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="1234",
            project_manager=True,
        )
        User.objects.create_user(
            username="jane",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            password="abcd",
            team_member=True,
        )

        response = client.get("/api/accounts/users/?page=1&page_size=1")

        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert "total_pages" in data
        assert "current_page" in data
        assert "results" in data

        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1

        user_data = data["results"][0]
        assert set(user_data.keys()) == {"id", "username", "email", "permissions"}
        assert isinstance(user_data["permissions"], dict)

    def test_get_all_users_no_users(self, client):
        response = client.get("/api/accounts/users/")

        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "Nenhum usuário encontrado."
