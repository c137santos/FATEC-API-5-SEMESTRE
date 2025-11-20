from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login),
    path("logout", views.logout),
    path("whoami", views.whoami),
    path("users/", views.users_view),
    path("users/<int:user_id>", views.delete_user_view, name="delete_user"),
]
