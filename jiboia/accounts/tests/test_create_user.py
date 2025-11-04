import pytest
from django.contrib.auth import get_user_model

from jiboia.accounts.services import create_user

User = get_user_model()


@pytest.mark.django_db
class TestCreateUser:
    def test_create_user_successfully(self):
        permissions = {"PROJECT_MANAGER": True, "TEAM_LEADER": False, "TEAM_MEMBER": False}

        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123",
            "permissions": permissions,
        }

        user_dict = create_user(**user_data)

        user = User.objects.get(email="john@example.com")
        assert user is not None
        assert user.name == "John Doe"
        assert user.project_manager is True
        assert user.team_leader is False
        assert user.team_member is False

        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "john@example.com"

    def test_missing_required_fields(self):
        with pytest.raises(ValueError, match="Name, password, and email are required"):
            create_user("", "123", "user@example.com", {"TEAM_MEMBER": True})

    def test_no_permissions(self):
        with pytest.raises(ValueError, match="At least one permission must be granted"):
            create_user(
                "User",
                "123",
                "user@example.com",
                {"PROJECT_MANAGER": False, "TEAM_LEADER": False, "TEAM_MEMBER": False},
            )

    def test_duplicate_email(self):
        permissions = {"TEAM_MEMBER": True}
        create_user("User1", "123", "dup@example.com", permissions)

        with pytest.raises(ValueError, match="A user with this email already exists"):
            create_user("User2", "456", "dup@example.com", permissions)
