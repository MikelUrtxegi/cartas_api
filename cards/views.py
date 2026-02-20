from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Card
from .serializers import CardSerializer, CardCreateSerializer


def _is_admin(user) -> bool:
    return bool(user and user.is_authenticated and user.is_staff)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def create_card(request):
    if not _is_admin(request.user):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        qs = Card.objects.all().order_by("-id")[:200]
        return Response(CardSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    serializer = CardCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    card = serializer.save(created_by=request.user)
    return Response(CardSerializer(card).data, status=status.HTTP_201_CREATED)