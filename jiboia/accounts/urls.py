from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login),
    path("logout", views.logout),
    path("whoami", views.whoami),
    path("users/", views.get_all_users, name="users_list"),
    path("users/create", views.create_user, name="users_create"),
]
