import pytest

from jiboia.accounts.models import User
from jiboia.accounts.services import delete_user


@pytest.mark.django_db
def test_delete_user_success():
    user = User.objects.create(username="test_user", email="test@example.com")

    result = delete_user(user.id)

    assert result is True
    assert User.objects.filter(id=user.id).exists() is False


@pytest.mark.django_db
def test_delete_user_not_found():
    result = delete_user(9999)

    assert result is False
