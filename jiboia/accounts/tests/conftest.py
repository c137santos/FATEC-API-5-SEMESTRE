import pytest

from jiboia.accounts.models import User


@pytest.fixture
def user_jon(db):
    jon = User.objects.create_user(
        username="jon",
        first_name="Jon",
        last_name="Snow",
        email="jon@example.com",
        password="snow",
    )
    return jon


@pytest.fixture
def logged_jon(client, user_jon, db):
    client.force_login(user_jon)
