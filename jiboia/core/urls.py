
from django.urls import path

from . import views

urlpatterns = [
    path("issues/add", views.add_issue),
    path("issues/list", views.list_issues),
    path("projects/<int:project_id>", views.project_overview, name='project_overview'),
    path("projects/overview", views.list_projects_general),
]
