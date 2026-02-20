from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminUserToken, IsParticipantToken
from .models import Session, Group, Canvas, Vote
from decks.models import DeckCard



from .models import Session, Group, Canvas
from .serializers import (
    SessionCreateSerializer,
    GroupCreateSerializer,
    JoinGroupSerializer,
    VoteCreateSerializer,
    CanvasUpsertSerializer,
)


@api_view(["POST"])
@permission_classes([IsAdminUserToken])
def create_session(request):
    serializer = SessionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save(created_by=request.user)
    
    if session.deck_id:
        first_dc = (
            DeckCard.objects.filter(deck_id=session.deck_id)
            .select_related("card")
            .order_by("order", "id")
            .first()
        )
        if first_dc:
            session.current_card = first_dc.card
            session.save(update_fields=["current_card", "modified"])

    return Response(SessionCreateSerializer(session).data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAdminUserToken])
def create_group(request):
    serializer = GroupCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    group = serializer.save()
    return Response(GroupCreateSerializer(group).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsParticipantToken])
def join_group(request):
    serializer = JoinGroupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    join_code = serializer.validated_data["join_code"]

    try:
        group = Group.objects.get(join_code=join_code)
    except Group.DoesNotExist:
        return Response({"detail": "Invalid join_code"}, status=status.HTTP_404_NOT_FOUND)

    # De momento devolvemos datos del grupo (más adelante: crear membership)
    return Response(
        {"id": group.id, "name": group.name, "join_code": group.join_code, "session": group.session_id},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsParticipantToken])
def create_vote(request):
    """
    Participante vota usando session_id y group_id desde el token.
    Body: { "card": <id>, "value": -1|0|1, "comment": "" }
    """
    serializer = VoteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Token claims (lo que ya te devuelve participant_join)
    auth = getattr(request, "auth", None) or {}
    session_id = auth.get("session_id")
    group_id = auth.get("group_id")

    if not session_id or not group_id:
        return Response({"detail": "participant token required"}, status=status.HTTP_403_FORBIDDEN)

    card = serializer.validated_data["card"]
    value = serializer.validated_data["value"]
    comment = serializer.validated_data.get("comment", "")

    vote, _created = Vote.objects.update_or_create(
        session_id=session_id,
        group_id=group_id,
        card=card,
        defaults={"value": value, "comment": comment},
    )

    return Response(VoteCreateSerializer(vote).data, status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
@permission_classes([IsParticipantToken])
def canvas_view(request, session_id: int):
    if request.method == "GET":
        canvas = Canvas.objects.filter(session_id=session_id).first()
        return Response({"session": session_id, "data": canvas.data if canvas else {}}, status=status.HTTP_200_OK)

    # PUT (upsert)
    payload = {"session": session_id, "data": request.data.get("data", {})}
    serializer = CanvasUpsertSerializer(data=payload)
    serializer.is_valid(raise_exception=True)

    canvas, _created = Canvas.objects.update_or_create(
        session_id=session_id,
        defaults={"data": serializer.validated_data["data"], "updated_by": request.user},
    )
    return Response({"session": session_id, "data": canvas.data}, status=status.HTTP_200_OK)
