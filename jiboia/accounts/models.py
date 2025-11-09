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
    project_admin = models.BooleanField(default=False)
    project_manager = models.BooleanField(default=False)
    team_leader = models.BooleanField(default=False)
    team_member = models.BooleanField(default=False)

    def __str__(self):
        return str(self.username)

    def to_dict_json(self):
        return {
            "id": self.id,
            "name": self.get_full_name(),
            "username": getattr(self, "username", None),
            "first_name": getattr(self, "first_name", None),
            "last_name": getattr(self, "last_name", None),
            "email": self.email,
            "password": self.password,
            "valor_hora": 0.0 if getattr(self, "valor_hora", None) is None else float(self.valor_hora),
            "jira_id": getattr(self, "jira_id", None),
            "permissions": {
                "ADMIN": getattr(self, "is_superuser", False),
                "STAFF": getattr(self, "is_staff", False),
                "PROJECT_ADMIN": getattr(self, "project_admin", False),
                "PROJECT_MANAGER": getattr(self, "project_manager", False),
                "TEAM_LEADER": getattr(self, "team_leader", False),
                "TEAM_MEMBER": getattr(self, "team_member", False),
            },
        }