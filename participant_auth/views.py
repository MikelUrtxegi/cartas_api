from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.utils import timezone

from rest_framework_simplejwt.tokens import AccessToken

from company_session.models import Group
from .models import Participant
from .serializers import ParticipantJoinSerializer
from datetime import timedelta


@api_view(["POST"])
def participant_join(request):
    serializer = ParticipantJoinSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    join_code = serializer.validated_data["join_code"]
    nickname = serializer.validated_data.get("nickname", "")

    try:
        group = Group.objects.select_related("session").get(join_code=join_code)
    except Group.DoesNotExist:
        return Response(
            {"detail": "Invalid join_code"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Crear participante
    participant = Participant.objects.create(
        session=group.session,
        group=group,
        nickname=nickname,
    )

    # Crear JWT limitado
    token = AccessToken()
    token["type"] = "participant"
    token["participant_id"] = participant.id
    token["session_id"] = group.session_id
    token["group_id"] = group.id
    token.set_exp(lifetime=timedelta(hours=8))  # Token válido por 8 horas  
    
    return Response(
        {
            "access": str(token),
            "session": group.session_id,
            "group": group.id,
            "participant": participant.id,
        },
        status=status.HTTP_200_OK,
    )
