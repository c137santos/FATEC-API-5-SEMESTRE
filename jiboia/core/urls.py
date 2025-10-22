from django.urls import path

from . import views

urlpatterns = [
    path("issues/add", views.add_issue, name="add_issue"),
    path("issues", views.list_paginable_issues, name="list_paginable_issues"),
    path("projects/<int:project_id>", views.project_overview, name="project_overview"),
    path("projects/overview", views.list_projects_general, name="list_projects_general"),
    path("projects/<int:project_id>/desenvolvedores", views.project_developers, name="project_developers"),
    path("btncron-all", views.trigger_jira_sync, name='trigger_jira_sync'),
]
