from .models import User


def list_users():
    users = User.objects.all()
    return [user.to_dict_json() for user in users]
