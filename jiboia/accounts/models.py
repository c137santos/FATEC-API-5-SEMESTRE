from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models


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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Usuário")
    valor_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valor por Hora",
        help_text="Valor cobrado por hora de trabalho",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        db_table = "user_profile"
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"

    def __str__(self):
        return f"Perfil de {self.user.username} - R$ {self.valor_hora}/hora"

    def to_dict_json(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "username": self.user.username,
            "valor_hora": str(self.valor_hora),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
