from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Card
from .serializers import CardSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def cards_dashboard(request):
    if request.method == "GET":
        qs = Card.objects.order_by("-id")
        return Response(CardSerializer(qs, many=True).data)

    serializer = CardSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    card = serializer.save(created_by=request.user)
    return Response(CardSerializer(card).data, status=status.HTTP_201_CREATED)
