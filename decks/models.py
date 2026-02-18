from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from cards.models import Card


class Deck(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="decks_created",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_default = models.BooleanField(default=False)

    cards = models.ManyToManyField(Card, through="DeckCard", related_name="decks")

    def __str__(self) -> str:
        return self.name


class DeckCard(TimeStampedModel):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="deck_cards")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="deck_cards")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["deck", "card"], name="uniq_deck_card"),
        ]
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.deck} - {self.card} ({self.order})"
