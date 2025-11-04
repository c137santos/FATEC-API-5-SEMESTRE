from jiboia.accounts.models import User


def list_users():
    users = User.objects.all()
    return [user.to_dict_json() for user in users]


def create_user(name, password, email, permissions):
    if not name or not password or not email:
        raise ValueError("Name, password, and email are required to create a user.")

    if not any(permissions.values()):
        raise ValueError("At least one permission must be granted to the user.")

    if email and User.objects.filter(email=email).exists():
        raise ValueError("A user with this email already exists.")

    user = User(
        name=name,
        email=email,
        project_manager=permissions.get("PROJECT_MANAGER", False),
        team_leader=permissions.get("TEAM_LEADER", False),
        team_member=permissions.get("TEAM_MEMBER", True),
    )
    user.set_password(password)
    user.save()
    return user.to_dict_json_user()
