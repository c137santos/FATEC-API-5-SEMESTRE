from django.contrib.auth.models import AbstractUser
from django.db import models  # noqa: F401


class User(AbstractUser):
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    jira_id = models.IntegerField(null=True, blank=True)

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
            "valor_hora": str(self.valor_hora) if self.valor_hora is not None else 0,
            "jira_id": self.jira_id if self.jira_id is not None else None,
            "permissions": {
                "ADMIN": self.is_superuser,
                "STAFF": self.is_staff,
            },
        }
