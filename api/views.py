from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.permissions import IsAdminUserStrict


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@permission_classes([IsAuthenticated, IsAdminUserStrict])

def ping(request):
    return Response({"ping": "pong"})
