
from django.urls import path

from . import views

urlpatterns = [
    path("issues/add", views.add_issue),
    path("issues/list", views.list_issues),
    path("api/projects/overview", views.list_projects_general),
    path("api/projects/<int:project_id>/overview", views.list_projects_especific)
]
