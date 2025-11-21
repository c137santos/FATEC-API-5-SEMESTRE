from jiboia.accounts.models import User


def list_users():
    users = User.objects.all()
    return [user.to_dict_json() for user in users]


def get_all_users():
    users = User.objects.all()
    return [user.to_get_user_json() for user in users]


def create_user(username, password, email, permissions):
    if not username or not password or not email:
        raise ValueError("Name, password, and email are required to create a user.")

    if not any(permissions.values()):
        raise ValueError("At least one permission must be granted to the user.")

    if User.objects.filter(email=email).exists():
        raise ValueError("A user with this email already exists.")

    user = User(
        username=username,
        email=email,
        project_admin=permissions.get("PROJECT_ADMIN", False),
        project_manager=permissions.get("PROJECT_MANAGER", False),
        team_leader=permissions.get("TEAM_LEADER", False),
        team_member=permissions.get("TEAM_MEMBER", True),
    )
    user.set_password(password)
    user.save()
    return user.to_dict_json()


def delete_user(user_id):
    try:
        user = User.objects.get(id=user_id, is_active=True)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return True
    except User.DoesNotExist:
        return False


def _ensure_user_exists(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def _validate_not_inactive(user):
    if not user.is_active:
        raise ValueError("Usuário não encontrado.")


def _validate_username(data):
    username = data.get("username")
    if username is not None and (not username or username.strip() == ""):
        raise ValueError("O nome de usuário não pode ser vazio.")


def _validate_email(data, user_id):
    email = data.get("email")
    if email is not None:
        if not email or email.strip() == "":
            raise ValueError("O email não pode ser vazio.")

        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValueError("Já existe um usuário com esse email.")


def _validate_permissions(data, user):
    permission_fields = {
        "PROJECT_ADMIN": "project_admin",
        "PROJECT_MANAGER": "project_manager",
        "TEAM_LEADER": "team_leader",
        "TEAM_MEMBER": "team_member",
    }

    if "permissions" not in data:
        return

    permissions = data.get("permissions", {})

    has_permission = any(
        bool(permissions.get(api_field, getattr(user, model_field)))
        for api_field, model_field in permission_fields.items()
    )

    if not has_permission:
        raise ValueError("O usuário deve ter pelo menos uma permissão ativa.")


def _apply_updates(user, data):
    if "username" in data:
        user.username = data["username"]

    if "email" in data:
        user.email = data["email"]

    if "permissions" in data:
        permission_map = {
            "PROJECT_ADMIN": "project_admin",
            "PROJECT_MANAGER": "project_manager",
            "TEAM_LEADER": "team_leader",
            "TEAM_MEMBER": "team_member",
        }

        permissions = data["permissions"]

        for api_field, model_field in permission_map.items():
            if api_field in permissions:
                setattr(user, model_field, bool(permissions[api_field]))

    user.save()


def update_user_service(user_id, data):
    user = _ensure_user_exists(user_id)
    if user is None:
        return None

    _validate_not_inactive(user)
    _validate_username(data)
    _validate_email(data, user_id)
    _validate_permissions(data, user)

    _apply_updates(user, data)

    return user
