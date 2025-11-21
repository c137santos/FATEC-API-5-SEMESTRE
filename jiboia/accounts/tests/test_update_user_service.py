import pytest

from jiboia.accounts.models import User
from jiboia.accounts.services import update_user_service


@pytest.mark.django_db
def test_update_user_not_found():
    result = update_user_service(9999, {"username": "New"})
    assert result is None


@pytest.mark.django_db
def test_update_user_inactive():
    user = User.objects.create(username="Ana", email="ana@example.com", is_active=False, project_admin=True)

    with pytest.raises(ValueError, match="Usuário não encontrado."):
        update_user_service(user.id, {"username": "X"})


@pytest.mark.django_db
def test_update_user_empty_username():
    user = User.objects.create(username="Ana", email="ana@example.com", is_active=True, project_admin=True)

    with pytest.raises(ValueError, match="O nome de usuário não pode ser vazio."):
        update_user_service(user.id, {"username": ""})


@pytest.mark.django_db
def test_update_user_empty_email():
    user = User.objects.create(username="Ana", email="ana@example.com", is_active=True, project_admin=True)

    with pytest.raises(ValueError, match="O email não pode ser vazio."):
        update_user_service(user.id, {"email": ""})


@pytest.mark.django_db
def test_update_user_duplicate_email():
    user1 = User.objects.create(username="Ana", email="ana@example.com", is_active=True, project_admin=True)

    User.objects.create(username="Joao", email="joao@example.com", is_active=True, project_admin=True)

    with pytest.raises(ValueError, match="Já existe um usuário com esse email."):
        update_user_service(user1.id, {"email": "joao@example.com"})


@pytest.mark.django_db
def test_update_user_no_active_permission():
    user = User.objects.create(username="Ana", email="ana@example.com", is_active=True, project_admin=True)

    data = {
        "permissions": {
            "PROJECT_ADMIN": False,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
            "TEAM_MEMBER": False,
        }
    }

    with pytest.raises(ValueError, match="O usuário deve ter pelo menos uma permissão ativa."):
        update_user_service(user.id, data)


@pytest.mark.django_db
def test_update_user_success():
    user = User.objects.create(
        username="Ana",
        email="ana@example.com",
        is_active=True,
        project_admin=True,
        project_manager=False,
        team_leader=True,
        team_member=False,
    )

    data = {
        "username": "Ana Paula",
        "email": "anapaula@example.com",
        "permissions": {"PROJECT_ADMIN": True, "PROJECT_MANAGER": False, "TEAM_MEMBER": False, "TEAM_LEADER": True},
    }

    updated = update_user_service(user.id, data)

    assert updated.username == "Ana Paula"
    assert updated.email == "anapaula@example.com"
    assert updated.project_admin is True
    assert updated.team_leader is True


@pytest.mark.django_db
def test_update_user_preserves_permissions_if_not_sent():
    user = User.objects.create(
        username="Ana", email="ana@example.com", is_active=True, project_admin=True, team_leader=False
    )

    data = {"username": "Ana Maria"}

    updated = update_user_service(user.id, data)

    assert updated.username == "Ana Maria"
    assert updated.project_admin is True
    assert updated.team_leader is False


@pytest.mark.django_db
def test_update_user_permissions_mapping():
    user = User.objects.create(
        username="Ana",
        email="ana@example.com",
        is_active=True,
        project_admin=True,
        project_manager=False,
        team_leader=False,
        team_member=True,
    )

    data = {
        "permissions": {
            "PROJECT_ADMIN": True,
            "TEAM_MEMBER": True,
            "PROJECT_MANAGER": False,
            "TEAM_LEADER": False,
        }
    }

    updated = update_user_service(user.id, data)

    assert updated.project_admin is True
    assert updated.team_member is True
