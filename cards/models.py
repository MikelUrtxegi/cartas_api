from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Card(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cards_created",
    )

    canonical_id = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["canonical_id", "version"],
                name="uniq_card_canonical_version",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title} (v{self.version})"
