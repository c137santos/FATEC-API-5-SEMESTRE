
from django.urls import path

from . import views

urlpatterns = [
    path("issues/add", views.add_issue),
    path("issues/list", views.list_issues),
]
