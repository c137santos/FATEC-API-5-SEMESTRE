import pytest

from jiboia.accounts.models import User
from jiboia.accounts.services import get_all_users


@pytest.mark.django_db
class TestGetAllUsers:
    def test_get_all_users_returns_list_of_users(self):
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
            last_name="Doe",
            email="jane@example.com",
            password="1234",
            team_member=True,
        )

        users = get_all_users()

        assert isinstance(users, list)
        assert len(users) == 2

        for user_data in users:
            assert set(user_data.keys()) == {"id", "username", "email", "permissions"}
            assert isinstance(user_data["permissions"], dict)

        john_data = next(u for u in users if u["username"] == "john")
        assert john_data["permissions"]["PROJECT_MANAGER"] is True
        assert john_data["permissions"]["TEAM_MEMBER"] is False
