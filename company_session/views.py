from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Session, Group, Canvas
from .serializers import (
    SessionCreateSerializer,
    GroupCreateSerializer,
    JoinGroupSerializer,
    VoteCreateSerializer,
    CanvasUpsertSerializer,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_session(request):
    serializer = SessionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    session = serializer.save(created_by=request.user)
    return Response(SessionCreateSerializer(session).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_group(request):
    serializer = GroupCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    group = serializer.save()
    return Response(GroupCreateSerializer(group).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def create_vote(request):
    serializer = VoteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    vote = serializer.save()
    return Response(VoteCreateSerializer(vote).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
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
