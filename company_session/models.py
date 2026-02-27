import secrets
import string

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from cards.models import Card
from decks.models import Deck
from companies.models import Company


def generate_join_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Session(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        FINISHED = "finished", "Finished"

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="sessions",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sessions_created",
    )

    language = models.CharField(max_length=10, default="en")

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    deck = models.ForeignKey(
        Deck,
        on_delete=models.PROTECT,
        related_name="sessions",
        null=True,
        blank=True,
    )

    current_card = models.ForeignKey(
        Card,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sessions_current",
    )



    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Session {self.id} ({self.company})"


class Group(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=255)
    join_code = models.CharField(max_length=12, unique=True, default=generate_join_code)

    def __str__(self) -> str:
        return f"{self.name} ({self.join_code})"


class SessionCard(TimeStampedModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_cards")
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="session_cards")
    notes = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "card"], name="uniq_session_card"),
        ]

    def __str__(self) -> str:
        return f"Session {self.session_id} - {self.card}"


class Vote(TimeStampedModel):
    class VoteValue(models.IntegerChoices):
        NO = -1, "NO"
        ABSTAIN = 0, "NO_RESPONDE"
        YES = 1, "SI"

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="votes")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="votes")
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="votes")

    value = models.SmallIntegerField(choices=VoteValue.choices)
    comment = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "group", "card"], name="uniq_vote_session_group_card"),
        ]

    def __str__(self) -> str:
        return f"Vote s={self.session_id} g={self.group_id} c={self.card_id} v={self.value}"

class Canvas(TimeStampedModel):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name="canvas")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="canvases_updated",
    )
    data = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"Canvas session={self.session_id}"
