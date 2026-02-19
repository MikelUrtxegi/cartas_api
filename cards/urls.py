from django.urls import path
from .views import cards_dashboard

urlpatterns = [
    path("cards/", cards_dashboard, name="dashboard_cards"),
]
