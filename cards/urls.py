from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_card, name="dashboard_cards_create"),  # POST /api/dashboard/cards/
]