
from django.urls import path

from . import views

urlpatterns = [
    path("cards/add", views.add_card),
    path("cards/list", views.list_cards),
]
