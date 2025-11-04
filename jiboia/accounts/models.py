from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models  # noqa: F401


class User(AbstractUser):
    valor_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor por Hora",
        help_text="Valor cobrado por hora de trabalho",
    )
    jira_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=150, null=False, blank=True)
    project_manager = models.BooleanField(default=False)
    team_leader = models.BooleanField(default=False)
    team_member = models.BooleanField(default=False)

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
            "valor_hora": 0.0 if self.valor_hora is None else float(self.valor_hora),
            "jira_id": self.jira_id,
            "permissions": {
                "ADMIN": self.is_superuser,
                "STAFF": self.is_staff,
            },
        }

    def to_dict_json_user(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "permissions": {
                "PROJECT_MANAGER": self.project_manager,
                "TEAM_LEADER": self.team_leader,
                "TEAM_MEMBER": self.team_member,
            },
        }
