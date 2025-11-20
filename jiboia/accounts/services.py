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
