from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Company(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="companies_created",
    )
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name
