from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_deck, name="create_deck"),
    path("<int:deck_id>/cards/", views.deck_cards, name="deck_cards"),
]
