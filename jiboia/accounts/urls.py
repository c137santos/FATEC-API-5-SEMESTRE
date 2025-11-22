from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login),
    path("logout", views.logout),
    path("whoami", views.whoami),
    path("users/create", views.create_user, name="users_create"),
    path("users/<int:user_id>", views.delete_user_view, name="delete_user"),
    path("users/", views.get_all_users, name="users_list"),
    path("users/edit/<int:user_id>", views.update_user_view, name="update_user"),
]
