from django.urls import path
from . import views

urlpatterns = [
    path("decks/", views.create_deck, name="create_deck"),
    path("decks/<int:deck_id>/cards/", views.deck_cards, name="deck_cards"),
]
