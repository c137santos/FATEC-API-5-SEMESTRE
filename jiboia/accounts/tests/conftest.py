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
    # Adicionamos db como dependência para garantir que a transação seja gerenciada corretamente
    client.force_login(user_jon)  # Podemos usar user_jon diretamente sem consultar novamente
    return user_jon
