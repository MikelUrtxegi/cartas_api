from django.db import models

from django.db import models
from django.utils.crypto import get_random_string

from company_session.models import Session, Group


def generate_participant_code() -> str:
    # ID corto para identificar al participante sin cuenta (opcional, útil para debugging)
    return get_random_string(10).upper()


class Participant(models.Model):
    """
    Participante de una sesión (no es un usuario del sistema).
    Entra con join_code -> se crea un Participant -> recibe token limitado.
    """

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="participants",
    )

    # Opcional: nombre mostrado en la mesa ("Mesa 3", "Ana", etc.)
    nickname = models.CharField(max_length=80, blank=True, default="")

    # Opcional: identificador corto (no secreto), útil para logs y depuración
    code = models.CharField(max_length=12, unique=True, default=generate_participant_code, editable=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["session", "group"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"Participant({self.id}) session={self.session_id} group={self.group_id} nickname='{self.nickname}'"
