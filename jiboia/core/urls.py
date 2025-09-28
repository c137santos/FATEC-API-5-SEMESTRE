
from django.urls import path

from . import views

urlpatterns = [
    path("issues/add", views.add_issue),
    path("issues/list", views.list_issues),
    path("projects/overview", views.list_projects_general),
]
