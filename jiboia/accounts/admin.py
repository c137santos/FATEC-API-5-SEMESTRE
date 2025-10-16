from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Perfil"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
