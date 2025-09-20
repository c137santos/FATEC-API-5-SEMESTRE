from django.contrib.auth.models import AbstractUser
from django.db import models  # noqa: F401


class User(AbstractUser):

    def __str__(self):
        return str(self.username)

    def to_dict_json(self):
        return {
            "id": self.id,
            "name": self.get_full_name(),
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "permissions": {
                "ADMIN": self.is_superuser,
                "STAFF": self.is_staff,
            },
        }
